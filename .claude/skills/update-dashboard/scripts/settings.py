"""settings.py — the numbers that are the owner's to choose, as one table (FINANCE.md §8e).

How many months an emergency fund should cover, what a month is planned to cost, what goes to
the broker: none of these is a fact a statement carries. They are declarations, and until
1.0.5 each one lived its own way — some asked once by the setup and editable only by hand, some
dragged on the page and kept in the browser, some written into the page code. This is the one
list of them. The Settings page, the setup's questions, the check on a stored value (D31) and
the verb that changes one (setting.py) all read TABLE, so a number becomes adjustable by adding
a row here and nowhere else.

The table points at where each value already lives — it moves no data:

    emergency   plan.json `emergency` {low, high}      months; absent means the default
    importDay   profile.json `importDay`
    planBase    plan.json `planBase`
    takeHome    funds.json plan.flows, the income flow paid today
    invest      funds.json plan.flows, the saving flow to the broker
    everyday    funds.json plan.flows, the everyday flow

and the day a value was last changed is beside it in plan.json `changed` {key: date}.

Pure: every function takes the three files as dicts (`files`: plan.json, funds.json,
profile.json by name) and reads or edits them; nothing here touches the disk.
"""
import flows

STAGES = ("start", "goal", "track", "after")

TABLE = [
    {"key": "emergency", "kind": "months", "stage": "start", "default": [3, 6], "min": 0, "max": 36,
     "en": "Emergency fund", "zh": "应急金",
     "whyEn": "How many months of your usual spending you want within reach.",
     "whyZh": "想留出够花几个月的、随时能用的钱。"},
    {"key": "importDay", "kind": "day", "stage": "start", "default": 1, "min": 1, "max": 28,
     "en": "Import day", "zh": "导入日",
     "whyEn": "The day of the month your statements are all out.",
     "whyZh": "每个月对账单都出齐的那一天。"},
    {"key": "planBase", "kind": "money", "stage": "goal", "default": None, "min": 0, "max": 1_000_000,
     "en": "Planning spend a month", "zh": "每月规划支出",
     "whyEn": "What a month costs, for the FIRE target.",
     "whyZh": "算 FIRE 目标时，一个月按多少花销算。"},
    {"key": "takeHome", "kind": "money", "stage": "track", "default": None, "min": 0, "max": 1_000_000,
     "en": "Take-home pay a month", "zh": "每月到手工资",
     "whyEn": "What reaches your account after tax.",
     "whyZh": "扣完税实际到账的钱。"},
    {"key": "invest", "kind": "money", "stage": "track", "default": None, "min": 0, "max": 1_000_000,
     "en": "To the broker a month", "zh": "每月投资",
     "whyEn": "What you invest every month.",
     "whyZh": "每个月转去投资的钱。"},
    {"key": "everyday", "kind": "money", "stage": "track", "default": None, "min": 0, "max": 1_000_000,
     "en": "Everyday a month", "zh": "每月日常开销",
     "whyEn": "The guilt-free amount, no categories.",
     "whyZh": "随便花、不分类别的额度。"},
]
BY_KEY = {r["key"]: r for r in TABLE}

# The flow each plan figure is: which rows of plan.flows carry it, and the row a first value makes.
_FLOW = {
    "takeHome": (lambda f: f.get("kind") == "income" and flows.active(f),
                 {"key": "pay", "kind": "income", "name": "Take-home pay"}),
    "invest": (lambda f: f.get("kind") == "saving" and flows.active(f) and (f.get("to") or "broker") == "broker",
               {"key": "invest", "kind": "saving", "name": "Invest", "to": "broker"}),
    "everyday": (lambda f: f.get("kind") == "everyday" and flows.active(f),
                 {"key": "everyday", "kind": "everyday", "name": "Everyday"}),
}


def _num(x):
    x = float(x)
    return int(x) if x == int(x) else round(x, 2)


def _plan(files):
    return files.get("plan.json") or {}


def _flow_rows(files, key):
    pred = _FLOW[key][0]
    return [f for f in ((files.get("funds.json") or {}).get("plan") or {}).get("flows") or [] if pred(f)]


def locked(key, files):
    """Why this number cannot be changed as one number, or None. A plan figure made of several
    flows (two paycheques, two transfers to the broker) is a sum: which line a new total would
    change is the owner's to say, line by line."""
    if key in _FLOW and len(_flow_rows(files, key)) > 1:
        return "several"
    return None


def stored(key, files):
    """The value the files carry, or None when the owner never gave one."""
    if key == "emergency":
        e = _plan(files).get("emergency")
        return [_num(e["low"]), _num(e["high"])] if isinstance(e, dict) and "low" in e and "high" in e else None
    if key == "importDay":
        return (files.get("profile.json") or {}).get("importDay")
    if key == "planBase":
        return _plan(files).get("planBase")
    rows = _flow_rows(files, key)
    if not rows or any(f.get("amount") is None for f in rows):
        return None
    return _num(sum(float(f["amount"]) for f in rows))


def value(key, files):
    """What every consumer reads: the stored value, else the table's default (which may be None:
    a plan figure has no default, it is Not set until the owner gives it)."""
    v = stored(key, files)
    return BY_KEY[key]["default"] if v is None else v


def check(key, raw):
    """(value, None) when `raw` is a legal value for this row, else (None, why). `raw` is what a
    form or a command line hands over: a number, a string, or for a range two of them."""
    row = BY_KEY.get(key)
    if row is None:
        return None, f"no setting called {key!r}"
    lo, hi = row["min"], row["max"]

    def one(x):
        if isinstance(x, bool) or x is None:
            raise ValueError
        if isinstance(x, str):
            x = x.strip().replace("$", "").replace(",", "")
        x = float(x)
        if x != x or x in (float("inf"), float("-inf")):
            raise ValueError
        return _num(x)

    try:
        if row["kind"] == "months":
            if isinstance(raw, str):
                raw = raw.replace("to", " ").replace("-", " ").replace(",", " ").split()
            a, b = (one(x) for x in raw)
            if not (lo <= a <= b <= hi) or b <= 0:
                return None, f"{row['en']}: a range inside {lo} to {hi} months, the lower number first"
            return [a, b], None
        v = one(raw)
    except (TypeError, ValueError):
        return None, f"{row['en']}: {raw!r} is not a number" if row["kind"] != "months" else f"{row['en']}: two numbers of months are needed"
    if row["kind"] == "day" and v != int(v):
        return None, f"{row['en']}: a whole day of the month"
    if not lo <= v <= hi:
        return None, f"{row['en']}: between {lo:,} and {hi:,}"
    return v, None


def write(key, v, files, today):
    """Put a checked value where it lives and date the change. Returns the names of the files
    edited. Raises ValueError for a number that is locked (see locked())."""
    why = locked(key, files)
    if why:
        raise ValueError(f"{BY_KEY[key]['en']} is the sum of several lines of the plan; change the line in funds.json")
    plan = files.setdefault("plan.json", {})
    touched = {"plan.json"}
    if key == "emergency":
        plan["emergency"] = {"low": v[0], "high": v[1]}
    elif key == "importDay":
        files.setdefault("profile.json", {})["importDay"] = int(v)
        touched.add("profile.json")
    elif key == "planBase":
        plan["planBase"] = v
    else:
        fl = files.setdefault("funds.json", {}).setdefault("plan", {}).setdefault("flows", [])
        rows = _flow_rows(files, key)
        if rows:
            rows[0]["amount"] = v
        else:
            fl.append(dict(_FLOW[key][1], amount=v))
        touched.add("funds.json")
    plan.setdefault("changed", {})[key] = today
    return sorted(touched)


def reset(key, files, today):
    """Back to the table's default. Only a row with a default can go back; returns the files edited."""
    row = BY_KEY[key]
    if row["default"] is None:
        raise ValueError(f"{row['en']} has no default to go back to")
    plan = files.setdefault("plan.json", {})
    if key == "emergency":
        plan.pop("emergency", None)
        (plan.get("changed") or {}).pop(key, None)
        if plan.get("changed") == {}:
            plan.pop("changed")
        return ["plan.json"]
    return write(key, row["default"], files, today)


def rows(files):
    """What the page is handed (the SETTINGS constant): every row of the table with its value now."""
    changed = _plan(files).get("changed") or {}
    out = []
    for r in TABLE:
        v, s = value(r["key"], files), stored(r["key"], files)
        out.append({"key": r["key"], "kind": r["kind"], "stage": r["stage"], "n": r["en"], "why": r["whyEn"],
                    "v": v, "def": r["default"], "min": r["min"], "max": r["max"],
                    "isDef": r["default"] is not None and (s is None or s == r["default"]),
                    "changed": changed.get(r["key"]), "locked": locked(r["key"], files)})
    return out


def emergency_state(months, band):
    """Where the months covered sit against the owner's range: below / inside / above, or None
    when the months cannot be known yet. The edges belong to the range."""
    if months is None or not band:
        return None
    return "below" if months < band[0] else "above" if months > band[1] else "inside"
