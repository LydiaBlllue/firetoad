"""strings.py — every word the panel says, in one place, in English and Chinese.

The dashboard is English (DESIGN.md); the panel is instructions, and instructions are read in
the owner's language. So each string lives here once per language, the page picks one at
render time (`?lang=zh` on the panel, remembered in .jade/settings.json; before that, profile.json
`lang`; before that, English), and nothing in panel.py or the template carries a sentence of its
own. A string says what to DO, in plain words: never a file name where a bank's name will do,
never a tool's word (ledger, register, reconcile) where the owner's will do.

    t("zh", "s1")                      → "拿到这个月的文件"
    t("en", "missing", n=2, months="Oct, Nov")

A key missing in one language falls back to English, so a half-translated table still renders.
"""

LANGS = ("en", "zh")

S = {
    # — header
    "subtitle": {"en": "This month's import · {date}", "zh": "本月导入 · {date}"},
    "intro": {"en": "Once a month, four things: get the files, put them here, import, answer a few questions. The highlighted step is where you are.",
              "zh": "每个月做四件事：拿到文件 → 放进来 → 导入 → 回答几个问题。高亮的那一步就是你现在该做的。"},
    "open_dash": {"en": "Open the dashboard ↗", "zh": "打开仪表盘 ↗"},
    "lang_other": {"en": "中文", "zh": "English"},
    "import_day": {"en": "your import day is the {day}", "zh": "你的导入日是每月 {day} 号"},
    # — the steps
    "s1": {"en": "Get this month's files", "zh": "拿到这个月的文件"},
    "s2": {"en": "Put them here", "zh": "放进来"},
    "s3": {"en": "Import", "zh": "导入"},
    "s4": {"en": "Answer a few questions", "zh": "回答几个问题"},
    "s5": {"en": "Done", "zh": "完成"},
    "lead_todo": {"en": "{n} thing(s) still to get — the rows marked “still missing” below say what and how.",
                  "zh": "还有 {n} 样没拿到——下面标着「还缺」的行写了是什么、怎么拿。"},
    "lead_unnamed": {"en": "{n} file(s) in inbox could not be recognised. Nothing imports until they are named — see step 2.",
                     "zh": "inbox 里有 {n} 个文件认不出来。命名之前什么都不会导入——看第 2 步。"},
    "lead_inbox": {"en": "Files are in. Next: step 3, press “See what would happen”.",
                   "zh": "文件已经放进来了。下一步：第 3 步，点「先看看会发生什么」。"},
    "lead_questions": {"en": "The import is done. {n} question(s) wait for you in step 4.",
                       "zh": "导入完成了。第 4 步有 {n} 个问题等你回答。"},
    "lead_done": {"en": "Everything is up to date. Nothing to do until the next statements arrive.",
                  "zh": "都是最新的。等下一批对账单出来之前没有事要做。"},
    # — step 1 rows
    "st_todo": {"en": "still missing", "zh": "还缺"},
    "st_inbox": {"en": "in inbox ✓", "zh": "已放进来 ✓"},
    "st_ok": {"en": "up to date", "zh": "已是最新"},
    "st_optional": {"en": "only if it changed", "zh": "有变化才要"},
    "kind_statement": {"en": "bank statement (PDF)", "zh": "银行对账单（PDF）"},
    "kind_export": {"en": "export file (CSV)", "zh": "导出文件（CSV）"},
    "kind_shot": {"en": "phone screenshot", "zh": "手机截图"},
    "kind_typed": {"en": "a number you type", "zh": "手填一个数"},
    "missing": {"en": "{doc}: {n} missing ({months})", "zh": "{doc}：缺 {n} 份（{months}）"},
    "doc_ok": {"en": "{doc}: up to date", "zh": "{doc}：已是最新"},
    "doc_inbox": {"en": "{doc}: in inbox", "zh": "{doc}：已放进来"},
    "export_line": {"en": "{what} export · newest {asof}", "zh": "{what} 导出 · 最新到 {asof}"},
    "how": {"en": "How do I get it?", "zh": "怎么拿？"},
    "how_bank_generic": {"en": "Sign in to {bank} online banking → Statements → download last month's PDF. Keep the file name the bank gives it, then drop it in step 2.",
                         "zh": "登录 {bank} 网银 → 对账单（Statements）→ 下载上个月的 PDF。文件名别改，然后在第 2 步放进来。"},
    "how_tail": {"en": "Keep the file name as downloaded, then drop it in step 2.", "zh": "文件名保持下载时的样子，然后在第 2 步放进来。"},
    "how_shot": {"en": "Open {capture}. Take a screenshot, then press “Read a screenshot” below — or just type the amount and the date.",
                 "zh": "打开 {capture}，截图；然后点下面的「读截图」——或者直接填金额和日期。"},
    "how_typed": {"en": "Open the {inst} app, find {name}, and type the balance it shows today with the date.",
                  "zh": "打开 {inst} 的 App，找到 {name}，把今天显示的余额和日期填进来。"},
    "people_line": {"en": "{who} paid something back? Only then: drop the new ledger file (last one {last}).",
                    "zh": "{who} 还钱了吗？有才需要：放进新的流水文件（上一份到 {last}）。"},
    "all_ok": {"en": "Up to date: {list}", "zh": "已是最新：{list}"},
    "other_balances": {"en": "Other balances you type by hand ({n}) — only when one changed", "zh": "其他手填的余额（{n} 个）——有变化时再填"},
    "asof": {"en": "as of {date}", "zh": "截至 {date}"},
    "never": {"en": "never", "zh": "从未"},
    "amount_ph": {"en": "the amount the app shows", "zh": "App 上显示的金额"},
    "save": {"en": "Save", "zh": "保存"},
    "read_shot": {"en": "Read a screenshot", "zh": "读截图"},
    "cands_note": {"en": "the amounts on the image, likeliest first — check, then Save", "zh": "图上的金额，最像的排第一——核对后按保存"},
    "cands_none": {"en": "no amount found on the image; type it", "zh": "图上没认出金额，手填吧"},
    "near": {"en": "near", "zh": "旁边是"},
    "date_read": {"en": "date read", "zh": "读到日期"},
    # — step 2
    "drop": {"en": "Drop the files here", "zh": "把文件拖到这里"},
    "or_choose": {"en": "or choose files", "zh": "或选择文件"},
    "open_inbox": {"en": "open the inbox folder", "zh": "打开 inbox 文件夹"},
    "waiting": {"en": "{n} file(s) here, recognised as:", "zh": "已放进来 {n} 个文件，认出为："},
    "none_waiting": {"en": "Nothing here yet. A PDF statement, a CSV export or a screenshot can be dropped.",
                     "zh": "还没有文件。可以放 PDF 对账单、CSV 导出文件、手机截图。"},
    "unnamed": {"en": "not recognised — {why}", "zh": "认不出 — {why}"},
    "unnamed_fix": {"en": "Rename it to the name the bank gives, or ask in the chat.", "zh": "改回银行给的文件名，或者在对话里问。"},
    "saved": {"en": "saved", "zh": "已保存"},
    "already": {"en": "already here", "zh": "已经有了"},
    "refused": {"en": "refused", "zh": "没放进去"},
    # — step 3
    "dry": {"en": "See what would happen", "zh": "先看看会发生什么"},
    "go": {"en": "Import now", "zh": "确认导入"},
    "dry_hint": {"en": "A look first. Nothing is written until you press “Import now”.", "zh": "先只是看一眼，按「确认导入」之前什么都不会写入。"},
    "dry_running": {"en": "looking at what is in inbox…", "zh": "正在看 inbox 里有什么…"},
    "dry_none": {"en": "Nothing to import: no new file in inbox.", "zh": "没有可导入的：inbox 里没有新文件。"},
    "dry_stop": {"en": "The import stops on what is marked ✗ above. Nothing was written.", "zh": "导入在上面标 ✗ 的地方停下了，什么都没写。"},
    "dry_plan": {"en": "That is the plan. “Import now” writes it, rebuilds the page and files the originals.", "zh": "这就是将要做的。按「确认导入」会写入、重建页面、归档原件。"},
    "go_running": {"en": "importing…", "zh": "正在导入…"},
    "go_done": {"en": "done — the page is rebuilt", "zh": "完成——页面已重建"},
    "go_failed": {"en": "the import failed and nothing was written; the lines say why", "zh": "导入失败，什么都没写；上面的行说了原因"},
    "undo": {"en": "Undo the last import", "zh": "撤销上一次导入"},
    "undo_q": {"en": "Put everything back as it was before the last import?", "zh": "把一切恢复到上一次导入之前？"},
    "undo_running": {"en": "undoing…", "zh": "正在撤销…"},
    "undo_done": {"en": "undone — the page is rebuilt", "zh": "已撤销——页面已重建"},
    "undo_none": {"en": "nothing was undone; the lines say why", "zh": "没有撤销；上面的行说了原因"},
    "failed_lines": {"en": "that failed; the lines say where", "zh": "失败了；上面的行说了在哪"},
    "running_busy": {"en": "{verb} is running — the lines below follow it.", "zh": "正在进行：{verb}——下面的行是它的进度。"},
    "held": {"en": "{verb} is running elsewhere (since {since}); wait for it.", "zh": "别处正在进行：{verb}（从 {since} 起），等它结束。"},
    # — step 4
    "q_intro": {"en": "The programs could not decide these on their own. Tap an answer on each, then save once.",
                "zh": "这些是程序自己拿不准的。每一条点一个答案，最后保存一次。"},
    "q_none": {"en": "Nothing to answer. New questions appear here after an import.", "zh": "没有要回答的。导入之后，新问题会出现在这里。"},
    "filed_as": {"en": "for now:", "zh": "现在记为："},
    "suggested": {"en": "suggested:", "zh": "建议："},
    "seen_n": {"en": "seen {n}×", "zh": "出现 {n} 次"},
    "model_dot": {"en": "a model's suggestion", "zh": "模型的建议"},
    "in_ledger": {"en": "answered in its ledger, not here", "zh": "要在流水里改，这里改不了"},
    "save_answers": {"en": "Save answers", "zh": "保存答案"},
    "unanswered_keep": {"en": "a row left alone keeps what it is filed as", "zh": "没点的保持现状"},
    "saving": {"en": "saving answers…", "zh": "正在保存答案…"},
    "saved_rebuilt": {"en": "answers saved — the page is rebuilt", "zh": "答案已保存——页面已重建"},
    "not_saved": {"en": "not saved; the lines under step 3 say which answer was refused", "zh": "没保存；第 3 步下面的行说了哪条被拒绝"},
    # — step 5
    "last_import": {"en": "last import {date}", "zh": "上次导入 {date}"},
    "no_import": {"en": "No import yet.", "zh": "还没有导入过。"},
    # — the folder's tool copy
    "tool_newer": {"en": "This folder's data is a newer shape (schema {ws}) than this app builds (schema {app}). Nothing is written until the app is updated.",
                   "zh": "这个文件夹的数据格式（schema {ws}）比这个应用（schema {app}）新。更新应用之前不会写入。"},
    "tool_migrate": {"en": "This folder's data is an older shape (schema {ws}) than this app builds (schema {app}): it has to be migrated first (tools/migrate.py), then refreshed.",
                     "zh": "这个文件夹的数据格式（schema {ws}）比应用（schema {app}）旧，要先迁移（tools/migrate.py），再刷新。"},
    "tool_differs": {"en": "This folder's copy of the tool differs from the app's in {n} place(s) — both doors should run one version.",
                     "zh": "这个文件夹里的工具副本和应用里的有 {n} 处不同——两边应该跑同一个版本。"},
    "refresh_copy": {"en": "Refresh the copy", "zh": "刷新副本"},
    "refresh_running": {"en": "refreshing this folder's copy of the tool…", "zh": "正在刷新工具副本…"},
    "refresh_done": {"en": "refreshed — both doors run one version now", "zh": "已刷新——两边现在是同一个版本"},
    "refresh_failed": {"en": "the refresh did not finish; the lines say why", "zh": "刷新没完成；上面的行说了原因"},
    # — the model card
    "ai_title": {"en": "A model, by choice", "zh": "可选：用一个模型帮忙"},
    "ai_intro": {"en": "Only for a merchant none of the maps know. Sent: the merchant string and the fifteen category names, nothing else. The answer is a suggestion you confirm, never the filing.",
                 "zh": "只用于谁都不认识的商户。发出去的只有商户名和 15 个类别名，别的什么都没有。回答只是建议，你确认了才算。"},
    "ai_off": {"en": "Off", "zh": "关"},
    "ai_on": {"en": "on", "zh": "开"},
    "ai_nokey": {"en": "set, but no key stored", "zh": "已设置，但还没有 key"},
    "ai_key_ph": {"en": "API key", "zh": "API key"},
    "ai_key_kept": {"en": "a key is stored — leave blank to keep it", "zh": "已存有 key——留空就不改"},
    "ai_try": {"en": "Try it on a merchant", "zh": "拿一个商户试试"},
    "ai_try_q": {"en": "A merchant string, as a statement prints it:", "zh": "一个商户名，照对账单上印的样子："},
    "ai_asking": {"en": "asking…", "zh": "正在问…"},
    "ai_noanswer": {"en": "no usable answer ({how}) — .jade/log/ai.jsonl has the exchange", "zh": "没有可用的回答（{how}）——.jade/log/ai.jsonl 里有往来记录"},
    "settings": {"en": "Settings", "zh": "设置"},
}

MONTHS = {"en": ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
          "zh": tuple(f"{i} 月" for i in range(1, 13))}


def t(lang, key, **kw):
    """The string for `key` in `lang` (English when the language has none), formatted. A
    placeholder may not be called `lang` or `key` (the panel crashed on `{key}` once a broker
    export was missing, 2026-11-07, found by the first full simulation)."""
    row = S.get(key) or {}
    text = row.get(lang) or row.get("en") or key
    try:
        return text.format(**kw) if kw else text
    except (KeyError, IndexError):
        return text


def month(lang, m):
    """'2026-11' → 'Nov' / '11 月'; anything else as it is."""
    m = str(m or "")
    if len(m) == 7 and m[4] == "-" and m[5:].isdigit():
        return MONTHS.get(lang, MONTHS["en"])[int(m[5:]) - 1]
    return m


def months(lang, ms):
    return ", ".join(month(lang, m) for m in (ms or []))


def js_strings(lang):
    """The strings the page needs after load (progress hints, prompts), as a dict for one language."""
    keys = ("dry_running", "dry_none", "dry_stop", "dry_plan", "go_running", "go_done", "go_failed", "undo_q", "undo_running",
            "undo_done", "undo_none", "failed_lines", "saving", "saved_rebuilt", "not_saved", "saved", "already", "refused",
            "cands_note", "cands_none", "near", "date_read", "refresh_running", "refresh_done", "refresh_failed",
            "ai_on", "ai_off", "ai_nokey", "ai_try_q", "ai_asking", "ai_noanswer")
    return {k: t(lang, k) for k in keys}


# ---------------------------------------------------------------- the setup wizard
W = {
    "w_title": {"en": "Setup · make this folder yours", "zh": "建账 · 把这个文件夹变成你的"},
    "w_step": {"en": "Step {i} of {n} · {name}", "zh": "第 {i} 步，共 {n} 步 · {name}"},
    "w_s1": {"en": "Ready", "zh": "准备"}, "w_s2": {"en": "Files", "zh": "文件"}, "w_s3": {"en": "Accounts", "zh": "账户"},
    "w_s4": {"en": "Money in and out", "zh": "收支"}, "w_s5": {"en": "Goal", "zh": "目标"}, "w_s6": {"en": "Day", "zh": "导入日"},
    "w_s7": {"en": "Build", "zh": "生成"},
    "w_back": {"en": "Back", "zh": "上一步"}, "w_next": {"en": "Next", "zh": "下一步"},
    # 1 ready
    "w_ready_h": {"en": "Is this computer ready?", "zh": "这台电脑准备好了吗？"},
    "w_ready_q": {"en": "Python and the PDF reader, checked before anything is asked. About twenty minutes with last month's files at hand.",
                  "zh": "先检查 Python 和 PDF 读取器，再开始问问题。手边有上个月的文件的话，大约二十分钟。"},
    "w_ready_ok": {"en": "✓ ready", "zh": "✓ 准备好了"},
    "w_ready_no": {"en": "✗ not yet — install what it names, then reload this page", "zh": "✗ 还没有——装上它点名的东西，然后刷新这一页"},
    "w_nothing": {"en": "nothing to report", "zh": "没有要报告的"},
    # 2 files
    "w_files_h": {"en": "Last month's files", "zh": "上个月的文件"},
    "w_files_q": {"en": "Drop the statements, the broker's holdings and activities exports, a screenshot of anything held abroad — with the banks' own filenames. They are the draft, and the first import.",
                  "zh": "把银行对账单、券商的持仓和交易导出、境外账户的截图放进来——文件名保持银行给的样子。它们既是草稿的来源，也是第一次导入。"},
    "w_drop": {"en": "Drop files here", "zh": "把文件拖到这里"}, "w_or_choose": {"en": "or choose files", "zh": "或选择文件"},
    "w_none_yet": {"en": "nothing yet", "zh": "还没有文件"},
    "w_saving": {"en": "saving …", "zh": "正在保存…"}, "w_reading": {"en": "saved — reading the files …", "zh": "已保存——正在读文件…"},
    "w_drafted": {"en": "✓ {n} account(s) drafted from these files", "zh": "✓ 从这些文件里起草了 {n} 个账户"},
    # 3 accounts
    "w_acc_h": {"en": "Who, and the accounts", "zh": "你是谁，有哪些账户"},
    "w_name_l": {"en": "Your name, as the page should show it", "zh": "你的名字，页面上要显示的"},
    "w_name_says": {"en": " (the statements say {who})", "zh": "（对账单上写的是 {who}）"},
    "w_name_ph": {"en": "your name", "zh": "你的名字"},
    "w_born_l": {"en": "Roughly what year were you born? Only the retirement arithmetic uses it; blank is fine",
                 "zh": "大概哪一年出生？只用来算退休年龄，留空也行"},
    "w_born_ph": {"en": "e.g. 1993", "zh": "例如 1993"},
    "w_acc_q": {"en": "One card per account the files show. Say what each one is for — the page's totals follow from it. Change a name if it is not what you call it.",
                "zh": "文件里出现的每个账户一张卡。说说每个账户是干什么的——页面上的合计都从这里来。名字不是你平时叫的，改掉。"},
    "w_no_balance": {"en": "the exports carry no balance for it", "zh": "导出文件里没有它的余额"},
    "w_call_it": {"en": "what you call it", "zh": "你怎么叫它"},
    "w_bal_ph": {"en": "the balance the app shows", "zh": "App 上显示的余额"},
    "w_debt": {"en": "a debt — it is subtracted, nothing to choose", "zh": "这是负债——直接扣减，不用选"},
    "w_missing": {"en": "Any account these files do not show — savings with no statement this month, a loan, a home, an account abroad?",
                  "zh": "有没有这些文件里没出现的账户——这个月没对账单的储蓄、一笔贷款、房子、境外账户？"},
    "w_missing_tail": {"en": " Add it with the balance the app shows today; leave empty if none.", "zh": "有就加上，填 App 上今天显示的余额；没有就留空。"},
    "w_add_acc": {"en": "+ add an account", "zh": "+ 加一个账户"},
    "w_inst_ph": {"en": "bank or broker", "zh": "银行或券商"}, "w_balance_ph": {"en": "balance", "zh": "余额"},
    "role_buffer": {"en": "Everyday money", "zh": "日常用的钱"}, "role_buffer_why": {"en": "cash I spend from or keep on hand", "zh": "平时花的、手头留的现金"},
    "role_grow": {"en": "Growing", "zh": "在增值的"}, "role_grow_why": {"en": "invested for the long run — the portfolio", "zh": "长期投资——投资组合"},
    "role_set-aside": {"en": "Set aside", "zh": "专款专用"}, "role_set-aside_why": {"en": "already has a purpose: a first home, an emergency fund", "zh": "已经有用途：首付、应急金"},
    "role_none": {"en": "Owned, not money", "zh": "资产，不是钱"}, "role_none_why": {"en": "a home, a car — counted, neither growing nor spent", "zh": "房、车——算进来，但既不增值也不花"},
    # 4 money
    "w_money_h": {"en": "Money in and out, a month", "zh": "一个月的收支"},
    "w_money_q": {"en": "The files suggest a figure where they can; confirm or change it. Blank means not set, never zero.",
                  "zh": "文件能看出来的数已经填上了，确认或改掉。留空表示「未设置」，不会当成零。"},
    "w_take": {"en": "Take-home pay a month", "zh": "每月到手工资"},
    "w_take_sug": {"en": "Your payroll deposit is {per}. Paid twice a month — take-home {sum} a month?", "zh": "工资入账 {per}，一个月两次——到手 {sum} 一个月？"},
    "w_take_none": {"en": "No payroll deposit in these statements. What is your take-home pay a month?", "zh": "这些对账单里没有工资入账。你每月到手多少？"},
    "w_invest": {"en": "To the broker a month", "zh": "每月转去券商的钱"},
    "w_everyday": {"en": "The everyday amount — guilt-free, no categories", "zh": "日常开销额度——随便花、不分类别"},
    "w_everyday_sug": {"en": "From what your cards spent, an everyday amount of {sug} a month is suggested. Keep it, or change it",
                       "zh": "按卡上的消费，每月日常额度建议 {sug}。就这个，或者改掉"},
    "w_amonth": {"en": "a month", "zh": "每月"},
    "w_committed": {"en": "Anything paid every month before you choose anything — rent, a mortgage, a loan? And rent you do not pay now but will after FIRE?",
                    "zh": "每个月不管怎样都要付的——房租、房贷、贷款？还有现在不付、退休后要付的房租？"},
    "w_committed_ph": {"en": "rent, mortgage, car loan …", "zh": "房租、房贷、车贷…"},
    "w_keep": {"en": "continues after FIRE", "zh": "退休后还要付"}, "w_ends": {"en": "ends by then", "zh": "到那时已付完"},
    "w_add_one": {"en": "+ add one", "zh": "+ 加一项"},
    "w_rent": {"en": "Rent you do not pay today but would after retiring early (blank if none)", "zh": "现在不付、提前退休后要付的房租（没有就留空）"},
    "w_planbase": {"en": "Planning spend a month, for the FIRE target (the everyday figure is the usual start)", "zh": "算 FIRE 目标用的每月规划支出（通常从日常额度起步）"},
    # 5 goal
    "w_goal_h": {"en": "One question", "zh": "一个问题"},
    "w_goal_q": {"en": "Is retiring early — reaching the point where work is optional (FIRE) — something you are working toward?",
                 "zh": "提前退休——到了工作可干可不干的那一步（FIRE）——是你在努力的方向吗？"},
    "w_yes": {"en": "Yes", "zh": "是"}, "w_no": {"en": "No", "zh": "不是"}, "w_skip": {"en": "Skip", "zh": "跳过"},
    "w_goal_hint": {"en": "Skipped means no for now; the FIRE pages show only for yes. It can be said later.", "zh": "跳过暂时当作不是；FIRE 页面只在「是」时出现。以后可以再说。"},
    "w_pens_q": {"en": "If you know them: the CPP and OAS your My Service Canada account estimates, and the age each starts. Blank is fine — never guessed.",
                 "zh": "如果知道的话：My Service Canada 上估算的 CPP 和 OAS 每月金额，以及各自从几岁开始。留空就行——不会替你猜。"},
    "w_from_age": {"en": "from age", "zh": "从几岁起"},
    # 6 day
    "w_day_h": {"en": "Your import day", "zh": "你的导入日"},
    "w_day_q": {"en": "The day of the month you sit down with the new statements.", "zh": "每个月你坐下来处理新对账单的那一天。"},
    "w_day_closes": {"en": "Your statements close on the {days}, so the day after the last one brings everything at once.",
                     "zh": "你的对账单在每月 {days} 号出，最晚那份的次日来做，一次就能拿齐。"},
    "w_day_default": {"en": "The 1st is the tool's default; any day works.", "zh": "默认是 1 号；哪天都行。"},
    "w_day_l": {"en": "Day of the month (1–28)", "zh": "每月几号（1–28）"},
    # 7 build
    "w_build_h": {"en": "Build your workspace", "zh": "生成你的工作区"},
    "w_build_q": {"en": "What will be written: your accounts and monthly files, your plan, empty ledgers — then the files in inbox/ are imported as your first month and the page is built. The demo owner's data is cleared.",
                  "zh": "将要写入：你的账户和每月文件、你的计划、空的流水——然后把 inbox/ 里的文件当作第一个月导入，生成页面。演示数据会被清掉。"},
    "w_born_is": {"en": ", born {y}", "zh": "，{y} 年生"},
    "w_sum_acc": {"en": "{n} account(s) from the files", "zh": "文件里的 {n} 个账户"}, "w_sum_added": {"en": " + {n} added", "zh": " + 手加 {n} 个"},
    "w_sum_money": {"en": "take-home {a} · invest {b} · everyday {c} · {n} committed", "zh": "到手 {a} · 投资 {b} · 日常 {c} · 固定支出 {n} 项"},
    "w_not_set": {"en": "not set", "zh": "未设置"},
    "w_sum_goal": {"en": "FIRE: {g} · import day {d}", "zh": "FIRE：{g} · 导入日 {d} 号"}, "w_skipped": {"en": "skipped", "zh": "跳过"},
    "w_later": {"en": "Left for later, in the chat or by hand:", "zh": "留到以后，在对话里或手动补："},
    "later_foreign": {"en": "Anything held in another currency.", "zh": "其他币种的账户。"},
    "later_counterparty": {"en": "Someone paying you back.", "zh": "有人在还你钱。"},
    "later_buckets": {"en": "Your investing buckets and their target bands.", "zh": "投资分桶和目标区间。"},
    "later_files": {"en": "Files that were not recognised.", "zh": "没认出来的文件。"},
    "w_build_hint": {"en": "This takes a minute. Nothing can be undone by a button afterwards: the demo is gone, your data is here.",
                     "zh": "大约一分钟。之后没有撤销按钮：演示数据没了，这里是你的数据。"},
    "w_building": {"en": "building …", "zh": "正在生成…"},
    "w_build_it": {"en": "Build it", "zh": "开始生成"},
    "w_not_finished": {"en": "that did not finish; the lines say why", "zh": "没有完成；上面的行说了原因"},
    "w_built": {"en": "✓ built. Your page is ready; the monthly panel takes over from here.", "zh": "✓ 生成好了。你的页面可以看了；以后每个月在面板上做。"},
    "w_open_dash": {"en": "Open the dashboard", "zh": "打开仪表盘"}, "w_panel": {"en": "The monthly panel", "zh": "月度面板"},
    "w_lang": {"en": "中文", "zh": "English"},
}


def wizard_strings(lang):
    out = {}
    for k, row in W.items():
        out[k] = row.get(lang) or row.get("en") or k
    return out
