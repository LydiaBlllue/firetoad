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

That is the whole instruction. It picks a free port on `127.0.0.1`, prints an address with a
fresh token in it, opens the panel in the system browser, and exits by itself five minutes after
the last tab is closed. `--no-browser` prints the address only; `--port N` fixes the port.

What the panel can do today (1b + 1c): show what is left to bring (the rows `status.py`
draws); take files dropped onto it into `inbox/` under their own names, named by preflight at
once (nothing is parsed until Import); run the import as a dry run and then for real with its
lines streaming in; undo the last import; answer the open questions with pills and save them all
at once; type a balance no file carries (`balance.py` behind it — banks.json and foreign.json
rows with no ledger; the register's copy follows); read such a balance off a phone screenshot
(`ocr.py`: Apple Vision on this computer, the amounts ranked by the account's `capture` line,
offered as pills, never written until tapped; the image is kept under .jade/shots/); open the
inbox folder; and show the last import's result. What it cannot yet: download a statement (the
owner does that, or this chat does with `fetch-statements`), set up a fresh workspace (the
wizard, step 2 of the roadmap), or use a model (step 3). OCR needs `ocrmac`
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
