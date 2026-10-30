# How Jade Toad works

The detail behind the [README](../README.md).

## Every page

| Section | Page | What it answers |
|---|---|---|
| — | Home | Where you stand, and what you are worth |
| Spending | This month | How much is still free to spend, and where the money went |
| | Year | How the year went, by category and month by month |
| | Subscriptions | What repeats, what it costs a year, what is due next |
| Income | Income | What came in, by source, and how much of it you kept |
| | Investment income | What the portfolio paid you before you sold anything, and which holding pays when |
| Investing | Portfolio | What is invested, by currency, by kind of asset and by bucket |
| | Performance | How it did against one benchmark fund bought on the same days |
| | Holdings | Every position, by role or by account |
| Plan | Budget | What each paycheque is for, and what the funds hold |
| | FIRE | How far the portfolio is from the target, and when it gets there |
| | Drawdown & care | Whether the money lasts, care included, and in how many real stretches of history it would have |
| | Spending baseline | The monthly figure the target is built on, against what you really spend |
| Records | Updates | What each update changed |
| | Accounts | Every place the money sits |
| | Statements | Which statement arrived which month, and what is missing |
| — | Glossary | Every finance term, and every word the page coined |

## Who it is for

> **Who it is for.** Someone in Canada working toward financial independence, with a paycheque, a few accounts at one or two of the big
> five banks, a broker, and a plan they want held to. The tax-sheltered accounts it knows are the
> TFSA, RRSP and FHSA, the money is Canadian dollars, and the retirement arithmetic assumes CPP
> and OAS. Statements are read by parsers, one per bank and kind of statement: today RBC and BMO,
> and Wealthsimple's exports. TD, Scotiabank and CIBC come next, then Questrade and Interactive
> Brokers, in that order. Until a parser exists for your bank, Claude reads those statements by
> hand — slower, and it means it sees them. Everything else — the accounts, the categories, the
> investing rules — is data you set in the interview, so nothing stops you elsewhere.

## What a month looks like

1. **Import day** (the 26th by default; a reminder lists what has arrived and what is missing).
   Download the month's statements into `inbox/`. Leave the bank's filenames alone — that is how
   each file is recognised.
2. **Say "update dashboards".** One local script does the month: every file is named and checked
   for duplicates before anything is touched; each statement is read by its parser and has to
   reconcile to its own totals before a row is written; purchases are filed by merchant; the page
   is rebuilt; the originals move to `archive/`. Claude reads only the script's summary and puts
   to you what a program cannot decide — a merchant it has not seen, a statement no parser could
   read — and you get a short report: what changed, what was noticed, what was decided without
   asking, what needs your word.
3. **Open the page.** Records → Statements shows which month got which file, so a gap is
   visible at a glance.

For Emma the monthly drop is eight files: three RBC PDFs, three BMO PDFs and two Wealthsimple
exports. Yours is whatever your register says.

## Why the numbers can be trusted

Every figure on the page is built from the data folder, never typed. Four checkers hold that
line, and a fifth checks the checkers:

- **Does the money add up** — every ledger's balance chain closes, every statement reconciles to
  its own totals, a repayment is never counted as income, the register agrees with its sources.
- **Does the page follow its design rules** — chart heights, line widths, contrast, navigation
  against sections, this README against the real pages.
- **Does it actually draw** — a headless browser opens every page at three widths and looks for
  anything that failed to render.
- **Are the checkers still checking** — a selftest plants 60 specific faults in a copy of the
  workspace and asserts each one is caught. It exists because a checker once linted an empty
  folder and reported success.

A clean run is silent. Anything else is a numbered finding, grouped by what went wrong.

<details>
<summary>Run them yourself</summary>

```bash
python3 .claude/skills/workspace-checks/scripts/check_data.py .
python3 .claude/skills/workspace-checks/scripts/check_design.py dashboards/finance_dashboard.html
python3 .claude/skills/workspace-checks/scripts/check_render.py dashboards/finance_dashboard.html
python3 .claude/skills/workspace-checks/scripts/selftest.py .
```

`check_data.py` is the one to start with; `-v` lists what passed. `check_render.py` needs Playwright
(`pip3 install --user playwright && python3 -m playwright install chromium`).
</details>

## Under the hood

<details>
<summary>The folder</summary>

```
inbox/        drop new files here; they move to archive/ once processed
findata/      the only source of truth, three folders by who writes them:
  register/     what you declare — accounts, plan, rules, merchants
  ledgers/      what the import writes — every ledger, purchases, the broker's exports
  history/      what each update leaves behind — updates, decisions, filings, snapshots
dashboards/   the built page (one self-contained HTML file)
templates/    the page code with every number empty; dashboards/ is built from it
archive/      processed originals, named <date>_<source>_<original name>
docs/         the pipeline diagram and the Chinese guide
.claude/      the three skills: setup, update-dashboard, workspace-checks
tools/        demo data, migrations, sync into a workspace
```

The folder is called `findata/` because iCloud for Windows refuses to sync any folder named
`data`. That one cost a day.
</details>

<details>
<summary>The pipeline</summary>

![Pipeline](pipeline.svg)

*Editable source: [`pipeline.drawio`](pipeline.drawio), generated by `pipeline.py`.*
</details>

<details>
<summary>The documents that govern it</summary>

| File | Owns |
|---|---|
| [`PRODUCT.md`](../PRODUCT.md) | what the product is for, its principles, and what it deliberately is not |
| `CLAUDE.md` | how Claude works here: the information model, the import, the checkers |
| `FINANCE.md` | the money logic: the FIRE target, pay-yourself-first, what counts as income |
| `DESIGN.md` | how the page looks and talks: palette, navigation, copy |
| `OWNER.md` | **yours** — your banks, your traps, your decisions; the other three name nobody |

They are rules, not notes: each line was written after something went wrong, and they are read
before every change. Anything agreed out loud has to land in one of them or it does not survive
the next session.
</details>

<details>
<summary>The tool and your workspace</summary>

This repository is the tool. Your workspace — the folder with your `findata/`, your
`inbox/`, your `OWNER.md` — is an instance of it. `tools/sync.py <workspace>` copies the skills,
the templates and the governing documents into it and touches nothing that is yours; when the
tool's data shape moves ahead of your folder, `tools/migrate.py <workspace>` brings the folder
up one step at a time.

The page is 17 pages in 5 sidebar groups —
Home · Spending · Income · Investing · Plan · Records · Glossary
— desktop only, at least 1120px wide.
</details>
