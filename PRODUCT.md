# PRODUCT.md — what Jade Toad is, and why it is shaped this way

> This file owns **the product**: who it is for, what it answers, what it does, the principles every page and
> script is held to, and what it deliberately is not. It states no rule in detail and no figure.
> The rules are elsewhere and win where this file is shorter: the money in
> [`FINANCE.md`](FINANCE.md), the page in [`DESIGN.md`](DESIGN.md), the work in
> [`CLAUDE.md`](CLAUDE.md). What shipped is [`CHANGELOG.md`](CHANGELOG.md); what is next is
> [`ROADMAP.md`](ROADMAP.md).

## 1. The product in one paragraph

One person's money on one page, rebuilt once a month from their own statements and kept honest
by checkers. The owner drops the month's files into a folder; a local script reads them,
reconciles every statement, files every purchase and rebuilds the page; Claude settles only what
a program cannot decide and asks the owner the rest. There is no server, no bank login kept
anywhere and no app: a folder of plain CSV and JSON, and one self-contained HTML file.

## 2. Who it is for

**The target user** (decided 2026-10-28): someone in Canada working toward financial
independence (FIRE — enough invested to live off it), with a paycheque, accounts at a bank the
parsers read, and a broker, who wants to know each month whether the plan still holds. Not
someone who only wants to see where their spending went; tools with a lower entry cost already
do that well, and this one's reason to exist is the plan, the portfolio and numbers that
reconcile.

- **One owner, one workspace.** Not a household ledger and not a service: a workspace is one
  person's folder, and the tool is the repository that folder is an instance of.
- **Several banks, a broker and often money in more than one country**, so no single app shows
  the whole picture.
- **A desktop reader** on a wide screen, once a month and on the days in between when a
  question comes up.
- **Someone who will not type numbers by hand.** Every number comes from a file the owner
  dropped, or from a declaration they made out loud.

### What they have to bring

Claude is what reads, files and asks; without it there is no product. Everything else on the
way in is a cost to remove, not a requirement.

| what | kind | where it stands |
|---|---|---|
| A Claude plan that includes Claude Code | essential — said up front | the price of the product |
| The Claude desktop app | essential for now — no terminal needed | the only way that keeps statements on the owner's computer |
| Git and a GitHub account | to remove | a download of the folder is enough |
| Python and the PDF reader | to remove | setup checks and says what to install (v1.2) |
| A terminal | removed | everything is said to Claude in the desktop app |

### What success looks like

| measure | target |
|---|---|
| From the first statement dropped in to a page worth reading | under 20 minutes |
| Purchases with a category after the first import | most of them, before anyone confirms anything |
| Owners who come back for a second month's import | the one that matters: the tool is monthly, and one use proves nothing |

## 3. The questions it answers

Each sidebar group answers one question; each page under it answers one smaller one (the full
list is README's *Every page*).

| group | the question |
|---|---|
| Home | Where do I stand, and what am I worth? |
| Spending | How much is still free to spend, and where did the money go? |
| Income | What came in, and how much of it did I keep? |
| Investing | What do I hold, and how did it do? |
| Plan | Does the plan hold — each paycheque, the FIRE target, and the years after it? |
| Records | What is waiting for me, what changed, and is everything filed? |

A page that answers no question a person would ask is not added; a page whose question another
page already answers is merged into it.

## 4. Features

What ships today. What is planned is in [`ROADMAP.md`](ROADMAP.md); when each arrived is in
[`CHANGELOG.md`](CHANGELOG.md).

### On the page

| group | features |
|---|---|
| Header | Net worth across every currency, visible from any page; under it two dates — the day every account is complete to, and the last update |
| Home | Net worth in one card, a row per purpose, each bar coloured by how easily the money can be reached · four cards: Portfolio, FIRE progress, this month's investing transfer, Free to spend |
| Spending | Free to spend today, and for how many days · this month by category, each opening its purchases · big buys apart from everyday spending · the year month by month, by category and against the allowance · subscriptions: what repeats, a year's cost, what is due in the next 30 days |
| Income | Income by source and how much of it was kept · investment income — dividends, interest, lending, withholding tax — on its own page |
| Investing | The portfolio by currency, kind of asset and bucket · performance against one benchmark fund bought on the same days · every holding, by role or by account |
| Plan | What each paycheque is for, and what each fund holds · the FIRE target, progress, the year it is reached and coast to FIRE · whether the money lasts, late-life care included, replayed through every stretch of real years since 1928 · the planning figure against what is really spent |
| Records | To do: questions, checks and tasks in one list · Updates: what each import changed, noticed and decided · Accounts: every place money sits, with its balance and date · Statements: which file arrived which month, and what is missing |
| Glossary | Every finance term and every coined word, at the foot of the sidebar in no group; a coined word's entry looks different from a dictionary entry |
| Everywhere | Terms with a dotted underline open their dictionary entry · numbers that need it open their sum · the planning figure and the toggles are tried out in the browser and never written back |

### Behind the page

| feature | what it does |
|---|---|
| Setup | Drafts the accounts, the monthly files and the plan from the first statements dropped in, asks only what the files cannot say, then writes the workspace |
| Fetching statements | Once the owner has signed in to the bank, works out which statements are missing, asks once, downloads them and files them into `inbox/` (RBC, BMO) |
| The monthly import | One local run: names every file and finds duplicates, reads each statement with its parser, refuses one that does not reconcile, files purchases by merchant, rebuilds the page, archives the originals and writes the update record |
| Parsers | RBC chequing and savings, RBC Visa, BMO chequing and savings, BMO Mastercard, and the broker's two exports; a statement no parser reads is transcribed and held to the same reconciliation |
| The To confirm queue | Every new merchant or unnamed transfer gets a default and a question; the answer is filed where it belongs |
| Undo | A failed run puts everything back; a finished one can be taken back whole |
| Prices | The benchmark's daily prices, the Bank of Canada's exchange rate, and yearly returns and inflation since 1928, fetched at each import |
| Money lent | What a borrower still owes, derived from the agreed amount and every repayment since |
| Checkers | Whether the money reconciles, the rules hold, the page is current, the data is clean and the page follows its design; a selftest plants faults to prove each checker still fires |
| Keeping a workspace current | Sync carries a new version of the tool into a workspace without touching the owner's data; migrations move the data one schema at a time; a commit guard refuses the owner's names |
| The demo | A complete synthetic owner, so a fresh clone opens to a full page |

## 5. The month

The product is built around one rhythm, the import day the owner chose.

1. **A reminder** opens the monthly import panel: everything to bring this month, each with the
   one button that moves it forward.
2. **The files arrive** — statements fetched once the owner has signed in to the bank
   themselves, broker exports, screenshots of accounts abroad.
3. **One local run** names, parses, reconciles, files and rebuilds. A file it cannot name stops
   the run; a statement that does not add up is refused.
4. **What a program cannot decide** comes back as a short list: a merchant seen for the first
   time, an e-Transfer with no name on the other side. Each waits on To do with a default
   applied meanwhile.
5. **The page is read.** Updates says what this month changed; the header says how complete the
   numbers are.

Between import days nothing moves on its own. The page is a picture of the last import, and says
which day that was.

## 6. Principles

Every one of these has already been broken once; each line in the three rule files says where.

1. **Trust is built, not claimed.** A statement is let in only if it reconciles; a page is built
   only from the data; checkers re-derive every copy; a selftest plants faults to prove the
   checkers still check. A page whose checks fail is not shown as if it were fine.
2. **Nothing on the page is typed by hand.** Every number is derived from `findata/` at build
   time. The page reads nothing at runtime, so it is one file that opens anywhere.
3. **One fact, one place.** A number lives in one layer and is written by one writer; any copy is
   re-derived and checked. A list written out by hand — of accounts, of files, of pages — is how
   things go stale, so lists are derived from the register.
4. **The register, not the code, knows the owner.** Adding an account, a bank or a loan is an
   edit to the owner's declarations, never a change to the page code. The code names no bank,
   no account and no person.
5. **The page talks about the owner's money, never about itself.** No "I", no rule numbers, no
   file names, no pipeline status. A warning ends with what the owner can do.
6. **Every word is designed.** A card has a label, one number and at most one fact. A term is
   explained by a dictionary entry; a number by its sum. Neither sits on the card.
7. **Show, don't explain.** What can be clicked looks clickable. No instructions, no
   provenance, no subtitles.
8. **The owner decides; the tool defaults and asks.** Anything ambiguous gets a safe default and
   a question, never a guess written as fact. A merchant name is not a sentence and is not read
   for meaning.
9. **Private by construction.** Statements stay in the owner's folder and the import is local.
   The tool's repository holds no one's data; an owner's decisions live only in their own
   `OWNER.md` and `findata/`.

## 7. The model behind the page

Two ideas carry everything, so a new kind of thing needs a row, not new code.

- **A balance item** is every place money sits and everything owed, placed on five axes: which
  side of the balance sheet, what it is for, how easily it can be reached, how its value is
  known, and what a debt is secured against. Each total on the page reads exactly one axis, so
  the two views of net worth — by purpose and by reach — agree by construction. A home, a
  mortgage or money lent to a friend is an ordinary row. (FINANCE.md §8a.)
- **A flow** is every monthly line of the plan: income, committed costs, saving, the allowance,
  each with an amount and, where it applies, an end date and what happens to it after FIRE.
  (FINANCE.md §8b.)

Everything in the workspace sits in one of five layers — evidence, facts, history,
declarations, derived — and the layer decides who may write it and which checker guards it.
(CLAUDE.md, *How information is stored and reached*.)

## 8. How the page speaks

- **Three lines a card**: a label of at most four words, one number, at most one status of at
  most seven words.
- **Terms** carry a dotted underline. Hover shows a dictionary entry — the word, one sentence, a
  formula, an example in round numbers — the same for anyone; click opens the Glossary.
- **Numbers** that need explaining are tappable and show their sum: the parts, then one line of
  what is in or out. This is the only place the owner's own descriptions appear.
- **One name per thing.** The Glossary is the authority for spelling and meaning.
- **English on the page**, whatever language the owner works in with Claude.
- **Restraint.** No footer disclaimer, no lecturing, no filler under the net worth — two dates.

The full rules are DESIGN.md §5b and §5b′.

## 9. What it deliberately is not

- **Not financial advice.** It shows the owner's own rules checked against their own data; it
  recommends nothing.
- **Not connected to any bank.** No credentials are stored or typed by the tool; the owner signs
  in themselves, and statements are files.
- **Not real-time.** It is monthly by design. A number is as of a stated day.
- **Not a budget with category caps.** One allowance, and everything under it is guilt-free.
- **Not mobile, not dark.** Desktop at 1120px and wider, light theme only.
- **Not a mixer of currencies.** Amounts stay per currency; the two converted totals carry
  their rate.
- **Not multi-user.** One owner per workspace; money in the owner's login that is not theirs is
  kept out of every figure.

## 10. Known gaps between this file and the pages

What the principles ask and the page does not do yet. Each is on the roadmap.

- Nothing stops real data being committed to a public clone (principle 9): `findata/` is
  tracked until the owner untracks it by hand. v1.1.
- A first import files every purchase as Other until each merchant is confirmed one by one, so
  the first page a new owner sees is not worth reading. v1.1.
- A setup question skipped becomes a default shown as a fact — income $0 — where principle 8
  asks for a question. v1.2.
- A fresh clone of the demo warns about a stale exchange rate on its first run, which principle
  1 says it should not. v1.1.
- The monthly import panel exists in the owner's workspace only; it ships after one real
  import. v1.3.
