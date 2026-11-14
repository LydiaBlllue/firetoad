#!/usr/bin/env python3
"""ai.py — a model, by choice, exactly where the programs stop.

Off unless the owner turns it on (ROADMAP 2.0.0 step 3; the design in the product notes). It is
called at one place the core already marks as *for a person*: a merchant that merchants.json,
the rows, the brand and the starter map all miss. The model's answer is written as the
question's `suggest`, never as the answer — the owner still confirms, in the panel or in chat —
and it has to be one of the fifteen categories or it is dropped. What is sent is the merchant
string and the category names: no amount, no date, no account.

    python3 .claude/skills/update-dashboard/scripts/ai.py . status                  # what is set, and whether a key is stored
    python3 .claude/skills/update-dashboard/scripts/ai.py . set openai --model gpt-4o-mini [--base-url …] [--key -]
    python3 .claude/skills/update-dashboard/scripts/ai.py . off
    python3 .claude/skills/update-dashboard/scripts/ai.py . test "STARBUCKS 1234 TORONTO"

Where things live: the choice (provider, base URL, model) in .jade/settings.json in the
workspace, gitignored and never synced; the key in the macOS Keychain (service "Jade Toad": the
product's first name, kept when it became FIRE Toad so a key already saved is still found),
or the JADE_AI_KEY environment variable, or — elsewhere — .jade/ai.key with owner-only
permissions; every call in .jade/log/ai.jsonl with what was sent, so the owner can read it back;
an answer already given in .jade/ai_cache.json, so one merchant costs one call.

Providers: `openai` (any OpenAI-compatible endpoint — OpenAI, DeepSeek, Qwen, Gemini's OpenAI
endpoint, Groq, OpenRouter — base URL and model), `anthropic`, and `ollama` (a model on this
computer; the same OpenAI shape, no key). Paid tiers only in the list the panel shows, with the
reason: a free tier may train on what is sent.
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
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from categories import CATEGORIES  # noqa: E402

SERVICE = "Jade Toad"   # not renamed with the product (2026-11-12): saved keys live under it
PROVIDERS = {
    "openai": {"label": "With my own key — an OpenAI-compatible service",
               "note": "OpenAI, DeepSeek, Qwen, Gemini's OpenAI endpoint, Groq, OpenRouter… a paid tier: a free one may train on what you send",
               "baseUrl": "https://api.openai.com/v1", "model": "gpt-4o-mini", "key": True},
    "anthropic": {"label": "With my own key — Anthropic",
                  "note": "a paid API key, not a chat subscription",
                  "baseUrl": "https://api.anthropic.com", "model": "claude-haiku-5-5", "key": True},
    "ollama": {"label": "On this computer — Ollama",
               "note": "nothing leaves the machine; Ollama has to be running with the model pulled",
               "baseUrl": "http://127.0.0.1:11434/v1", "model": "qwen2.5:7b", "key": False},
}
TIMEOUT = 20


# ---------------------------------------------------------------- settings and the key
def _dir(root):
    d = os.path.join(root, ".jade")
    os.makedirs(d, exist_ok=True)
    return d


def settings(root):
    try:
        return json.load(open(os.path.join(root, ".jade", "settings.json"), encoding="utf-8")).get("ai") or {"provider": "none"}
    except (OSError, ValueError):
        return {"provider": "none"}


def save_settings(root, ai):
    p = os.path.join(_dir(root), "settings.json")
    try:
        all_ = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        all_ = {}
    all_["ai"] = ai
    tmp = p + ".tmp"
    json.dump(all_, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, p)


def key_get(root, provider):
    """The key, from the environment, the Keychain, or the owner-only file — never from findata/."""
    if os.environ.get("JADE_AI_KEY"):
        return os.environ["JADE_AI_KEY"]
    if sys.platform == "darwin":
        r = subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-a", provider, "-w"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    p = os.path.join(root, ".jade", f"ai-{provider}.key")
    try:
        return open(p, encoding="utf-8").read().strip() or None
    except OSError:
        return None


def key_set(root, provider, key):
    if sys.platform == "darwin":
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
    if sys.platform == "darwin":
        subprocess.run(["security", "delete-generic-password", "-s", SERVICE, "-a", provider], capture_output=True)
    try:
        os.remove(os.path.join(root, ".jade", f"ai-{provider}.key"))
    except OSError:
        pass


def key_stored(root, provider):
    return bool(key_get(root, provider)) if PROVIDERS.get(provider, {}).get("key") else True


def enabled(root):
    s = settings(root)
    p = s.get("provider")
    return p in PROVIDERS and key_stored(root, p)


def status(root):
    s = settings(root)
    p = s.get("provider") or "none"
    return {"provider": p, "baseUrl": s.get("baseUrl") or PROVIDERS.get(p, {}).get("baseUrl"),
            "model": s.get("model") or PROVIDERS.get(p, {}).get("model"),
            "keyStored": key_stored(root, p) if p in PROVIDERS else False,
            "enabled": enabled(root), "providers": PROVIDERS}


# ---------------------------------------------------------------- the call
def _post(url, headers, body):
    """One HTTPS POST, JSON in and out. Kept apart so the tests can stand in for it."""
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def chat(root, system, user, max_tokens=40):
    """The model's reply to one short exchange, or raise. The provider's shape is the only
    thing that differs; the text is what comes back."""
    s = settings(root)
    p = s.get("provider")
    if p not in PROVIDERS:
        raise RuntimeError("no model is set (ai.py set …)")
    base = (s.get("baseUrl") or PROVIDERS[p]["baseUrl"]).rstrip("/")
    model = s.get("model") or PROVIDERS[p]["model"]
    key = key_get(root, p) if PROVIDERS[p]["key"] else None
    if PROVIDERS[p]["key"] and not key:
        raise RuntimeError(f"no key stored for {p}")
    if p == "anthropic":
        out = _post(base + "/v1/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"},
                    {"model": model, "max_tokens": max_tokens, "system": system, "messages": [{"role": "user", "content": user}]})
        return "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text").strip()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    out = _post(base + "/chat/completions", headers,
                {"model": model, "max_tokens": max_tokens, "temperature": 0,
                 "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
    return ((out.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()


def _log(root, rec):
    d = os.path.join(_dir(root), "log")
    os.makedirs(d, exist_ok=True)
    rec = {"at": datetime.datetime.now().isoformat(timespec="seconds"), **rec}
    with open(os.path.join(d, "ai.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _cache(root):
    try:
        return json.load(open(os.path.join(root, ".jade", "ai_cache.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def pick_category(text):
    """The one category a reply names, or None: exact first, then the first category word the
    reply contains. Anything else is not an answer."""
    t = (text or "").strip().strip(".\"'").lower()
    for c in CATEGORIES:
        if t == c.lower():
            return c
    for c in CATEGORIES:
        if re.search(r"\b" + re.escape(c.lower()) + r"\b", t):
            return c
    return None


SYSTEM = ("You file a merchant string from a bank statement into exactly one spending category. "
          "Answer with the category name only, nothing else. The categories: " + ", ".join(CATEGORIES) + ".")


def categorise(root, merchant):
    """(category or None, how): the model's one-word filing of a merchant string, validated
    against the fifteen and cached. `how` says what happened: cached, model, invalid, error, off."""
    if not enabled(root):
        return None, "off"
    cache = _cache(root)
    if merchant in cache:
        return cache[merchant], "cached"
    t0 = time.monotonic()
    sent = {"merchant": merchant, "categories": list(CATEGORIES)}
    try:
        reply = chat(root, SYSTEM, f"Merchant: {merchant}")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, RuntimeError) as e:
        _log(root, {"fn": "categorise", "sent": sent, "error": f"{type(e).__name__}: {e}", "took": round(time.monotonic() - t0, 2)})
        return None, "error"
    cat = pick_category(reply)
    _log(root, {"fn": "categorise", "sent": sent, "got": reply, "category": cat, "took": round(time.monotonic() - t0, 2)})
    if cat:
        cache[merchant] = cat
        json.dump(cache, open(os.path.join(_dir(root), "ai_cache.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        return cat, "model"
    return None, "invalid"


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    sp = sub.add_parser("set"); sp.add_argument("provider", choices=sorted(PROVIDERS)); sp.add_argument("--model"); sp.add_argument("--base-url")
    sp.add_argument("--key", help="the key, or - to read it from stdin")
    sub.add_parser("off")
    tp = sub.add_parser("test"); tp.add_argument("merchant", nargs="?", default="STARBUCKS 1234 TORONTO ON")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if a.cmd == "set":
        s = {"provider": a.provider, "baseUrl": a.base_url or PROVIDERS[a.provider]["baseUrl"],
             "model": a.model or PROVIDERS[a.provider]["model"], "since": datetime.date.today().isoformat()}
        save_settings(root, s)
        if a.key:
            key = sys.stdin.readline().strip() if a.key == "-" else a.key
            print(f"  key stored in the {key_set(root, a.provider, key)}")
        a.cmd = "status"
    if a.cmd == "off":
        save_settings(root, {"provider": "none"})
        print("  a model is no longer used; the key, if any, is still stored"); return 0
    if a.cmd == "test":
        cat, how = categorise(root, a.merchant)
        print(f"  {a.merchant!r} → {cat} ({how})"); return 0 if cat else 1
    st = status(root)
    print(f"=== model — {st['provider']}" + (f" · {st['model']} at {st['baseUrl']} · key {'stored' if st['keyStored'] else 'MISSING'}" if st["provider"] != "none" else " (off)") + " ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
