# Roadmap

What is planned for the next releases, and roughly when. Dates are targets, not promises; what
shipped is in [`CHANGELOG.md`](CHANGELOG.md).

Every release goes out the same way: a privacy scan of every changed file and commit message, a
fresh clone that must rebuild to the committed page with every checker clean and every planted
fault caught, then a pull request from the release branch, merged as one squashed commit on
`main` (since 2026-10-29), tagged with its version, and the live demo redeploys with it.

How work reaches a release (since 2026-10-30):

- **`main` is the released tool**, and only a release or a hotfix changes it, so what users get
  and what the demo shows are always a finished version.
- **One branch per coming version**, named for it (`v1.3`). Everything for that version is
  committed there, without a pull request; work done side by side starts a short branch from it
  and is merged back locally.
- **A hotfix** — a bug in the released tool that users would hit — is a small pull request
  straight to `main`, which is then merged back into the version branch.
- **After a release**, the next version's branch starts from the new `main`.
- The first owner's workspace is synced from the version branch, so a change runs on real data
  for a month before anyone else gets it.

Items marked *(first user)* came from the first person other than the owner to set the tool up
from scratch: one credit card, nine statements, a cloud session.

## The first release — by 2026-11-29

v1.1 and v1.2 are the first release: the version a friend can set up alone and the one that is
announced. Four weeks, one outcome each (positioning: PRODUCT.md §2).

| week | what | done when |
|---|---|---|
| 1 · 10-29 → 11-04 | v1.1 shipped · the live demo · the positioning in PRODUCT.md | one link opens the full demo |
| 2 · 11-05 → 11-11 | the core of v1.2 · three to five friends found, **and their banks asked first** | a list of friends and their banks |
| 3 · 11-12 → 11-18 | v1.2 finished · a fresh setup run end to end · the first two friends set up, each report in `feedback/` | two friends see their own page within 20 minutes |
| 4 · 11-19 → 11-29 | the friends' P0s fixed · v1.2 released · the first post: the demo link and a one-minute recording | announced |

- **The basics come first** (2026-10-29). Limited features, not rough ones: a friend sets up
  alone, the first import reconciles with no false alarm, every purchase gets a category to
  confirm, and net worth, spending and the FIRE target are right on their own data with every
  checker clean. A release that misses one of these is not announced.
- **The risk is the banks.** The parsers read RBC and BMO; a friend at another bank is read by
  hand, slower and less trusted. If most of the friends bank elsewhere, week 3 writes that
  bank's parser instead.
- **Not in this month**: v1.3 and later, a bank or broker connection, the browser-only
  experiment, announcing the monthly import panel (it ships in the tool, unannounced).
- **The test** is the second month: whether the friends come back for the import around the
  next import day (PRODUCT.md §2, *What success looks like*).

## v1.1 — shipped 2026-10-29

Merged into `main`; what it carries is in CHANGELOG, 1.1.

## Between v1.1 and v1.2

- **A live demo, one click away.** The demo owner's page is published on GitHub Pages from
  `main`, and the README's first screen links to it, so seeing the product needs no download.

## v1.2 — 2026-11-24 — a first setup that works for someone else

**Released 2026-10-29** — what each item became is in CHANGELOG, 1.2. Still open, and carried
into v1.3: the screenshots a step in *Start here* (the words are done), and spreading a bill paid
once a year over twelve months when months are compared. Setup was run end to end for a card-only owner, and
the selftest now does that every time; the migration was run on a copy of user 001's workspace.

- **The demo on a phone.** A link shared on social media is opened on a phone, and the page is
  built for 1120px and wider. First step: the live demo's front door shows a phone the
  screenshots, in Chinese or English by the phone's language, with a button to send the link to
  a computer; a wide screen goes straight to the page. Next: a simplified view of Home that
  reads at phone width.
- **Every suggestion confirmed in one table.** *(first user)* The starter map now files a common
  chain under its category on the first import (1.1); what is left is asking all of them at
  once, in one table on the panel, instead of one question each.
- **Start here, in pictures.** One path from nothing to a first page, a screenshot a step:
  install the Claude desktop app, open its **Code** tab (not Chat), choose the downloaded folder,
  say *set this up*. No git, no terminal. The first screen of the README says the same, so
  someone who opened it in Chat is pointed back to the right place.
- **Ready before it starts.** *(first user)* Setup checks for Python and the PDF reader first and
  says exactly what to install, and says up front how long it takes and how many steps there
  are; each step says where it is.
- **A number you never gave is not shown as one.** *(first user)* A question skipped at setup —
  income, the investing amount, the year of birth — reads *Not set* on the page, with the place
  to set it, instead of a default that looks like a fact.
- **Spending only, if that is all you bring.** *(first user)* A workspace with only a credit
  card is a complete product: the spending pages in full, the pages that need more data folded
  away until it arrives.
- **No false alarms on a first import.** *(first user)* Two identical charges on one statement
  are two purchases, not a duplicate; negative amounts are compared in one format; a workspace
  with no broker is not asked for a broker's file.
- **A second account after the first.** *(first user)* Adding an account once setup is done is
  something you say, not a file you edit: it reads the new statements, drafts the row, and the
  first import creates its balance, so net worth moves with it.
- **Every chequing row gets a type.** *(first user)* Bills — property tax, insurance, a phone
  plan — a government refund, a cash withdrawal and a transfer between banks are recognised, and
  Bill is a type of its own. *(Built; replaced by the next item, which makes a bill spending.)*
- **Spending is what it is, not how it was paid** (decided 2026-10-29, for the target user;
  replaces the seven categories). *Built on `v1.2` (CHANGELOG); still open: a bill paid once a
  year spread over twelve months.* Spending is money that leaves and buys nothing you still own:
  card and debit purchases, and from chequing rent, bills, cash taken out, fees and interest,
  and money sent to family. Not spending: moving money between your own accounts (abroad
  included), investing, a card payment, lending, being repaid, loan principal.
  - **Three groups, fifteen categories.** *Fixed* — Housing, Bills. *Everyday* — Groceries,
    Dining, Transport, Shopping, Software & tools, Entertainment, Health, Travel, Family & gifts, Cash, Fees,
    Other. *For a time* (it ends) — Education: tuition, books, exams and credential
    assessments. Each category has a default group the owner can change.
  - **What each group counts for.** Only Everyday is measured against the guilt-free
    allowance. Fixed and Everyday make the measured spending the FIRE target is calibrated on;
    For a time is in the year's total and never in the target. A bill paid once a year is
    spread over twelve months when months are compared.
  - **A subscription is a mark, not a category.** A charge that repeats — one merchant, one
    price month after month — is detected and marked, and the subscriptions list is
    every marked charge; each keeps the category of what it bought.
  - **Family money.** Money sent to family is Family & gifts, asked once, since a program
    cannot tell a parent from the owner's own account abroad. Money from family (a parent
    paying toward tuition) is other income.
  - Rent and a mortgage stay declared flows as well, matched against the ledger (D21), so a
    payment is counted once. The owner's workspace maps its seven categories across.
- **The selftest never crashes on an owner's own data.** *(first user)* A workspace with no
  fund, or anything else the demo has and an owner may not, gets an answer, not an error.
- **Setup, tested end to end.** A fresh workspace set up the way a new owner would, then
  compared with a real one: what the interview misses becomes the next list.

## v1.3 — 2026-12-15

- **The monthly import as a panel.** Everything to bring this month (statements, broker
  exports, phone screenshots, balances no file carries, open questions), each with the one
  button that moves it forward. In the tool since 2026-10-30, so a sync no longer removes it;
  still to run through one real import before it is announced.
- **An account seen only in payments is offered.** *(first user)* When the statements show money
  moving to or from an account nobody registered, setup asks whether to add it, so a card-only
  owner's net worth is not just the card's debt.
- **A regular e-Transfer may be pay.** *(first user)* When the same amount arrives every month
  from no named sender, the question offers it as income first.
- **Cashback has a home.** *(first user)* A redemption is filed as a reward, not left as a credit
  nobody claimed.
- **The selftest passes on a fresh machine.** *(first user)* One case failed in a cloud session
  and passes locally; reproduce it there and fix it.

## v1.4 — January 2027

- **Government pensions in the drawdown.** CPP and OAS, from the owner's own statement, so the
  plan stops overstating what has to be saved.
- **Chequing, transaction by transaction.** Transfers, fees and e-Transfers one row each, with
  search by merchant and a filter by account.
- **A checker for charts drawn by month**: the months must have an end (DESIGN.md §5f).
- **Charts draw in** the first time they appear (optional).

## v2.0 — after v1.4 — the page on a framework, the data in a database

Decided 2026-10-30 (user 001). This month was built twice in React to compare, on the
`proto-react-month` branch (`prototypes/`): with Tremor, and with shadcn/ui. The shadcn/ui build
keeps the page's look, reads as four shared blocks (a labelled card, a stat, a label-and-value
list, a ranked bar row) plus the flow chart, and is 216 KB as one file. It is the starting point.
The move is planned here so it does not land in the middle of the first release.

- **The page is built from components, not from strings.** React with shadcn/ui, whose
  components are copied into the repository as source; Svelte 5 is the second choice. Tremor is
  not used: it has no flow chart, and its colours need a safelist to take the fifteen
  categories. The charts stay hand-drawn SVG, one component each, as the prototype's
  `FlowChart` already is.
- **Users install nothing new.** Node is needed only to develop the page. Vite builds it into
  one self-contained HTML template that is committed; `rebuild.py` fills in the data as today,
  so a user still needs only Python, and the page still opens from disk with nothing fetched.
- **The data goes in as one JSON block**, not 48 constants, and T1 checks that the template's
  block is empty.
- **The checkers follow.** `check_design` and `check_render` read the built page, and the
  selftest plants its faults in the component sources.
- **One page at a time**, This month first, each released only when the checkers pass on it.

**The data moves into a database** (decided 2026-10-30, user 001), in the same release, so the
data layer is rewritten once with the page rather than twice:

- **SQLite, through Python's own `sqlite3`**: nothing new to install. What it buys: an import
  is one transaction, written whole or not at all; two writers (an import and a save from the
  page) queue instead of overwriting each other; the simple rules (a category is one of the
  fifteen, a key is unique) are constraints a bad row cannot pass; any question about the data
  is one query, which a search or filter on the page can ask without Claude; and a later sync
  across devices has a known shape (Actual Budget's CRDT log).
- **Edited on the page and saved**, through a small local server started with a double-click,
  later wrapped as a desktop app (Tauri). Every write goes through one module that checks it,
  dates it with its reason and rebuilds; the page, `confirm.py` and any later bank connection
  all use it.
- **What stays files**: `inbox/` and `archive/` (the original statements), and the demo and
  fixtures in the repository, kept as text and loaded into a database when built, so a pull
  request still shows what changed and the privacy guard still reads every line.
- **The checkers follow.** check_data keeps the rules that span tables (a balance chain closes,
  a fund never claims more than its account) and reads them from the database; the selftest
  plants its faults there. A migration moves an existing workspace's `findata/` in, user 001's
  included, and proves the figures are unchanged.
- **Decided first**: where the workspace lives. A database inside iCloud Drive can be corrupted
  by a sync in the middle of a write, so the workspace leaves iCloud and gets a backup of its
  own; which, and how it reaches a second computer, is settled before any code.

## Later

- **Without the desktop app.** *(first user)* Today setup and the import need Claude Code on a
  computer. A path for someone on the web or a phone only — statements uploaded, the page built
  in the cloud — has to keep the promise that a statement a parser reads never leaves the
  owner's hands, so it waits until that can be kept. A smaller step toward it: a local app
  opened with a double-click, the page with buttons that answer the import's questions and
  write them back, so answering needs no Claude (PRODUCT.md §6.11). It ends the page being one
  file that opens anywhere, so it waits for friends to show that Claude is where they stop.
- **Updates between imports, from a connection the owner authorises** (to try). Two free
  personal-use routes, each owner bringing their own key: Plaid's Trial plan for banks (real
  data, US and Canada, ten connections; whether a given Canadian bank is on it is unconfirmed)
  and SnapTrade Personal for brokers (Wealthsimple listed). First step: confirm the owner's banks
  are on the Trial list, then a local experiment. The key stays out of `findata/` and out of the
  repository, and statements stay the way in for anyone who does not connect. See
  [`docs/competitors.md`](docs/competitors.md) and PRODUCT.md §9.
