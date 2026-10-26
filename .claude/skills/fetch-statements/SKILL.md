---
name: fetch-statements
description: Download the owner's monthly bank statements from their online banking in Chrome, once they have signed in themselves — work out from the register which statements are still missing, list them for the owner to approve, download them, and move them into inbox/ for the import. Use when the owner says "download my statements", "get my RBC statements", 下载对账单, or asks to fetch statements before an update. It never signs in, never types a password or a code, and never runs the import by itself.
---

# Fetch statements

What a program can do is in `scripts/fetch.py`: which statements are missing, and which freshly
downloaded files are statements. What needs a browser — the bank's site — is the steps below.
The owner signs in; everything after that is yours, except that **every download is approved
first**.

## The order

1. **What is missing.** Run

   ```bash
   python3 .claude/skills/fetch-statements/scripts/fetch.py missing --bank RBC
   ```

   (`--bank` is the register's `ep`; leave it out for every bank). It reads `documents[]` and
   `filings.json` and prints, per document, the last month filed and every month since that
   should have closed — plus anything already sitting in inbox/. Nothing about which accounts
   exist is written in this skill; the register says.

2. **The owner signs in.** Use Claude in Chrome (their real Chrome, their own session). Open the
   bank's sign-in page in a new tab and **stop**: they type the card number, the password and
   the one-time code. Never fill any of it, even when asked. If a cookie banner is in the way,
   choose the essential-only option or leave it to them.

3. **Find the statements** (bank notes below), and compare what the site offers with step 1.

4. **Ask once, with the list.** Account, statement date, how many files. Wait for a yes. The
   approval covers that list, nothing more.

5. **Download**, then

   ```bash
   python3 .claude/skills/fetch-statements/scripts/fetch.py collect --minutes 30
   python3 .claude/skills/fetch-statements/scripts/fetch.py collect --minutes 30 --write
   ```

   The first compares, the second moves. Only files modified in that window **and** named by
   preflight's own classifier move; everything else in the downloads folder stays where it is.

6. **Run `preflight.py`** (in the update-dashboard scripts) and report. A file it cannot name
   stops here — ask, exactly as the import would. Then the owner says "update dashboards"; this
   skill never starts the import.

## When a filename stops matching

A card that is reissued keeps its account and changes its number, so the bank's file arrives
under a new name and preflight refuses it. **Ask the owner** whether the card was replaced —
never assume. If it was: change that account's `id` and the document's `file` pattern in the
register, keep the `key`, the `spendTag` and the archive `tags` (keys never move, and the filing
history stays one series), and write the date and the old number in both `note`s. Rebuild, and
preflight names the file.

## Bank notes

Each note is what the site actually did, not what it looks like it should do.

### RBC

- Sign-in: `https://secure.royalbank.com/statics/login-service-ui/index#/full/signin?LANGUAGE=ENGLISH`.
  Signed in, the landing page is Accounts Summary.
- Statements: the "Statements/Documents" link on Accounts Summary → Account Documents. Choose
  *Statements & general documents*, open **Accounts → Select all → Apply**, Month **All months**,
  the Year, then **Show Documents**. The list takes a few seconds; read it with page text rather
  than a screenshot — every account and statement date is in it, newest first.
- ⚠ **Each "PDF" link is `javascript:void(0)` and ignores a click by element reference** — the
  click reports success and nothing downloads. Click its **screen coordinates** (zoom on the
  table to place them). Each link appears twice in the tree (desktop and mobile layouts); that is
  not two files.
- Files land in the Chrome downloads folder as `<Type> Statement-<last 4> <YYYY-MM-DD>.pdf`. A
  credit card's "last 4" is the card number, which changes when the card is reissued (above).
- The site keeps seven years, so a missed month can always be fetched later.

### BMO

- Sign-in: `https://www1.bmo.com/banking/digital/login` (it redirects to the sign-in form; the
  card number may already be remembered — the password and the code are still the owner's).
- Statements live **per account**: Accounts → the account → the **Statements** tab, a list of
  dated "PDF file" links for the year. Unlike RBC, a click by element reference downloads.
- Files land as `<Month D, YYYY>.pdf`. Bank accounts that close the same day download under the
  **same name**, and the register tells them apart only by the `-2` the second one carries — so
  fetch one account at a time, `collect` it into inbox/ before the next, and **read each file
  with `parse.py` before naming it**: the account the statement itself names decides which file
  gets the `-2`, never the page it was downloaded from.
- ⚠ **Consolidated statements.** When the Statements tab says *Statement type: Consolidated*,
  one PDF carries the main account and its member accounts, and every member's page offers a
  copy of that same statement. The copies differ by a few bytes, so preflight's byte-identical
  check does not catch them; importing two would book the member accounts twice. Download the
  consolidated statement **once** (from the main account) — the import files every account in
  it under its own document. The switch can happen mid-year: the months before it are still
  separate files.
- A download can arrive twice (a second copy named `… (1).pdf`, sometimes opened in a tab of
  its own). Check the downloads folder after each batch; a copy is a duplicate, not a statement.
- The closing day moves to the business day before a weekend (the 5th became the 4th), which
  preflight's few-day tolerance absorbs.
