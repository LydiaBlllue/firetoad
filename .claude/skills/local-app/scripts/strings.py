"""strings.py — every word the panel says, in one place, in English and Chinese.

The dashboard is English (DESIGN.md); the panel is instructions, and instructions are read in
the owner's language. So each string lives here once per language, the page picks one at
render time (`?lang=zh` on the panel, remembered in .jade/settings.json; before that, profile.json
`lang`; before that, the system's language — `system_lang()`), and nothing in panel.py or the template carries a sentence of its
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
    "intro": {"en": "Once a month: get the files, put them here, import, categorize what is left. The highlighted step is where you are.", "zh": "每个月：拿到文件 → 放进来 → 导入 → 给剩下的归类。高亮的那一步就是你现在该做的。"},
    "open_dash": {"en": "Open the dashboard ↗", "zh": "打开仪表盘 ↗"},
    "lang_other": {"en": "中文", "zh": "English"},
    "import_day": {"en": "your import day is the {day}", "zh": "你的导入日是每月 {day} 号"},
    # — the steps
    "s1": {"en": "Get this month's files", "zh": "拿到这个月的文件"},
    "s2": {"en": "Put them here", "zh": "放进来"},
    "s3": {"en": "Import", "zh": "导入"},
    "s4": {"en": "Categorize what is left", "zh": "给剩下的归类"},
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
    # — step 3's result card (drawn from the import's summary, never from its lines)
    "r_dry_h": {"en": "What would happen", "zh": "将会发生什么"},
    "r_done_h": {"en": "Done", "zh": "已完成"},
    "r_files": {"en": "Files read", "zh": "读到的文件"},
    "r_none_read": {"en": "nothing new in inbox", "zh": "inbox 里没有新文件"},
    "r_counts": {"en": "What they hold", "zh": "里面有"},
    "c_statements": {"en": "{n} statement(s)", "zh": "{n} 份对账单"},
    "c_ledger rows": {"en": "{n} account rows", "zh": "{n} 行账户流水"},
    "c_purchases": {"en": "{n} purchases", "zh": "{n} 笔消费"},
    "c_refunds": {"en": "{n} refund(s)", "zh": "{n} 笔退款"},
    "r_asked": {"en": "{n} question(s) for you afterwards — step 4", "zh": "之后有 {n} 个问题要你答——第 4 步"},
    "r_by_hand": {"en": "{n} file(s) no program can read: a person has to", "zh": "{n} 个文件程序读不了，得人来读"},
    "r_untyped": {"en": "{n} row(s) nobody could type", "zh": "{n} 行没人认得出是什么"},
    "r_unknown": {"en": "Stopped: {n} file(s) nobody can name", "zh": "停下了：{n} 个文件认不出是谁的"},
    "r_stopped": {"en": "Stopped", "zh": "停下了"},
    "r_nothing_written": {"en": "Nothing was written.", "zh": "什么都没有写入。"},
    "r_changed": {"en": "What changed", "zh": "变了什么"},
    "r_noticed": {"en": "Noticed", "zh": "顺带发现"},
    "r_findings": {"en": "The checks ask you to look at", "zh": "检查要你看一眼的"},
    "r_clean": {"en": "every check clean", "zh": "所有检查都过了"},
    "r_raw": {"en": "the full record", "zh": "完整记录"},
    # — the questions, said from their facts
    "qs_credit_named": {"en": "{amount} arrived by e-Transfer on {date} from {who}. What is it?", "zh": "{date} 收到 {who} 的 e-Transfer {amount}。这是什么？"},
    "qs_credit": {"en": "{amount} arrived by e-Transfer on {date}; the statement names no sender. What is it?", "zh": "{date} 收到一笔 e-Transfer {amount}，对账单没写是谁。这是什么？"},
    "qs_sent": {"en": "{amount} left by e-Transfer on {date} to someone you have not named. What was it?", "zh": "{date} 转出一笔 e-Transfer {amount}，给了没登记的人。这是什么？"},
    "qs_account_to": {"en": "{amount} went to an account you have not registered, on {date} ({desc}).", "zh": "{date} 有 {amount} 转到一个没登记的账户（{desc}）。"},
    "qs_account_from": {"en": "{amount} came from an account you have not registered, on {date} ({desc}).", "zh": "{date} 有 {amount} 从一个没登记的账户转来（{desc}）。"},
    "qs_merchant": {"en": "{merchant} — the first time it appears. Which category?", "zh": "{merchant}——第一次出现。算哪一类？"},
    "qs_merchant_starter": {"en": "{merchant} — the first time it appears; a known chain, filed as {cat}.", "zh": "{merchant}——第一次出现；常见连锁店，暂记为 {cat}。"},
    "qs_fire": {"en": "Is retiring early (FIRE) something you are working toward? The FIRE pages show only for yes.", "zh": "提前退休（FIRE）是你在努力的方向吗？FIRE 页面只在「是」时出现。"},
    "opt_Pay": {"en": "Pay", "zh": "工资"}, "opt_Family or gift": {"en": "Family or gift", "zh": "家人或礼物"},
    "opt_Other income": {"en": "Other income", "zh": "其他收入"}, "opt_Own money": {"en": "Own money", "zh": "自己的钱"},
    "opt_Paid back": {"en": "Paid back", "zh": "还款"}, "opt_Yes": {"en": "Yes", "zh": "是"}, "opt_No": {"en": "No", "zh": "不是"},
    # — step 4
    "q_intro": {"en": "The import filed everything it could. Tap an answer on each of these, then save once.", "zh": "能归类的都已归好。下面这些每条点一个答案，最后保存一次。"},
    "q_none": {"en": "Nothing to categorize. Anything the next import cannot file appears here.", "zh": "没有要归类的。下次导入归不了类的会出现在这里。"},
    "filed_as": {"en": "for now:", "zh": "现在记为："},
    "suggested": {"en": "suggested:", "zh": "建议："},
    "seen_n": {"en": "seen {n}×", "zh": "出现 {n} 次"},
    "model_dot": {"en": "a model's suggestion", "zh": "模型的建议"},
    "in_ledger": {"en": "answered in its ledger, not here", "zh": "要在流水里改，这里改不了"},
    "save_answers": {"en": "Save answers", "zh": "保存答案"},
    "q_money_h": {"en": "First, the money questions", "zh": "先是钱的问题"},
    "q_sug_h": {"en": "Merchants with a suggestion ({n})", "zh": "已有建议的商户（{n}）"},
    "q_sug_intro": {"en": "Known chains, or a model's guess. Accept them all in one go, or change one.", "zh": "常见连锁店，或模型猜的。一键全收，或者单独改一个。"},
    "q_accept_all": {"en": "Accept all {n} suggestions", "zh": "接受全部 {n} 条建议"},
    "q_accepted": {"en": "accepted — change one below if you like", "zh": "已接受——下面还可以单独改"},
    "q_change": {"en": "change", "zh": "改"},
    "q_unknown_h": {"en": "Merchants nobody knows ({n}), biggest first", "zh": "没人认识的商户（{n}），按金额从大到小"},
    "q_unknown_intro": {"en": "One at a time. Tap a category, or skip — a skipped one stays Other and is asked again if it comes back.",
                        "zh": "一次一个。点一个类别，或者跳过——跳过的先记「其他」，下次再出现再问。"},
    "q_meta": {"en": "{amount} · {n}×", "zh": "{amount} · {n} 次"},
    "q_skip": {"en": "Skip — leave it Other", "zh": "跳过，先记「其他」"},
    "q_skip_all": {"en": "Leave the rest Other", "zh": "其余都先记「其他」"},
    "q_other_now": {"en": "Other is {pct}% of spending", "zh": "「其他」现在占支出 {pct}%"},
    "q_other_after": {"en": "after this one → {pct}%", "zh": "答完这条 → {pct}%"},
    "q_left": {"en": "{n} left", "zh": "还剩 {n} 条"},
    "q_cards_done": {"en": "All seen. Save when ready.", "zh": "都过了一遍。可以保存了。"},
    "q_more": {"en": "more…", "zh": "更多…"},
    "q_brand": {"en": "you filed other {brand} charges as {cat}", "zh": "你之前把别的 {brand} 归为 {cat}"},
    "q_undo_card": {"en": "back one", "zh": "回上一条"},
    "q_saved_one": {"en": "saved", "zh": "已存"},
    "q_saving_one": {"en": "saving…", "zh": "存中…"},
    "q_save_failed": {"en": "not saved — the lines under step 3 say why", "zh": "没存上——第 3 步下面的行说了原因"},
    "q_resume": {"en": "Each answer is saved as you give it; close the tab and come back any time.", "zh": "每答一条就存一条，随时关掉再回来。"},
    "m_title": {"en": "Merchants already filed ({n}) — change one", "zh": "已归类的商户（{n}）——可以改"},
    "m_intro": {"en": "Every purchase of that merchant moves with it, past and future.", "zh": "改一个，这家商户过去和以后的每一笔都跟着变。"},
    "m_none": {"en": "none yet", "zh": "还没有"},
    "m_more": {"en": "show all {n}", "zh": "显示全部 {n} 个"},
    "m_moved": {"en": "moved: {n} purchase(s)", "zh": "已改：{n} 笔"},
    "unanswered_keep": {"en": "a row left alone keeps what it is filed as", "zh": "没点的保持现状"},
    "saving": {"en": "saving answers…", "zh": "正在保存答案…"},
    "saved_rebuilt": {"en": "answers saved — the page is rebuilt", "zh": "答案已保存——页面已重建"},
    "not_saved": {"en": "not saved; the lines under step 3 say which answer was refused", "zh": "没保存；第 3 步下面的行说了哪条被拒绝"},
    # — step 5
    "last_import": {"en": "last import {date}", "zh": "上次导入 {date}"},
    "no_import": {"en": "No import yet.", "zh": "还没有导入过。"},
    # — the folder's tool copy
    "tool_newer": {"en": "This folder was made by a newer FIRE Toad. Update the app to use it. Nothing is changed until then.", "zh": "这个文件夹是更新版的 FIRE Toad 建的。请先更新应用。在那之前不会改动任何东西。"},
    "tool_migrate": {"en": "This folder was made by an older FIRE Toad and has to be converted first. Your data stays as it is.", "zh": "这个文件夹是旧版 FIRE Toad 建的，要先转换。你的数据不会动。"},
    "tool_differs": {"en": "This folder was made by an older FIRE Toad. Update it to match this version. Your data stays as it is.", "zh": "这个文件夹是旧版 FIRE Toad 建的。把它更新到这个版本，你的数据不会动。"},
    "refresh_copy": {"en": "Update", "zh": "更新"},
    "refresh_running": {"en": "updating this folder…", "zh": "正在更新这个文件夹…"},
    "refresh_done": {"en": "Updated.", "zh": "已更新。"},
    "refresh_failed": {"en": "The update did not finish. The lines above say why.", "zh": "更新没完成。上面几行写了原因。"},
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
    # — a run that stopped: a code, one line, the text to copy (applog.report), where the log is
    "err_h": {"en": "That did not finish.", "zh": "没有完成。"},
    "err_copy": {"en": "Copy error", "zh": "复制错误信息"}, "err_copied": {"en": "Copied", "zh": "已复制"},
    "err_log": {"en": "Log", "zh": "日志"},
    "err_code": {"en": "Error code", "zh": "错误代码"}, "err_run": {"en": "Run", "zh": "运行编号"},
    "err_start": {"en": "FIRE Toad could not start.\n\n{code}\n{message}", "zh": "FIRE Toad 没能启动。\n\n{code}\n{message}"},
    # — the app's first launch (app.py), before there is a folder: the system's language, one at a time
    "welcome": {"en": "Welcome to FIRE Toad. Everything it keeps is in one folder on this Mac.",
                "zh": "欢迎使用 FIRE Toad。它的所有内容都放在这台 Mac 上的一个文件夹里。"},
    "create_folder": {"en": "Create my folder", "zh": "新建文件夹"},
    "open_folder": {"en": "Open my folder", "zh": "打开文件夹"},
    "choose_again": {"en": "Choose again", "zh": "重新选择"},
    "quit": {"en": "Quit", "zh": "退出"},
    "choose_prompt": {"en": "Choose your FIRE Toad folder", "zh": "选择你的 FIRE Toad 文件夹"},
    "not_a_folder": {"en": "This is not a FIRE Toad folder: {path}", "zh": "这不是 FIRE Toad 文件夹：{path}"},
    "your_folder": {"en": "Your folder: {path}", "zh": "你的文件夹：{path}"},
}

MONTHS = {"en": ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
          "zh": tuple(f"{i} 月" for i in range(1, 13))}


def system_lang():
    """The system's own language, `zh` or `en`: what the first launch speaks before there is a
    folder, and the panel's when nothing was chosen yet (2026-11-12, user 001: not both at
    once). macOS keeps the order of preferred languages in AppleLanguages; elsewhere the locale."""
    import re
    import subprocess
    import sys
    first = ""
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True, text=True).stdout
            m = re.search(r"[A-Za-z]{2}[\w-]*", out)   # ("zh-Hans-CA", "en-CA") → zh-Hans-CA
            first = m.group(0) if m else ""
        except OSError:
            pass
    if not first:
        import locale
        import os
        first = os.environ.get("LC_ALL") or os.environ.get("LANG") or (locale.getlocale()[0] or "")
    return "zh" if first.lower().startswith("zh") else "en"


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
    keys = ("r_dry_h", "r_done_h", "r_files", "r_none_read", "r_counts", "c_statements", "c_ledger rows", "c_purchases", "c_refunds",
            "r_asked", "r_by_hand", "r_untyped", "r_unknown", "r_stopped", "r_nothing_written", "r_changed", "r_noticed",
            "r_findings", "r_clean", "r_raw",
            "q_money_h", "q_sug_h", "q_sug_intro", "q_accept_all", "q_accepted", "q_change", "q_unknown_h", "q_unknown_intro",
            "q_meta", "q_skip", "q_skip_all", "q_other_now", "q_other_after", "q_left", "q_cards_done", "q_more", "q_brand",
            "q_undo_card", "q_saved_one", "q_saving_one", "q_save_failed", "q_resume", "m_moved", "q_change",
            "filed_as", "suggested", "seen_n", "in_ledger", "model_dot",
            "dry_running", "dry_none", "dry_stop", "dry_plan", "go_running", "go_done", "go_failed", "undo_q", "undo_running",
            "undo_done", "undo_none", "failed_lines", "saving", "saved_rebuilt", "not_saved", "saved", "already", "refused",
            "cands_note", "cands_none", "near", "date_read", "refresh_running", "refresh_done", "refresh_failed",
            "ai_on", "ai_off", "ai_nokey", "ai_try_q", "ai_asking", "ai_noanswer",
            "err_h", "err_copy", "err_copied", "err_log", "err_code", "err_run")
    return {k: t(lang, k) for k in keys}


# ---------------------------------------------------------------- the setup wizard
W = {
    "w_title": {"en": "Setup · make this folder yours", "zh": "建账 · 把这个文件夹变成你的"},
    "w_step": {"en": "Step {i} of {n} · {name}", "zh": "第 {i} 步，共 {n} 步 · {name}"},
    "w_s2": {"en": "Files", "zh": "文件"}, "w_s3": {"en": "Accounts", "zh": "账户"},
    "w_s4": {"en": "Money in and out", "zh": "收支"}, "w_s5": {"en": "Goal", "zh": "目标"}, "w_s6": {"en": "Day", "zh": "导入日"},
    "w_s7": {"en": "Build", "zh": "生成"},
    "w_back": {"en": "Back", "zh": "上一步"}, "w_next": {"en": "Next", "zh": "下一步"},
    # the readiness check, shown on the files screen only when something is missing
    "w_need_h": {"en": "Before the statements can be read", "zh": "读对账单之前还缺一样东西"},
    "w_py_old": {"en": "Python {v} is too old — {min} or newer is needed (python.org)", "zh": "Python {v} 太旧——需要 {min} 或更新（python.org）"},
    "w_pdf_missing": {"en": "the PDF reader is missing — statements cannot be read until it is installed. In a terminal:", "zh": "缺 PDF 读取器——装上之前读不了对账单。在终端里运行："},
    "w_need_then": {"en": "Then reload this page.", "zh": "装好后刷新这一页。"},
    "w_nothing": {"en": "nothing to report", "zh": "没有要报告的"},
    # 2 files
    "w_files_h": {"en": "Bring your last 1–3 months", "zh": "带上最近 1–3 个月的文件"},
    "w_how_long": {"en": "How long?", "zh": "要多久？"},
    "w_files_q": {"en": "Keep the names the bank gave the files.", "zh": "文件名保持银行给的样子。"},
    "w_files_1": {"en": "Bank and card statements (PDF)", "zh": "银行和信用卡对账单（PDF）"},
    "w_files_2": {"en": "Broker exports (CSV)", "zh": "券商导出（CSV）"},
    "w_files_3": {"en": "Screenshots of accounts abroad", "zh": "境外账户的截图"},
    "w_long_1": {"en": "Download from each bank", "zh": "从每家银行下载"}, "w_long_1v": {"en": "5–10 min", "zh": "5–10 分钟"},
    "w_long_2": {"en": "These six screens", "zh": "这里的六屏"}, "w_long_2v": {"en": "5–8 min", "zh": "5–8 分钟"},
    "w_long_3": {"en": "Categorize what is left", "zh": "给剩下的归类"}, "w_long_3v": {"en": "5–10 min", "zh": "5–10 分钟"},
    "w_long_sum": {"en": "One bank and a broker", "zh": "一家银行加一家券商"}, "w_long_sumv": {"en": "20–30 min", "zh": "20–30 分钟"},
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
    "w_ofx_q": {"en": "{file} is a bank download that names its accounts by number, not the bank. Which bank is it from?",
                "zh": "{file} 是银行下载的文件，里面只有账号没有银行名。它来自哪家银行？"},
    "w_ofx_ph": {"en": "the bank's name, e.g. RBC", "zh": "银行名，例如 RBC"},
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
    "w_build_h": {"en": "Build your page", "zh": "生成你的页面"},
    "w_build_q": {"en": "Check these, then build. Your files are read and your page is made.", "zh": "核对一下，然后生成。程序会读你的文件，做出你的页面。"},
    "w_born_is": {"en": ", born {y}", "zh": "，{y} 年生"},
    "w_sum_acc": {"en": "{n} account(s) from the files", "zh": "文件里的 {n} 个账户"}, "w_sum_added": {"en": " + {n} added", "zh": " + 手加 {n} 个"},
    "w_not_set": {"en": "not set", "zh": "未设置"},
    "w_skipped": {"en": "skipped", "zh": "跳过"},
    "w_later": {"en": "You can add these later:", "zh": "这些可以以后再加："},
    "later_foreign": {"en": "Anything held in another currency.", "zh": "其他币种的账户。"},
    "later_counterparty": {"en": "Someone paying you back.", "zh": "有人在还你钱。"},
    "later_buckets": {"en": "Your investing buckets and their target bands.", "zh": "投资分桶和目标区间。"},
    "later_files": {"en": "Files that were not recognised.", "zh": "没认出来的文件。"},
    "w_build_hint": {"en": "It takes about a minute.", "zh": "大约一分钟。"},
    "w_building": {"en": "Building your page…", "zh": "正在生成你的页面…"},
    "w_build_it": {"en": "Build it", "zh": "开始生成"},
    "w_not_finished": {"en": "That did not finish.", "zh": "没有完成。"},
    "w_built": {"en": "Your page is ready.", "zh": "你的页面好了。"},
    "w_open_dash": {"en": "Open the dashboard", "zh": "打开仪表盘"}, "w_panel": {"en": "Monthly import", "zh": "月度导入"},
    "w_details": {"en": "Details", "zh": "详情"},
    "w_err_copy": {"en": "Copy error", "zh": "复制错误信息"}, "w_err_copied": {"en": "Copied", "zh": "已复制"},
    "w_err_log": {"en": "Log", "zh": "日志"},
    "w_err_code": {"en": "Error code", "zh": "错误代码"}, "w_err_run": {"en": "Run", "zh": "运行编号"},
    "w_sum_name": {"en": "Name", "zh": "名字"}, "w_sum_born": {"en": "Born", "zh": "出生年"},
    "w_sum_accounts": {"en": "Accounts", "zh": "账户"}, "w_sum_take": {"en": "Take-home a month", "zh": "每月到手"},
    "w_sum_invest": {"en": "To the broker a month", "zh": "每月投资"}, "w_sum_every": {"en": "Everyday a month", "zh": "每月日常开销"},
    "w_sum_fixed": {"en": "Fixed costs", "zh": "固定支出"}, "w_sum_fire": {"en": "Early retirement goal", "zh": "提前退休目标"},
    "w_sum_day": {"en": "Import day", "zh": "导入日"},
    "w_over": {"en": "This plan asks for {ask} a month and take-home is {pay}. The {gap} gap would come from savings.",
               "zh": "这个计划每月要 {ask}，到手是 {pay}。差的 {gap} 要从存款里出。"},
    "w_sort_n": {"en": "{what} to categorize first.", "zh": "先归类：{what}。"},
    "w_sort_go": {"en": "Categorize them", "zh": "去归类"},
    "w_n_merchant": {"en": "{n} merchant(s)", "zh": "{n} 个商户"}, "w_n_transfer": {"en": "{n} transfer(s)", "zh": "{n} 笔转账"},
    "w_n_other": {"en": "{n} question(s)", "zh": "{n} 个问题"}, "w_and": {"en": " and ", "zh": "、"},
    "w_lang": {"en": "中文", "zh": "English"},
}


def wizard_strings(lang):
    out = {}
    for k, row in W.items():
        out[k] = row.get(lang) or row.get("en") or k
    return out
