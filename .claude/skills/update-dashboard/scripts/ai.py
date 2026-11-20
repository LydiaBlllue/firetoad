#!/usr/bin/env python3
"""ai.py — AI assist: a model, by choice, exactly where the programs stop.

Off unless the owner turns it on (DESIGN.md Settings, "AI assist"). It is asked at one place the
core already marks as *for a person*: a merchant that merchants.json, the rows, the brand and the
starter map all miss. The model's answer is written as the question's `suggest`, never as the
answer — the owner still confirms, in the panel or in chat — and it has to be one of the fifteen
categories or it is dropped. What is sent is the merchant strings and the category names: no
amount, no date, no account.

    python3 .claude/skills/update-dashboard/scripts/ai.py . status
    python3 .claude/skills/update-dashboard/scripts/ai.py . set claude|chatgpt|deepseek [--key -]
    python3 .claude/skills/update-dashboard/scripts/ai.py . set ollama [--model qwen2.5:7b]
    python3 .claude/skills/update-dashboard/scripts/ai.py . set openai --base-url URL --model NAME [--key -]   # any other OpenAI-compatible service, from the chat only
    python3 .claude/skills/update-dashboard/scripts/ai.py . off                     # and the key is deleted
    python3 .claude/skills/update-dashboard/scripts/ai.py . test "STARBUCKS 1234 TORONTO"

The owner picks a service by name and pastes a key; the tool chooses the address and the model,
so they move with the tool's versions. Ollama is listed only when it is running on this
computer, and a model of its that runs on Ollama's own servers (a name with "-cloud") is never
listed: an address on this computer is not the same as nothing leaving it.

How often: only during an import, never while a page is read. A cloud service is asked once per
import, every new merchant in one request; Ollama one merchant at a time, on this computer. At
most MAX_PER_IMPORT merchants an import — a technical ceiling against a runaway bill, not a
number the owner manages. A merchant answered once is cached and never sent again. A failure is
never retried: the questions are asked as if it were off.

Where things live: the choice in .firetoad/settings.json in the workspace, gitignored and never
synced; the key in the macOS Keychain (service "Jade Toad": the product's first name, kept when it
became FIRE Toad so a key already saved is still found), or the FIRETOAD_AI_KEY environment
variable, or — elsewhere — .firetoad/ai-<service>.key with owner-only permissions; every request in
.firetoad/log/ai.jsonl with what was sent, which the Settings page shows; an answer already given
in .firetoad/ai_cache.json.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from categories import CATEGORIES  # noqa: E402
import layout  # noqa: E402  where the app's own files live in a workspace

SERVICE = "Jade Toad"   # not renamed with the product (2026-11-12): saved keys live under it
# The services the owner chooses from, by name. `kind` is the shape of the request; `cloud` says
# the merchants leave this computer, so they are asked in one request; `company` is who receives
# them, as the Settings page says it.
PROVIDERS = {
    # `menu` is what the Service menu calls it when the name people know is not the company the
    # key comes from: a Claude or ChatGPT plan is not that company's API key
    "claude":   {"label": "Claude", "menu": "Claude (Anthropic)", "company": "Anthropic", "kind": "anthropic", "cloud": True, "key": True,
                 "baseUrl": "https://api.anthropic.com", "model": "claude-haiku-5-5", "keyUrl": "https://console.anthropic.com/settings/keys"},
    "chatgpt":  {"label": "ChatGPT", "menu": "ChatGPT (OpenAI)", "company": "OpenAI", "kind": "openai", "cloud": True, "key": True,
                 "baseUrl": "https://api.openai.com/v1", "model": "gpt-5.4-mini", "keyUrl": "https://platform.openai.com/api-keys"},
    "deepseek": {"label": "DeepSeek", "company": "DeepSeek", "kind": "openai", "cloud": True, "key": True,
                 "baseUrl": "https://api.deepseek.com", "model": "deepseek-flash", "keyUrl": "https://platform.deepseek.com/api_keys"},
    "ollama":   {"label": "Ollama on this computer", "company": "", "kind": "openai", "cloud": False, "key": False,
                 "baseUrl": "http://127.0.0.1:11434/v1", "model": "", "keyUrl": ""},
    # any other OpenAI-compatible service, with its address and model: set from the chat only
    "openai":   {"label": "Another service", "company": "that service", "kind": "openai", "cloud": True, "key": True,
                 "baseUrl": "", "model": "", "keyUrl": "", "hidden": True},
}
SHOWN = [k for k, v in PROVIDERS.items() if not v.get("hidden")]
OLD_NAMES = {"anthropic": "claude"}          # what settings.json said before 1.1.0
OLLAMA = "http://127.0.0.1:11434"
TIMEOUT = 60
MAX_PER_IMPORT = 50
# Room for the answer. Models that think before they answer spend part of it thinking, and with
# 40 they came back empty (measured 2026-11-20); a batch gets more for each merchant. It is a
# ceiling, not a cost — only what the model writes is billed — so it is generous: an answer cut
# off at the ceiling is the failure to avoid (it used to yield no suggestion and no word of why).
ANSWER_TOKENS = 2000


def budget(n=1):
    return ANSWER_TOKENS + 60 * max(0, n - 1)


class Failed(RuntimeError):
    """A request that did not get an answer, with the reason the owner can act on: `key` (the
    service refused it), `credit` (the account has none), `busy` (rate limit, overload, a server
    error), `network` (no connection, a timeout), or `error`. The text is for the log and never
    carries the service's own message, which can quote part of the key."""

    def __init__(self, why, detail=""):
        super().__init__(detail or why)
        self.why = why


def _error_kind(text):
    """The service's own name for an error, from its JSON body: a type or a code, never the message."""
    try:
        err = json.loads(text).get("error")
    except (ValueError, AttributeError):
        return ""
    if isinstance(err, dict):
        return str(err.get("type") or err.get("code") or "")[:60]
    return ""


def http_why(code, text):
    """Which of Failed's reasons an HTTP error is. Services say "no credit" under several codes:
    402, or a 400 / 403 / 429 whose body speaks of credit, balance, billing or quota."""
    low = (text or "").lower()
    if code == 402 or any(w in low for w in ("credit balance", "insufficient_quota", "insufficient balance", "billing", "exceeded your current quota")):
        return "credit"
    if code in (401, 403):
        return "key"
    if code == 429 or code >= 500:
        return "busy"
    return "error"


# ---------------------------------------------------------------- settings and the key
def _dir(root):
    d = layout.state_dir(root)
    os.makedirs(d, exist_ok=True)
    return d


def _write_json(p, obj):
    """Whole or not at all: written beside, closed, then moved over the old one."""
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def _all_settings(root):
    try:
        with open(os.path.join(layout.state_dir(root), "settings.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def settings(root):
    s = dict(_all_settings(root).get("ai") or {"provider": "none"})
    s["provider"] = OLD_NAMES.get(s.get("provider"), s.get("provider") or "none")
    return s


def save_settings(root, ai):
    p = os.path.join(_dir(root), "settings.json")
    all_ = _all_settings(root)
    all_["ai"] = ai
    _write_json(p, all_)


def _keychain():
    """Whether the macOS Keychain is used. Not when the key comes from the environment, and not
    when FIRETOAD_AI_NO_KEYCHAIN is set (the selftest and the unit tests): the Keychain is the
    whole computer's, not this folder's, so a test turning AI assist off must never delete the
    owner's real key."""
    return sys.platform == "darwin" and not any(os.environ.get(n) for n in ("FIRETOAD_AI_KEY", "JADE_AI_KEY", "FIRETOAD_AI_NO_KEYCHAIN"))


def _accounts(provider):
    """The Keychain accounts a service's key may be under: its own name, and its name before 1.1.0."""
    return [provider] + [old for old, new in OLD_NAMES.items() if new == provider]


def key_get(root, provider):
    """The key, from the environment, the Keychain, or the owner-only file — never from findata/."""
    for name in ("FIRETOAD_AI_KEY", "JADE_AI_KEY"):      # the second is the name until 1.0.5
        if os.environ.get(name):
            return os.environ[name]
    for acct in _accounts(provider):
        if _keychain():
            r = subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-a", acct, "-w"],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        try:
            with open(os.path.join(layout.state_dir(root), f"ai-{acct}.key"), encoding="utf-8") as fh:
                k = fh.read().strip()
            if k:
                return k
        except OSError:
            pass
    return None


def key_set(root, provider, key):
    if _keychain():
        r = subprocess.run(["security", "add-generic-password", "-U", "-s", SERVICE, "-a", provider, "-w", key],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return "keychain"
    p = os.path.join(_dir(root), f"ai-{provider}.key")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(key)
    os.chmod(p, 0o600)
    return "file"


def key_delete(root, provider):
    for acct in _accounts(provider):
        if _keychain():
            subprocess.run(["security", "delete-generic-password", "-s", SERVICE, "-a", acct], capture_output=True)
        try:
            os.remove(os.path.join(layout.state_dir(root), f"ai-{acct}.key"))
        except OSError:
            pass


def key_stored(root, provider):
    return bool(key_get(root, provider)) if PROVIDERS.get(provider, {}).get("key") else True


def enabled(root):
    s = settings(root)
    p = s.get("provider")
    if p not in PROVIDERS:
        return False
    if p == "ollama":
        return bool(s.get("model"))
    if p == "openai" and not (s.get("baseUrl") and s.get("model")):
        return False
    return key_stored(root, p)


def address_ok(url):
    """https to anywhere, or plain http to this computer and nowhere else. The host is read out
    of the address: a prefix test let http://localhost.example.com through, and a key would
    have gone to it unencrypted."""
    try:
        u = urllib.parse.urlsplit(url or "")
        host = (u.hostname or "").lower()
    except ValueError:
        return False
    return bool(host) and (u.scheme == "https" or (u.scheme == "http" and host in ("127.0.0.1", "localhost", "::1")))


def turn_on(root, provider, key=None, model=None, base_url=None):
    """Choose a service. A key, when given, is stored; a key for another service is deleted, so
    only the service in use ever holds one. The address and model are the tool's, except for
    Ollama's model (one installed here) and the chat-only `openai`."""
    provider = OLD_NAMES.get(provider, provider)
    if provider not in PROVIDERS:
        raise ValueError(f"unknown service {provider!r}")
    now = settings(root)
    s = {"provider": provider, "since": (now.get("since") if now.get("provider") == provider else None) or datetime.date.today().isoformat()}
    if provider == "ollama":
        names = ollama_models()
        model = model or (names[0] if names else None)
        if not model:
            raise ValueError("Ollama is not running on this computer, or has no model installed")
        if model not in names or is_cloud_model(model):
            raise ValueError(f"{model!r} is not a model installed in Ollama on this computer")
        s["model"] = model
    if provider == "openai":
        if not (base_url and model):
            raise ValueError("another service needs its address and model (--base-url, --model)")
        if not address_ok(base_url):
            raise ValueError("the address has to be https, or this computer")
        s["baseUrl"], s["model"] = base_url.rstrip("/"), model
    keep = {k: v for k, v in now.items() if k in ("declined",)}
    save_settings(root, {**keep, **s})
    for other in PROVIDERS:
        if other != provider and PROVIDERS[other]["key"]:
            key_delete(root, other)
    if key:
        return key_set(root, provider, key.strip())
    return None


def turn_off(root):
    """Off, and the key with it: nothing is sent again, and nothing is left to send with."""
    for p in PROVIDERS:
        if PROVIDERS[p]["key"]:
            key_delete(root, p)
    keep = {k: v for k, v in settings(root).items() if k in ("declined",)}
    save_settings(root, {**keep, "provider": "none", "off": datetime.date.today().isoformat()})


def decline(root):
    """The panel's "Not now": the first-time question is not asked again."""
    s = settings(root)
    s["declined"] = datetime.date.today().isoformat()
    save_settings(root, s)


# ---------------------------------------------------------------- Ollama on this computer
def is_cloud_model(name):
    """A model Ollama runs on its own servers (name like "gpt-oss:120b-cloud"): the request goes to
    this computer's address and on to ollama.com, so it is not "on this computer"."""
    return bool(re.search(r"[-:]cloud\b", name or ""))


def ollama_models(timeout=0.8):
    """The models installed in Ollama on this computer, without its cloud ones; [] when it is not running."""
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=timeout) as r:
            tags = json.loads(r.read().decode("utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for m in tags.get("models") or []:
        name = m.get("name") or m.get("model") or ""
        if name and not is_cloud_model(name) and not m.get("remote_host"):
            out.append(name)
    return sorted(out)


# ---------------------------------------------------------------- the call
def _post(url, headers, body):
    """One HTTPS POST, JSON in and out. Kept apart so the tests can stand in for it."""
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _target(root):
    s = settings(root)
    p = s.get("provider")
    if p not in PROVIDERS:
        raise RuntimeError("AI assist is off")
    spec = PROVIDERS[p]
    base = ((s.get("baseUrl") or "") if p == "openai" else spec["baseUrl"]).rstrip("/")
    model = s.get("model") if p in ("ollama", "openai") else spec["model"]
    return p, spec, base, model


def openai_body(model, system, user, max_tokens):
    """The request in OpenAI's shape. The gpt-5 family thinks before it answers: it takes
    max_completion_tokens and no temperature; the others take max_tokens and temperature 0."""
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if re.match(r"(gpt-5|o\d)", model or ""):
        body.update({"max_completion_tokens": max_tokens, "reasoning_effort": "low"})
    else:
        body.update({"max_tokens": max_tokens, "temperature": 0})
    return body


def _ask(url, headers, body):
    """_post, with a failure turned into Failed and its reason."""
    try:
        return _post(url, headers, body)
    except urllib.error.HTTPError as e:
        try:
            text = e.read().decode("utf-8", "replace")[:2000]
        except Exception:  # noqa: BLE001  a body that cannot be read says nothing
            text = ""
        raise Failed(http_why(e.code, text), f"HTTP {e.code} {_error_kind(text)}".strip()) from None
    except (urllib.error.URLError, OSError) as e:
        raise Failed("network", type(e).__name__) from None


def exchange(root, system, user, max_tokens=ANSWER_TOKENS):
    """(reply, cut): the model's reply to one exchange, and whether it stopped at the ceiling
    with more to say. Raises Failed. Only the request's shape differs by service."""
    p, spec, base, model = _target(root)
    key = key_get(root, p) if spec["key"] else None
    if spec["key"] and not key:
        raise Failed("key", f"no key stored for {p}")
    if spec["kind"] == "anthropic":
        out = _ask(base + "/v1/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"},
                   {"model": model, "max_tokens": max_tokens, "system": system, "messages": [{"role": "user", "content": user}]})
        text = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text").strip()
        return text, out.get("stop_reason") == "max_tokens"
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    out = _ask(base + "/chat/completions", headers, openai_body(model, system, user, max_tokens))
    choice = (out.get("choices") or [{}])[0]
    return ((choice.get("message") or {}).get("content") or "").strip(), choice.get("finish_reason") == "length"


def chat(root, system, user, max_tokens=ANSWER_TOKENS):
    """The model's reply to one exchange, or raise."""
    return exchange(root, system, user, max_tokens)[0]


def _log(root, rec):
    d = os.path.join(_dir(root), "log")
    os.makedirs(d, exist_ok=True)
    rec = {"at": datetime.datetime.now().isoformat(timespec="seconds"), **rec}
    with open(os.path.join(d, "ai.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _cache(root):
    try:
        with open(os.path.join(layout.state_dir(root), "ai_cache.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _cache_save(root, cache):
    _write_json(os.path.join(_dir(root), "ai_cache.json"), cache)


def pick_category(text):
    """The one category a reply names, or None: the name alone, or a sentence that names exactly
    one. Anything else is not an answer."""
    t = (text or "").strip().strip(".\"'").lower()
    for c in CATEGORIES:
        if t == c.lower():
            return c
    # a sentence that names one category is that category; one that names two ("not Dining, it
    # is Grocery") is not an answer — which was meant cannot be read off the order of a list
    named = [c for c in CATEGORIES if re.search(r"\b" + re.escape(c.lower()) + r"\b", t)]
    return named[0] if len(named) == 1 else None


SYSTEM = ("You file a merchant string from a bank statement into exactly one spending category. "
          "Answer with the category name only, nothing else. The categories: " + ", ".join(CATEGORIES) + ".")
SYSTEM_MANY = ("You file merchant strings from a bank statement into spending categories. For each numbered "
               "merchant, choose exactly one category from: " + ", ".join(CATEGORIES) + ". "
               'Answer with JSON only, the number to the category: {"1": "Dining", "2": "Grocery"}.')


def many_prompt(merchants):
    return "\n".join(f"{i}. {m}" for i, m in enumerate(merchants, 1))


def parse_many(reply, n):
    """{index (1-based): category} from a batch reply: a JSON object, perhaps inside a code fence
    or after some thinking; else the pairs of one that was cut off; else lines like "3. Dining".
    An answer that is not one of the fifteen is dropped."""
    out, text = {}, reply or ""
    for m in re.finditer(r"\{[^{}]*\}", text):
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            continue
        got = {}
        for k, v in obj.items():
            if str(k).strip().isdigit() and 1 <= int(k) <= n:
                c = pick_category(str(v))
                if c:
                    got[int(k)] = c
        if got:
            out = got
    if not out:
        # no whole object: a reply cut off before its closing brace still has every pair it got to
        for m in re.finditer(r'"(\d+)"\s*:\s*"([^"\n]*)"', text):
            c = pick_category(m.group(2))
            if 1 <= int(m.group(1)) <= n and c:
                out[int(m.group(1))] = c
    if not out:
        for m in re.finditer(r"(?m)^\s*(\d+)\s*[.:)\-]\s*(.+?)\s*$", text):
            i = int(m.group(1))
            c = pick_category(m.group(2).split("→")[-1].split(":")[-1])
            if 1 <= i <= n and c:
                out[i] = c
    return out


ERRORS = (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, RuntimeError)   # Failed is a RuntimeError


# What a failure is called for the owner: what happened, then the one thing they can do about it.
# The panel says the same in the owner's language (strings.py, ai_fail_*).
WHY = {
    "key": "{svc} did not accept the key. Put in a new one in Settings, under AI assist.",
    "credit": "The {svc} account has no credit left. Add credit on its website.",
    "busy": "{svc} is busy right now. Try again in a few minutes.",
    "network": "{svc} could not be reached. Check the internet connection.",
    "not running": "{svc} is not open on this computer. Open it first.",
    "error": "{svc} did not answer.",
    "cut": "{svc}'s answer reached its length limit before it got to every merchant. Ask again to send only the rest.",
}


def why_text(why, label):
    return WHY.get(why, WHY["error"]).format(svc=label or "The service")


def why_of(e):
    """The reason to tell the owner (Failed's), or `error` for anything else that went wrong."""
    return getattr(e, "why", None) or "error"


def categorise(root, merchant):
    """(category or None, how): one merchant, validated against the fifteen and cached. `how`:
    cached, model, invalid, error, off. The chat's `test` uses this."""
    if not enabled(root):
        return None, "off"
    cache = _cache(root)
    if merchant in cache:
        return cache[merchant], "cached"
    p = settings(root)["provider"]
    t0 = time.monotonic()
    sent = {"merchants": [merchant], "categories": list(CATEGORIES)}
    try:
        reply = chat(root, SYSTEM, f"Merchant: {merchant}")
    except ERRORS as e:
        _log(root, {"fn": "categorise", "service": p, "sent": sent, "error": f"{type(e).__name__}: {e}", "why": why_of(e),
                    "took": round(time.monotonic() - t0, 2)})
        return None, "error"
    cat = pick_category(reply)
    _log(root, {"fn": "categorise", "service": p, "sent": sent, "got": reply, "found": {merchant: cat} if cat else {},
                "took": round(time.monotonic() - t0, 2)})
    if cat:
        cache[merchant] = cat
        _cache_save(root, cache)
        return cat, "model"
    return None, "invalid"


def suggest_many(root, merchants):
    """({merchant: category}, info) for one import's new merchants. A cloud service is asked once,
    all of them in one request; Ollama one at a time. Cached answers are not sent again; past
    MAX_PER_IMPORT the rest are not asked. Never raises: a failure is said in `info` and the
    questions go on without a suggestion."""
    info = {"service": settings(root).get("provider"), "label": "", "requests": 0, "sent": 0, "suggested": 0, "left": 0, "error": None,
            "cut": False, "answered": []}        # answered: the merchants a request came back for, whatever it said
    if not enabled(root):
        info["error"] = "off"
        return {}, info
    p, spec, _base, _model = _target(root)
    info["label"] = spec["label"]
    cache = _cache(root)
    out = {m: cache[m] for m in merchants if m in cache}
    todo = [m for m in dict.fromkeys(merchants) if m not in cache]
    info["left"] = max(0, len(todo) - MAX_PER_IMPORT)
    todo = todo[:MAX_PER_IMPORT]
    if not todo:
        info["suggested"] = len(out)
        return out, info
    if not spec["cloud"] and not ollama_models():
        info["error"] = "not running"
        return out, info
    groups = [todo] if spec["cloud"] else [[m] for m in todo]
    for group in groups:
        t0 = time.monotonic()
        sent = {"merchants": group, "categories": list(CATEGORIES)}
        info["requests"] += 1
        info["sent"] += len(group)
        try:
            if len(group) == 1:
                reply, cut = exchange(root, SYSTEM, f"Merchant: {group[0]}")
                c = pick_category(reply)
                found = {group[0]: c} if c else {}
            else:
                reply, cut = exchange(root, SYSTEM_MANY, many_prompt(group), budget(len(group)))
                found = {group[i - 1]: c for i, c in parse_many(reply, len(group)).items()}
        except ERRORS as e:
            _log(root, {"fn": "suggest", "service": p, "sent": sent, "error": f"{type(e).__name__}: {e}", "why": why_of(e),
                        "took": round(time.monotonic() - t0, 2)})
            info["error"] = why_of(e)
            break                               # never retried: the rest are asked without a suggestion
        _log(root, {"fn": "suggest", "service": p, "sent": sent, "got": reply, "found": found, "took": round(time.monotonic() - t0, 2),
                    **({"cut": True} if cut else {})})
        info["cut"] = info["cut"] or cut
        # a reply cut short answered only the merchants it got to: the others can be asked again
        info["answered"] += [m for m in group if not cut or m in found]
        cache.update(found)
        out.update(found)
    _cache_save(root, cache)
    info["suggested"] = len(out)
    return out, info


def suggest_open(root, say=None):
    """The open merchant questions with no suggestion yet, asked once (the panel, after AI assist
    was turned on in the middle of categorizing). Each one a request came back for is marked, so
    it is not asked again whatever the answer; a request that failed marks nothing. Writes
    decisions.json only."""
    say = say or (lambda *a, **k: None)
    p = layout.path(root, "decisions.json")
    with open(p, encoding="utf-8") as fh:
        dec = json.load(fh)
    todo = [d for d in dec.get("decisions", []) if d.get("kind") == "merchant" and d.get("status") == "open"
            and not d.get("suggest") and not d.get("aiAsked") and d.get("match")]
    if not todo or not enabled(root):
        return {"asked": 0, "suggested": 0, "error": None if todo else "nothing to ask", "cut": False, "label": ""}
    found, info = suggest_many(root, [d["match"] for d in todo])
    n = 0
    answered = set(info["answered"]) | set(found)
    for d in todo[:MAX_PER_IMPORT]:
        # marked only when an answer came back: after a refused key or a lost connection the
        # same merchants are asked again once that is put right
        if d["match"] not in answered:
            continue
        d["aiAsked"] = datetime.date.today().isoformat()
        c = found.get(d["match"])
        if c and c != d.get("default"):
            d["suggest"], d["suggestBy"] = c, "model"
            n += 1
    _write_json(p, dec)
    say(f"  AI assist: {info['sent']} merchant(s) asked, {n} with a suggestion")
    if info["error"] or info["cut"]:
        say("  AI assist: " + why_text(info["error"] or "cut", info["label"]))
    return {"asked": info["sent"], "suggested": n, "error": info["error"], "cut": info["cut"], "label": info["label"]}


# ---------------------------------------------------------------- what the Settings page shows
def history(root):
    """Every request, newest first: the day, the service and who received it (`to`: the company,
    since that is whose terms apply; for Ollama and a service of the owner's own, its name), the
    merchants sent, whether it answered."""
    out = []
    try:
        with open(os.path.join(layout.state_dir(root), "log", "ai.jsonl"), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return out
    for ln in lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        sent = r.get("sent") or {}
        ms = sent.get("merchants") or ([sent["merchant"]] if sent.get("merchant") else [])
        svc = OLD_NAMES.get(r.get("service"), r.get("service") or "")
        spec = PROVIDERS.get(svc) or {}
        out.append({"at": (r.get("at") or "")[:10], "service": svc,
                    "to": (spec.get("label") if spec.get("hidden") or not spec.get("company") else spec["company"]) or svc,
                    "merchants": ms, "ok": not r.get("error"), "why": r.get("why") if r.get("error") else None, "cut": bool(r.get("cut"))})
    return out[::-1]


def kept(root):
    """(suggested, kept): the merchants AI assist suggested a category for, and how many of those
    the owner's answer agreed with — from decisions.json, where each answer already is."""
    try:
        with open(layout.path(root, "decisions.json"), encoding="utf-8") as fh:
            dec = json.load(fh).get("decisions", [])
    except (OSError, ValueError):
        return 0, 0
    sug = [d for d in dec if d.get("suggestBy") == "model" and d.get("suggest")]
    ok = [d for d in sug if d.get("status") == "confirmed" and str(d.get("answer") or "").split("|")[0] == d["suggest"]]
    return len(sug), len(ok)


def status(root):
    """What the Settings page and the panel need — never the key."""
    s = settings(root)
    p = s.get("provider") or "none"
    month = datetime.date.today().isoformat()[:7]
    hist = history(root)
    suggested, kept_n = kept(root)
    return {"provider": p, "enabled": enabled(root), "keyStored": key_stored(root, p) if p in PROVIDERS else False,
            "model": s.get("model") if p in ("ollama", "openai") else PROVIDERS.get(p, {}).get("model"),
            "since": s.get("since"), "declined": s.get("declined"),
            "services": [{"id": k, "menu": PROVIDERS[k].get("menu") or PROVIDERS[k]["label"],
                          **{x: PROVIDERS[k][x] for x in ("label", "company", "cloud", "key", "keyUrl")}} for k in SHOWN],
            "ollama": ollama_models(),
            "askedThisMonth": sum(1 for h in hist if h["at"][:7] == month),
            "suggested": suggested, "kept": kept_n, "history": hist[:24]}


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    sp = sub.add_parser("set"); sp.add_argument("provider", choices=sorted(set(PROVIDERS) | set(OLD_NAMES)))
    sp.add_argument("--model"); sp.add_argument("--base-url")
    sp.add_argument("--key", help="the key, or - to read it from stdin")
    sub.add_parser("off")
    tp = sub.add_parser("test"); tp.add_argument("merchant", nargs="?", default="STARBUCKS 1234 TORONTO ON")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if a.cmd == "set":
        key = (sys.stdin.readline().strip() if a.key == "-" else a.key) if a.key else None
        try:
            where = turn_on(root, a.provider, key=key, model=a.model, base_url=a.base_url)
        except ValueError as e:
            print(f"  ✗ {e}"); return 2
        if where:
            print(f"  key stored in the {where}")
        a.cmd = "status"
    if a.cmd == "off":
        turn_off(root)
        print("  AI assist is off; the key is deleted"); return 0
    if a.cmd == "test":
        cat, how = categorise(root, a.merchant)
        print(f"  {a.merchant!r} → {cat} ({how})"); return 0 if cat else 1
    st = status(root)
    if st["provider"] == "none":
        print("=== AI assist — off ===")
    else:
        print(f"=== AI assist — {PROVIDERS[st['provider']]['label']}, {st['model'] or 'no model'}, "
              f"{'on' if st['enabled'] else 'not on: ' + ('no key stored' if not st['keyStored'] else 'incomplete')} ===")
    print(f"  asked this month: {st['askedThisMonth']}; suggested {st['suggested']}, kept {st['kept']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
