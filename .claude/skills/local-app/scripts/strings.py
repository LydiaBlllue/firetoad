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
    "export_line": {"en": "{key} export · newest {asof}", "zh": "{key} 导出 · 最新到 {asof}"},
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
    """The string for `key` in `lang` (English when the language has none), formatted."""
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
