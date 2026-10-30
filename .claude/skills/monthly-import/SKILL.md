---
name: monthly-import
description: The monthly import as taps instead of typing — draw a panel of everything the owner has to bring this month (bank statements, broker exports, phone screenshots, balances no file carries, open questions), each with the one button that moves it forward, then run fetch-statements and update-dashboard behind those buttons and draw the panel again after every step. Use when the owner says "start the monthly import", 开始月度导入, 月度导入, "what do I still need to bring", on the import day (profile.json `importDay`), or when the import-day reminder opens the session.
---

# Monthly import

The owner should be able to do a whole month by tapping. This skill is the order and the panel;
the work is done by the two skills underneath it — `fetch-statements` (downloads) and
`update-dashboard` (the import). Read neither from memory; invoke them when a button says so.

Everything on the panel comes from one command:

```bash
python3 .claude/skills/monthly-import/scripts/status.py --json
```

Rows exist because the register has a document or an account for them; their state comes from
`filings.json`, each account's `asof`, and what is waiting in inbox/. **Never add, drop or rename
a row by hand** — if the panel is wrong, the register is, and that is what to fix.

## The order

1. **Run `status.py --json` and draw the panel** (below). Say nothing else but one line: how many
   things are left for the owner, and the one to do first.
2. **Wait for a tap.** Each button sends a prompt; do what the table says, then run `status.py`
   again and **draw the panel again** — the owner should always be looking at the current state,
   never at a list in the scrollback.
3. When nothing on the panel is `todo` (or the owner taps *Import what's here*), invoke
   `update-dashboard`. Its run reports `?` items; they are already rows in `decisions.json`, so
   run `status.py` once more and draw the **questions card**.
4. After the answers are written, draw the **result card**: the import record's `changed` and
   `noticed`, read from the newest entry in `imports.json`. That is the report.

Anything `unnamed` (a file preflight cannot name) is drawn first, in red, and **stops the run**:
ask what it is. Never infer an account from a filename.

## What each button does

| Button | What it sends | What you do |
|---|---|---|
| a bank row: *Signed in* | that bank, signed in | invoke `fetch-statements` for that bank (it lists, asks once, downloads, collects) |
| a bank row: *Open sign-in* | open that bank | open the bank's sign-in page in Chrome (the bank notes in `fetch-statements`) and stop |
| an export row: *Signed in* | that broker, signed in | `fetch-statements` for that broker if it has notes for it; otherwise say which export to make, in one line, and wait for *Exported* |
| an export row: *Exported* | exported | `fetch.py collect`, then redraw |
| screenshots: *They're in inbox* / an image sent in chat | screenshots are in | look at every image: name the app and page each one shows, match it to a `capture` row, read the balance and its date. Save images sent in chat to inbox/ as `<inst> <page> <date>.<ext>`. A row no image matches stays `todo`; an image no row matches is asked about |
| screenshots: *Skip this month* | skip | leave them; the page already says how old they are |
| a balance row: *Read it from the site* | read the balance | read the number and its date off the signed-in page in Chrome; if nobody is signed in, open the sign-in page and wait for *Signed in* rather than asking the owner to type it |
| a person row: *Nothing changed* | nothing to do | drop the row for this run |
| *Import what's here* / *Start import* | import | invoke `update-dashboard` |
| questions card: *Save answers* | every answer at once | for each: write `answer` and `resolved` on its `decisions.json` row, apply it (`merchants.json`, the ledger's `type`), then rebuild and run the checkers |

Write the button labels **and the prompts they send** in the owner's language (OWNER.md); the
prompt is what appears in the chat as theirs, so it should read like something they would say.

## Drawing it

Use the inline widget tool (`show_widget`); a button calls `sendPrompt(...)`. One card, one row
per row of `status.py`, grouped in the order of the JSON. Each row: an icon, the institution,
one line of what is missing (*2 statements: Sept, Oct* — never a filename), a state pill, and at
most two buttons. States: `todo` (warning tint) · `inbox` (waiting in inbox, success tint) ·
`ok` (success tint, no button) · `optional` (neutral). Rows that are `ok` collapse into a single
line at the bottom ("BMO, RBC, Wealthsimple up to date") so the card shows only what is left.

- **Screenshots** are one row per account, and the line is the account's `capture` — the app,
  the page, the number to see. The owner should be able to take the screenshot from the panel
  alone. An account with no `capture` falls back to "the page with the balance"; when that
  happens, ask once what page they use and write it to the register as `capture` with today's
  date, so next month's panel says it.
- **Questions card**: one row per open question — the question, its `suggest` (or, with none,
  its current default) as the selected pill, and the `choices` as pills to tap (merchants: the categories; money in from no named
  sender: Pay, Other income, Own money, Paid back; other e-Transfers: the ledger types, most used
  first — show the first five and a *More* pill). Answers are saved with `confirm.py --set`. Tapping only selects,
  in the widget's own state. One button at the bottom, *Save answers*, sends every selection in
  one prompt, numbered by the question's `index`. An unanswered row keeps its default.
- **Result card**: net worth before and after, the other `changed` lines, then `noticed` with
  its severity. Nothing else.

Keep it the size of a phone screen. The panel is the instructions; the chat around it is one
line.

## When the reminder starts the session

The import-day task opens a session and asks for this skill. Draw the panel and nothing else —
no import is started until the owner taps.
