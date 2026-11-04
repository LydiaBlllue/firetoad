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

FORMATS = {
    "pdf": ("PDF statement", "PDF 对账单"),
    "ofx": ("OFX / QFX download", "OFX / QFX 下载"),
    "csv": ("CSV download", "CSV 下载"),
    "export": ("Broker export", "券商导出"),
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
     "how": ("The card's page → Download → .ofx format", "信用卡页面 → Download → .ofx 格式"), "note": ("", "")},
    {"bank": "BMO", "accounts": ("Chequing, savings", "支票、储蓄"), "format": "csv", "status": "no",
     "how": ("", ""),
     "note": ("Several accounts in one file with nothing saying which is which. Use OFX.",
              "一个文件里有几个账户，却没写哪段是哪个账户。请用 OFX。")},
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
    {"bank": "Wealthsimple", "accounts": ("TFSA, RRSP, FHSA, non-registered, crypto", "TFSA、RRSP、FHSA、非注册、加密"), "format": "export", "status": "confirmed",
     "how": ("The holdings report and the activities export", "持仓报告和活动导出"), "note": ("", "")},
    {"bank": "Any other bank", "accounts": ("—", "—"), "format": "ofx", "status": "expected",
     "how": ("The Money or Quicken choice in online banking", "网银下载里的 Money 或 Quicken"),
     "note": ("OFX is one standard; a file that does not check itself against its balance is refused, never guessed.",
              "OFX 是统一标准；对不上自己余额的文件会被拒，不会去猜。")},
]

TITLE = ("Banks and files", "支持的银行和文件")
INTRO = (
    "Which files Jade Toad reads, bank by bank. Every file has to reconcile before it is let in: a "
    "statement to the totals it prints, an OFX download to the bank's own balance, a CSV to its "
    "balances or to the balance your app shows. **Prefer OFX / QFX** where your bank offers it, and "
    "always download a **date range**, never \"since last download\": the bank moves that mark every "
    "time you download.",
    "Jade Toad 能读哪些银行的哪些文件。每个文件都要先核对通过才收进来：对账单要对上它印的合计，OFX 要对上"
    "银行给的余额，CSV 要对上文件里的余额或 app 上的余额。银行提供的话，**优先用 OFX / QFX**；下载时一律"
    "选**日期范围**，不要选「上次下载以来」，因为每下载一次银行都会改这个标记。")
NOTE = ("This page is written from the tool's own table (`parsers/support.py`); a status changes only "
        "when a real file has been read.",
        "这一页由工具自己的表（`parsers/support.py`）生成；只有读过真实文件，状态才会改。")


def render(lang):
    i = 0 if lang == "en" else 1
    head = ("| Bank | Accounts | File | Status | How to get it | Note |" if i == 0 else
            "| 银行 | 账户 | 文件 | 状态 | 怎么下载 | 说明 |")
    lines = [f"# {TITLE[i]}", "", INTRO[i], "", head, "|---|---|---|---|---|---|"]
    for r in SUPPORT:
        lines.append(f"| {r['bank']} | {r['accounts'][i]} | {FORMATS[r['format']][i]} | {STATUS[r['status']][i]} | "
                     f"{r['how'][i] or '—'} | {r['note'][i] or '—'} |")
    lines += ["", f"*{NOTE[i]}*", ""]
    return "\n".join(lines)
