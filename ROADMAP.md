# Roadmap

What is planned for the next releases, and roughly when. Dates are targets, not promises; what
shipped is in [`CHANGELOG.md`](CHANGELOG.md).

Every release goes out the same way: a privacy scan of every changed file and commit message, a
fresh clone that must rebuild to the committed page with every checker clean and every planted
fault caught, then a pull request from the release branch, merged as one squashed commit on
`main` (since 2026-10-29), and the live demo redeploys with it.

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
  experiment, the monthly import panel's public release.
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
  button that moves it forward. Released after it has run through one real import.
- **A renamed file is still recognised.** *(first user)* A statement whose spaces and commas
  were turned into underscores on the way in is named the same as the original.
- **An account seen only in payments is offered.** *(first user)* When the statements show money
  moving to or from an account nobody registered, setup asks whether to add it, so a card-only
  owner's net worth is not just the card's debt.
- **A regular e-Transfer may be pay.** *(first user)* When the same amount arrives every month
  from no named sender, the question offers it as income first.
- **Which file is which.** *(first user)* Two statements that share a filename pattern, a card
  and a chequing account, are named for the account the statement prints, so the owner can tell
  them apart in `inbox/` and `archive/`.
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
