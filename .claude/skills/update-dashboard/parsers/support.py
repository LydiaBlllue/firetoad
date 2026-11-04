"""support.py — which banks' files the tool reads, in one place.

docs/banks.md and docs/zh/banks.md are written from this table by `tools/banks.py`, and
check_design's S9 fails when either differs from what it would write: a bank marked confirmed
here is confirmed there, and nowhere else says otherwise (2026-11-04, user 001).

`status`:
  confirmed    read here from a real file of that bank, and it reconciled
  expected     a standard format the bank offers; not yet seen from this bank
  unconfirmed  a layout taken from others' descriptions; not yet seen from this bank
  no           offered by the bank but not read, and why

A CSV map's `verified` flag in csv_bank.PROFILES has to agree with its row here (S9 checks it).
"""
import re

FORMATS = {
    "pdf": ("PDF statement", "PDF 对账单"),
    "ofx": ("OFX / QFX download", "OFX / QFX 下载"),
    "csv": ("CSV download", "CSV 下载"),
    "holdings": ("Holdings export (CSV)", "持仓导出（CSV）"),
    "activities": ("Activities export (CSV)", "交易记录导出（CSV）"),
}

STATUS = {
    "confirmed": ("✓ Confirmed on a real file", "✓ 已用真实文件确认"),
    "expected": ("Expected to work (a standard format), not yet seen", "应该可用（标准格式），还没见过真实文件"),
    "unconfirmed": ("Layout from others' descriptions, not yet seen", "格式来自他人描述，还没见过真实文件"),
    "no": ("✗ Not read", "✗ 不读取"),
}

# bank, accounts, format, status, csv profile (when a CSV map exists), how to get it, a note — each in en / zh
SUPPORT = [
    {"bank": "RBC", "accounts": ("Chequing, savings, Visa", "支票、储蓄、Visa"), "format": "pdf", "status": "confirmed",
     "how": ("Online Banking → Statements, one PDF per account a month", "网银 → Statements，每个账户每月一份 PDF"),
     "note": ("Reconciled to the totals each statement prints. The best choice for chequing: it names who sent an e-Transfer.",
              "按每份对账单印的合计核对。支票账户最好用这个：它写着 e-Transfer 是谁转的。")},
    {"bank": "RBC", "accounts": ("Chequing, savings, Visa", "支票、储蓄、Visa"), "format": "ofx", "status": "confirmed",
     "how": ("Account Services → Download Transactions → Money, a date range, all accounts in one file",
             "Account Services → Download Transactions → Money，选日期范围，所有账户一个文件"),
     "note": ("Checks itself against the bank's balance. It does not name who sent an e-Transfer, so each one is asked.",
              "按银行给的余额自己核对。不写 e-Transfer 是谁转的，所以每笔都要问。")},
    {"bank": "RBC", "accounts": ("Chequing, savings, Visa", "支票、储蓄、Visa"), "format": "csv", "status": "confirmed", "profile": "rbc",
     "how": ("Download Transactions → Comma Delimited", "Download Transactions → Comma Delimited"),
     "note": ("No balance in the file: the balance your app shows is asked each month. Prefer OFX.",
              "文件里没有余额：每月要报一次 app 上的余额。优先用 OFX。")},
    {"bank": "BMO", "accounts": ("Chequing, savings, Mastercard", "支票、储蓄、Mastercard"), "format": "pdf", "status": "confirmed",
     "how": ("Online Banking → Statements", "网银 → Statements"),
     "note": ("From October 2026 chequing and savings come as one statement.", "2026 年 10 月起支票和储蓄合成一份对账单。")},
    {"bank": "BMO", "accounts": ("Chequing, savings, US-dollar accounts", "支票、储蓄、美元账户"), "format": "ofx", "status": "confirmed",
     "how": ("Account → Transactions → Download → .ofx format, between two dates (two months at most)",
             "账户 → Transactions → Download → .ofx 格式，选两个日期之间（最多两个月）"),
     "note": ("Checks itself against the bank's balance. The first time, setup asks which account each id in the file is.",
              "按银行给的余额自己核对。第一次 setup 会问文件里每个编号对应哪个账户。")},
    {"bank": "BMO", "accounts": ("Mastercard", "Mastercard"), "format": "ofx", "status": "expected",
     "how": ("A separate download, from the card's own page → Download → .ofx format",
             "单独下载：信用卡自己的页面 → Download → .ofx 格式"), "note": ("", "")},
    {"bank": "BMO", "accounts": ("Chequing, savings, US-dollar accounts", "支票、储蓄、美元账户"), "format": "csv", "status": "confirmed",
     "profile": "bmo",
     "how": ("Account → Transactions → Download → .csv format, one account at a time", "账户 → Transactions → Download → .csv 格式，一次只下一个账户"),
     "note": ("The file has a section for every account and nothing saying which is which, so a file with rows for "
              "more than one is refused. No balance in it: the balance your app shows is asked. Prefer OFX.",
              "文件里每个账户占一段，却没写哪段是哪个账户，所以有几个账户的文件会被拒。文件里也没有余额，"
              "要报一次 app 上的余额。优先用 OFX。")},
    {"bank": "BMO", "accounts": ("Mastercard", "Mastercard"), "format": "csv", "status": "confirmed", "profile": "bmo_card",
     "how": ("A separate download, from the card's own page → Download → .csv format",
             "单独下载：信用卡自己的页面 → Download → .csv 格式"),
     "note": ("No balance in it: the balance your app shows is asked.", "文件里没有余额，要报一次 app 上的余额。")},
    {"bank": "TD", "accounts": ("Chequing, savings, Visa", "支票、储蓄、Visa"), "format": "ofx", "status": "expected",
     "how": ("EasyWeb → Download transactions → Quicken or Money", "EasyWeb → Download transactions → Quicken 或 Money"), "note": ("", "")},
    {"bank": "TD", "accounts": ("Chequing, savings, Visa", "支票、储蓄、Visa"), "format": "csv", "status": "unconfirmed", "profile": "td",
     "how": ("EasyWeb → Download transactions → Spreadsheet (accountactivity.csv)", "EasyWeb → Download transactions → Spreadsheet（accountactivity.csv）"),
     "note": ("Chequing has a balance column; check against it.", "支票文件有余额列，可以按它核对。")},
    {"bank": "Scotiabank", "accounts": ("Chequing, savings, credit cards", "支票、储蓄、信用卡"), "format": "ofx", "status": "expected",
     "how": ("Online banking → the account → Download → Quicken (QFX)", "网银 → 账户 → Download → Quicken（QFX）"), "note": ("", "")},
    {"bank": "Scotiabank", "accounts": ("Chequing, savings, credit cards", "支票、储蓄、信用卡"), "format": "csv", "status": "unconfirmed", "profile": "scotia",
     "how": ("Online banking → the account → Download → CSV", "网银 → 账户 → Download → CSV"),
     "note": ("A download stops at 100 rows: get one statement period at a time.", "一次最多下载 100 行：按账单期分次下载。")},
    {"bank": "CIBC", "accounts": ("Chequing, savings, credit cards", "支票、储蓄、信用卡"), "format": "ofx", "status": "expected",
     "how": ("Online banking → Download Transactions → Quicken or Money", "网银 → Download Transactions → Quicken 或 Money"), "note": ("", "")},
    {"bank": "CIBC", "accounts": ("Chequing, savings, credit cards", "支票、储蓄、信用卡"), "format": "csv", "status": "unconfirmed", "profile": "cibc",
     "how": ("Online banking → Download Transactions → spreadsheet", "网银 → Download Transactions → spreadsheet"), "note": ("", "")},
    {"bank": "Tangerine", "accounts": ("Chequing, savings, credit card", "支票、储蓄、信用卡"), "format": "ofx", "status": "expected",
     "how": ("Website (not the app) → the account → Download → QFX or Money", "网页版（不是 app）→ 账户 → Download → QFX 或 Money"), "note": ("", "")},
    {"bank": "Tangerine", "accounts": ("Chequing, savings, credit card", "支票、储蓄、信用卡"), "format": "csv", "status": "unconfirmed", "profile": "tangerine",
     "how": ("Website → the account → Download → CSV", "网页版 → 账户 → Download → CSV"), "note": ("", "")},
    {"bank": "Simplii", "accounts": ("Chequing, savings", "支票、储蓄"), "format": "csv", "status": "unconfirmed", "profile": "simplii",
     "how": ("Online banking → Download → CSV", "网银 → Download → CSV"),
     "note": ("Its QFX download has been reported not to open in other programs.", "有人反映它的 QFX 在别的软件里打不开。")},
    {"bank": "EQ Bank", "accounts": ("Savings", "储蓄"), "format": "csv", "status": "unconfirmed",
     "how": ("The account's transactions → the download arrow", "账户交易页 → 下载箭头"),
     "note": ("Nothing describes its columns: setup reads the first lines with you and maps them.",
              "查不到它的列格式：setup 会和你一起看前几行，再起草对应表。")},
    {"bank": "Any other bank", "accounts": ("—", "—"), "format": "ofx", "status": "expected",
     "how": ("The Money or Quicken choice in online banking", "网银下载里的 Money 或 Quicken"),
     "note": ("OFX is one standard; a file that does not check itself against its balance is refused, never guessed.",
              "OFX 是统一标准；对不上自己余额的文件会被拒，不会去猜。")},
    {"bank": "Wealthsimple", "accounts": ("TFSA, RRSP, FHSA, non-registered, crypto", "TFSA、RRSP、FHSA、非注册、加密"), "format": "holdings", "status": "confirmed",
     "how": ("In the app: the holdings report, as CSV", "在 App 里导出持仓报告（CSV）"),
     "note": ("What each account holds today, at today's prices.", "每个账户现在持有什么、按今天的价格值多少。")},
    {"bank": "Wealthsimple", "accounts": ("TFSA, RRSP, FHSA, non-registered, crypto", "TFSA、RRSP、FHSA、非注册、加密"), "format": "activities", "status": "confirmed",
     "how": ("In the app: the activities export, as CSV, a date range", "在 App 里导出交易记录（CSV），选日期范围"),
     "note": ("Deposits, buys, sells and dividends; the exchange rate is taken from it too.",
              "存入、买入、卖出和分红；汇率也从这里取。")},
]

# Every bank and broker the page names, in its order, with the one way to start. A broker with no
# row in SUPPORT has no reader yet; the page still names it, so a user can see that it was looked at.
INSTITUTIONS = [
    ("RBC", "bank", ("**OFX**: one download carries every account. If you receive many e-Transfers, use the PDF statement "
                     "for chequing instead: it names who sent each one, so nothing has to be asked.",
                     "**OFX**：一次下载包含所有账户。如果你常收 e-Transfer，支票账户改用 PDF 对账单："
                     "它写着每笔是谁转的，就不用一笔笔回答。")),
    ("BMO", "bank", ("**OFX** for chequing, savings and US-dollar accounts, in one download. The Mastercard is a separate "
                     "download from the card's own page: the **CSV** (it asks the balance your app shows) or the **PDF "
                     "statement** (it asks nothing).",
                     "支票、储蓄、美元账户用 **OFX**，一次下完。Mastercard 要在信用卡自己的页面单独下载："
                     "用 **CSV**（要报一次 app 上的余额）或 **PDF 对账单**（什么都不用报）。")),
    ("TD", "bank", ("**OFX** first; the CSV if the OFX will not read.", "先用 **OFX**；读不了再用 CSV。")),
    ("Scotiabank", "bank", ("**OFX** first; the CSV if the OFX will not read.", "先用 **OFX**；读不了再用 CSV。")),
    ("CIBC", "bank", ("**OFX** first; the CSV if the OFX will not read.", "先用 **OFX**；读不了再用 CSV。")),
    ("Tangerine", "bank", ("**OFX**, from the website rather than the app; the CSV if it will not read.",
                           "用网页版下载 **OFX**（app 里没有）；读不了再用 CSV。")),
    ("Simplii", "bank", ("**CSV**.", "**CSV**。")),
    ("EQ Bank", "bank", ("**CSV**; the first time, setup reads its columns with you.", "**CSV**；第一次 setup 会和你一起认它的列。")),
    ("Any other bank", "bank", ("**OFX**, if online banking offers a Money or Quicken download. If not, the **PDF statement**: "
                                "Claude reads it by hand.",
                                "网银里有 Money 或 Quicken 下载，就用 **OFX**。没有的话用 **PDF 对账单**，由 Claude 手读。")),
    ("Wealthsimple", "broker", ("**Both CSV exports** each month: holdings and activities. A cash account has no export: its "
                                "balance is read from the app.",
                                "每月导出**两个 CSV**：持仓和交易记录。现金账户没有导出文件，余额从 App 里看。")),
]
OTHER_BROKERS = ["Questrade", "Interactive Brokers", "RBC Direct Investing", "TD Direct Investing", "BMO InvestorLine",
                 "CIBC Investor's Edge", "Scotia iTRADE", "National Bank Direct Brokerage", "Qtrade", "Any other broker"]
BALANCE_ONLY = ("No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. "
                "It counts in net worth; the Investing pages do not show what it holds.",
                "还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。"
                "它算进净资产，但投资页面看不到它持有什么。")
INSTITUTIONS += [(b, "broker", BALANCE_ONLY) for b in OTHER_BROKERS]

TITLE = ("Supported banks and brokers", "支持的银行和券商")
INTRO = (
    "Which files Jade Toad reads, institution by institution. Every file has to reconcile before it is "
    "let in: a statement to the totals it prints, an OFX download to the bank's own balance, a CSV to "
    "its balances or to the balance your app shows.",
    "Jade Toad 能读哪些银行、券商的哪些文件。每个文件都要先核对通过才收进来：对账单要对上它印的合计，"
    "OFX 要对上银行给的余额，CSV 要对上文件里的余额或 app 上的余额。")
GUIDE_HEAD = ("Which to use", "用哪种")
GUIDE = (
    ["**OFX / QFX** — the first choice. One download carries every account at the bank, for the dates you pick, "
     "and it checks itself against the bank's balance.",
     "**PDF statement** — the most complete: it names who sent an e-Transfer and prints totals to check against. "
     "But it is one file per account a month.",
     "**CSV** — the last choice. Most carry no balance, so the balance your app shows is asked each month.",
     "**Balance only** — when none of these can be read: the total from the app, once a month. It counts in net "
     "worth, with no transactions behind it.",
     "Whatever you download, pick a **date range**, never \"since last download\": the bank moves that mark every "
     "time you download."],
    ["**OFX / QFX**：首选。一次下载包含这家银行所有账户，日期自己选，还会自己对上银行的余额。",
     "**PDF 对账单**：信息最全，写着 e-Transfer 是谁转的，印着合计可以核对。但每个账户每月一份。",
     "**CSV**：最后选。多数文件没有余额，每月要报一次 app 上的余额。",
     "**只记余额**：以上都读不了的时候，每月报一次 app 上的总数。算进净资产，但没有交易明细。",
     "不管下载哪种，都选**日期范围**，不要选「上次下载以来」：每下载一次，银行都会改这个标记。"])
NOTE = ("This page is written from the tool's own table (`parsers/support.py`); a status changes only "
        "when a real file has been read.",
        "这一页由工具自己的表（`parsers/support.py`）生成；只有读过真实文件，状态才会改。")


MARK = {"confirmed": "✓", "expected": "○", "unconfirmed": "○", "no": "✗"}
LEGEND = ("✓ read here from a real file and reconciled · ○ should work, not yet confirmed on a real "
          "file · ✗ not read · — no reader here (a PDF statement can still be read by Claude, by hand)",
          "✓ 已用真实文件读过并核对通过 · ○ 应该可用，还没用真实文件确认 · ✗ 不读取 · "
          "— 没有现成的读取方式（PDF 对账单仍可由 Claude 手读）")
NAME_ZH = {"Any other bank": "其他银行", "Any other broker": "其他券商"}
TABLES = {
    "bank": (("pdf", "ofx", "csv"), (("Bank", "PDF statement", "OFX / QFX", "CSV"), ("银行", "PDF 对账单", "OFX / QFX", "CSV")),
             ("Banks", "银行"), ("Banks: how to download each", "银行：每种怎么下载")),
    "broker": (("holdings", "activities"), (("Broker", "Holdings export", "Activities export"), ("券商", "持仓导出", "交易记录导出")),
               ("Brokers", "券商"), ("Brokers: how to export", "券商：怎么导出")),
}
RECOMMEND = ("Recommended", "推荐")


def slug(text):
    """The anchor GitHub gives a heading: lower case, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def render(lang):
    """How to choose, then a grid per kind of institution (a mark per kind of file, each name a link to
    its own section), then each institution's recommendation and its files' how and why."""
    i = 0 if lang == "en" else 1
    colon, op, cl = ("：", "（", "）") if i else (": ", " (", ")")
    name = lambda b: NAME_ZH.get(b, b) if i else b

    def cell(rows):
        if not rows:
            return "—"
        if len({r["status"] for r in rows}) == 1:
            return MARK[rows[0]["status"]]
        # one bank, one kind of file, a different answer per account (BMO's card has not been seen)
        return " · ".join(f"{MARK[r['status']]} {r['accounts'][i]}" for r in rows)

    lines = [f"# {TITLE[i]}", "", INTRO[i], "", f"## {GUIDE_HEAD[i]}", ""]
    lines += [f"{n}. {g}" for n, g in enumerate(GUIDE[i], 1)]
    for kind, (cols, head, title, _) in TABLES.items():
        lines += ["", f"## {title[i]}", "", "| " + " | ".join(head[i]) + " |", "|---|" + ":---:|" * len(cols)]
        for b, k, _rec in INSTITUTIONS:
            if k != kind:
                continue
            rows = [r for r in SUPPORT if r["bank"] == b]
            lines.append(f"| [{name(b)}](#{slug(name(b))}) | "
                         + " | ".join(cell([r for r in rows if r["format"] == c]) for c in cols) + " |")
    lines += ["", LEGEND[i], ""]
    for kind, (_, _, _, details) in TABLES.items():
        lines += [f"## {details[i]}", ""]
        for b, k, rec in INSTITUTIONS:
            if k != kind:
                continue
            lines += [f"### {name(b)}", "", f"**{RECOMMEND[i]}**{colon}{rec[i]}", ""]
            rows = [x for x in SUPPORT if x["bank"] == b]
            for r in rows:
                what = " — ".join(t for t in (r["how"][i], r["note"][i]) if t)
                lines.append(f"- {MARK[r['status']]} {FORMATS[r['format']][i]} · {r['accounts'][i]}" + (f"{colon}{what}" if what else ""))
            if rows:
                lines.append("")
    lines += [f"*{NOTE[i]}*", ""]
    return "\n".join(lines)
