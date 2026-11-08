---
name: local-app
description: Open Jade Toad in the browser without Claude — start the local app (python3 app.py), which serves the built dashboard and the monthly panel (Bring · Import · Questions · Result) on 127.0.0.1 and runs the same scripts the import skills run. Use when the owner says "open the app", "start the local app", 打开本地应用, 不用 Claude 打开面板, or asks how someone without a Claude plan runs their workspace.
---

# The local app — the second door

Claude Code is one way into a workspace; `app.py` is the other (ROADMAP 2.0.0, decided
2026-11-05). Both call the same scripts — `status.py`, `update.py`, `confirm.py`, `rebuild.py`
— so a month done by tapping in the browser leaves exactly what a month done in this chat
leaves; the selftest holds the two doors to the same `findata/`.

```bash
python3 app.py
```

That is the whole instruction — or, packaged, a double-click: `python3 build/build.py` makes
`dist/Jade Toad.app` (a folder with Python, the tool and the demo inside; `build/build.py` says
what goes in and what never does). The packaged app asks for the workspace folder on its first
launch — *Open a folder* or *Make one* — and remembers it in the system's application-support
folder, never in the workspace; `--choose` asks again. On every launch it compares the folder's
copy of the tool with its own (`app.py` `tool_state`, sync.py's rules): a folder that differs
gets a *Refresh the copy* button on the panel, a folder whose data is a newer shape than the
app builds is shown and **not written to** until the app is updated. Inside the app there is no
`python3`: the app's own binary runs the core's scripts when the core calls them. It picks a free port on `127.0.0.1`, prints an address with a
fresh token in it, opens the panel in the system browser, and exits by itself five minutes after
the last tab is closed. `--no-browser` prints the address only; `--port N` fixes the port.

**The panel is five numbered steps in the owner's language** (2026-11-07, after the owner could
not tell what the first version wanted): 1 get this month's files (one row per thing, a plain
state — still missing · in inbox · up to date — and *How do I get it?* folded under each missing
one: the bank's own download path from `parsers/support.py`, the app page for a screenshot, a
field for a number) · 2 put them here · 3 import (look first, then import) · 4 answer a few
questions · 5 done. A strip at the top lights the current step and one line says what to do
next. Every sentence is in `scripts/strings.py`, English and Chinese; the page picks the
language from `?lang=zh|en` (remembered in .jade/settings.json), else profile.json `lang`, else
English, and the header has the switch. The setup wizard reads its words from the same table
(`W` in `scripts/strings.py`) and switches the same way; the draft's own sentences are not shown
— the wizard says each question in its own words with the draft's figure in it.

Step 4 writes each answer as it is given (`POST /api/answers` with `ok: false`, the item named
by its `id:` in decisions.json), so a closed tab loses nothing; Save confirms the rest. The
merchants already filed are listed under it and any can be refiled (`confirm.py --refile
"MERCHANT=Category" --write` does the same from this chat).

What the panel can do today (1b + 1c): show what is left to bring (the rows `status.py`
draws); take files dropped onto it into `inbox/` under their own names, named by preflight at
once (nothing is parsed until Import); run the import as a dry run and then for real with its
lines streaming in; undo the last import; answer the open questions with pills and save them all
at once; type a balance no file carries (`balance.py` behind it — banks.json and foreign.json
rows with no ledger; the register's copy follows); read such a balance off a phone screenshot
(`ocr.py`: Apple Vision on this computer, the amounts ranked by the account's `capture` line,
offered as pills, never written until tapped; the image is kept under .jade/shots/); open the
inbox folder; and show the last import's result. **A fresh folder gets the
setup as screens** (step 2, 2026-11-06): while `findata/` is still the demo's, `/panel` draws the
wizard instead — Files · Accounts · Money in and out · Goal · Day · Build — from
`setup/scripts/wizard.py`, which drafts the screens with `propose.py` from the files dropped
and, on *Build it*, writes `setup-answers.json` in the skill's own shape, runs the scaffold, the
rebuild and the first import. A question skipped stays unanswered (the skill's rule); what the
screens do not cover (anything abroad, a counterparty, the buckets, a CSV or OFX nobody could
name) is listed on the last screen as left for the chat. **A model, by choice** (steps 3 and 4, 2026-11-06): the panel's last card is one setting —
Off · With my own key (an OpenAI-compatible service, or Anthropic) · On this computer (Ollama).
Off is the default and means not one call. On, `ai.py` in the update-dashboard scripts is asked
at exactly one place: a merchant that merchants.json, the earlier rows, the brand and the
starter map all miss. It sends the merchant string and the fifteen category names, nothing
else; the answer has to be one of the fifteen or it is dropped; it becomes the question's
*suggestion* (a dot marks it on the panel) and never the filing — Other stays until the owner
confirms. The key lives in the macOS Keychain (service "Jade Toad"), never in the workspace;
the choice in .jade/settings.json; every exchange in .jade/log/ai.jsonl; one merchant costs
one call (.jade/ai_cache.json). The same setting from this chat:
`python3 .claude/skills/update-dashboard/scripts/ai.py . status | set <provider> … | off | test "<merchant>"`.
What it cannot yet: download a statement (the owner does that, or this chat does with
`fetch-statements`). OCR needs `ocrmac`
(`pip3 install --user ocrmac`; on the system Python 3.9, `pyobjc-core<11` first); without it the
panel says so and the amount is typed.

## Rules the server keeps

- **No financial logic in it.** Every route is one call into a script's `run()`
  (`.claude/skills/local-app/scripts/server.py` lists them in its docstring). A new thing the
  panel should do is first a thing the script can do.
- **One writer.** A lock file (.jade.lock) in the workspace while a verb runs; a second import or save gets
  409 and the panel says what is running. A run from this chat while the app imports would race
  it — look for the lock file first.
- **Loopback only, token in the path, no CORS.** A wrong token is 404.
- **It never edits the page.** The import rebuilds through `rebuild.py` as it always did; the
  browser reloads the static file.
- Logs: the app.log file under .jade/log/ in the workspace, nothing in the repository (both are gitignored).
- **The build carries no workspace.** `build/build.py` refuses a checkout whose `findata/` is
  not the demo's, and bundles only what `tools/sync.py` copies plus the demo. Without `--sign`
  it is ad-hoc signed (this Mac runs it; another asks for right-click → Open once); a public
  download needs `--sign` with a Developer ID and `--notarize`.
