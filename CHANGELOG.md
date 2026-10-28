# Changelog

## 1.0 — unreleased

The tool is the repository; every workspace, the author's included, is an instance of it.

- **The dry-powder band is not judged any more** (2026-10-28, with Rules). Home's Portfolio card
  and Portfolio's Dry powder card show the share as a number; the ✓/⚠, the "short of the floor"
  line, the holdings-limit mark and the Portfolio dot in the sidebar are gone. `rules.json` keeps
  the band.

- **One sign for every balance** (2026-10-28, findata schema 10). The register wrote what the
  owner owes as negative; `banks.json` wrote a card's balance as the amount owed, and the build
  turned it back with an absolute value that assumed a card can only be owed. A card paid past
  zero was therefore subtracted from net worth: one $928 in credit lowered it by $928 and put the
  Accounts total $1,857 away from the header. Every file now signs a balance from the owner's
  side — owed is negative, credit positive — the import turns a statement's figure once, and the
  build reads it as written; a card in credit counts as spendable cash. `tools/migrate_9to10.py`
  turns the `debts` in an existing `banks.json`.

- **Home loses its to-do list; Records stays open** (2026-10-28). The owner's call, with Rules:
  "What needs you today" is gone from Home; what waits is on To do, and the sidebar dots still
  mark a page that needs a look. Records no longer folds away at the foot of the sidebar.

- **Records, written to the card rules, and the last `?` goes** (2026-10-28). To do's cards open
  their counts, and a task says when it is due rather than when it was added. Updates puts the
  file count with the files. Accounts names each account's role and reach in the page's own
  words instead of the register's (`grow · today` became *For FIRE*, *Spendable today*), dates
  read `Oct 25`, and the total in dollars opens its conversion; the lines about where balances
  come from and how currencies are kept are gone, as are the yes/no rows under money held abroad
  and under money lent. Statements keeps the import day and how many sources are older than a
  month. With every group moved over, the `?` mark and its code are gone from the page.

- **Rules comes off the page, for now** (2026-10-28). The owner's call: rules done well are hard,
  and the basics come first. The page, its sidebar dot and the rule lines on Home are gone; the
  dry-powder band is still judged on Portfolio and, when it is broken, on Home. `rules.json` keeps
  everything it held, and D26 stands down while no page runs a principle (its planted fault
  goes with it: 55). 18 pages.

- **Plan, written to the card rules** (2026-10-28). Budget's rows lost their `?` marks: Invest,
  Everyday, Big buys, the travel fund, committed payments and Unallocated are terms, and each
  fixed amount opens what it is for. The funds' descriptions moved behind their balances. FIRE's
  three cards open their sums (portfolio over target, target less portfolio, the planning figure
  times 12 times 25). The returns on the trajectory are read from the scenarios rather than
  written out. Drawdown & care and the replay keep their numbers and lose their paragraphs: one
  grey line says every figure is in today's money, one says the history is American and the
  stretches overlap, and a warning box is left only where the plan needs action. Spending
  baseline gets a label, and its comparison rows open their working.

- **The Glossary leaves Records** (2026-10-28). It is a reference for reading the page, not a
  record, so it sits on its own at the foot of the sidebar, below Records and above the version.
  Still 19 pages in 5 groups; S4 now reads every heading-less group in the order a reader sees it.

- **A coined word does not look like a dictionary entry** (2026-10-28). *Bucket*, *Set aside*,
  *Kept* and the rest are this page's own words, not finance terms; their entry drops the part
  of speech and carries a gold rule and the heading *A word on this page*, in the explanation
  and on the Glossary page alike.

- **Investing, written to the card rules** (2026-10-28). Portfolio's four cards lost their `?`
  marks and captions: Portfolio, Set aside, Dry powder and Holdings are terms, and each number
  opens its sum (the accounts, the symbols against the denominator, the band). The US-dollar card
  is three plain rows. Performance's cards say *Growth accounts*, *Same money in* the benchmark
  and *Difference*; the price sources are gone from the page, and the note that a short
  comparison says little is one grey line instead of a warning. What you put in and what the
  market added are terms (*book value*, *unrealized gain*), and the paragraph under them is gone.
  Holdings calls the funds abroad *Held abroad* and a set-aside account *Set aside*; the P&L
  footnote is gone. On Rules, each rule's detail is one sentence, its composition behind the
  number.

- **Income, written to the card rules** (2026-10-28). Income, Spent and Kept each open their
  sum; *Kept* and *Paid back* are terms, and Investment is the Glossary's *investment income*
  rather than a `?`. The coverage line under the chart (ledger date ranges strung on `·`) is
  now only "Oct 2026 is still open" when it is. Investment income's four cards lost their
  explanations to their sums and to *tax withheld*; the months read `Jan`, not `2026-01`; tax
  withheld is no longer green, the colour of money coming back; the source and rate list under
  the table is gone.

- **DESIGN.md holds rules only** (2026-10-28). It states what is true today; how each rule came
  about — the dates, the measurements, what was there before — moved to *How the design rules
  came about* at the end of this file. Rules that described pages long gone (Overview's donuts,
  Month by Month, the Cash flow page, the Insights and Tasks tabs) were dropped, and the ones that
  had drifted from the page were corrected: the sidebar is 210px in five sections, no page has a
  description line, Home is in no pill list.

- **Spending, written to the card rules** (2026-10-28). This month, Year and Subscriptions keep
  a label, a number and at most one fact per card; the long captions (coverage lines, "click a
  category…", how the 30-day list is projected) are gone, and each number opens its sum. What
  stands out names the merchant that takes a quarter of Dining or more, whichever it is, instead
  of one written into the page. Negative money reads `−$61`, never `$-61`. The explanations are
  a light card with a heading, a formula, a labelled example, and a total line on a sum.

- **Words on a card, and a Glossary** (2026-10-28). DESIGN.md §5b′ sets what a card may say: a
  label of at most four words, one number, and at most one fact under it; no subtitles, on a
  card or under a page title. A word that needs explaining is a term (dotted underline, hover for
  its dictionary entry, click for the new Glossary page under Records); a number that needs
  explaining opens its sum when hovered or tapped. Home and the header are written that way;
  `Earmarked` is `Set aside` everywhere, and the reach cut is Spendable today / Taxed to take
  out / Promised to a goal / Lent out / In property / Held abroad. 19 pages.

- **The header says two dates** (2026-10-27). "Numbers as of Oct 25. Everything is filed and
  nothing is waiting." is now *Complete to* (the day every account is in up to) and *Updated*
  (the last update), each explained behind its `?`. What is missing or waiting is To do's to say.

- **Home: net worth in one card** (2026-10-27). The by-purpose and the by-reach cards were the
  same accounts sliced twice, and the slices nearly coincide. One card shows both now: a row per
  purpose with the accounts it counts, its bar coloured by how easily it can be reached, total
  assets, less what you owe, and one line for what is reachable today.

- **Home says Portfolio** (2026-10-27). Home's first card read *Invested* while the Investing
  page showed the same number as *Portfolio*; one figure, two names. It is Portfolio on both now,
  as it is in FINANCE.md's figures table.

- **To do: one place for what waits on you** (2026-10-27). Three things waited for you on two
  pages, each with its own count: the questions an update left and the checks wanting a decision
  (on Updates), and the open tasks (on Tasks). They are one page now, To do, first in Records,
  with one count and one dot; Tasks is gone (an old link to it opens To do), and Updates keeps
  only the record of each update. The header says "questions" rather than "items", because it
  counts only those. 18 pages.

- **Plan: when, and whether it lasts** (2026-10-27). Coast & care asked two questions: *when do
  you get there* and *does the money last*. The coast sentence (the age today's money reaches the
  target with nothing added) moved to FIRE, under the trajectory; the page is Drawdown & care, and
  gains *Would it have lasted?* — the same drawdown replayed through every whole stretch of real
  years since 1928, mixed like the portfolio is today (`RET_HIST`, from the new
  `findata/ledgers/returns.json`: Damodaran's annual returns and BLS inflation, fetched by
  `prices.py` once a year). It gives how many stretches lasted, the worst start and the middle
  case, and says plainly that this is American history and the stretches overlap. Baseline is
  Spending baseline. The "year you lean hardest" stops once less than a year of spending is left
  (it read 2,090% on a pot of a few dollars). D28 fails a history with a year missing; the
  selftest plants it (56 faults).

- **Performance, against one fund you could have bought instead** (2026-10-27). Investing's
  Overview held what you own and how it did on one page. It is Portfolio now (what you hold, how
  it splits, the US-dollar rate), and Performance is a page of its own: the same money bought
  into the fund `rules.json` `benchmark` names (VT in the demo), on the days it actually went in,
  drawn as that fund's daily line against the growth accounts' snapshots, with the difference and
  — under a year — a note that the span is too short to judge; then what you put in against what
  the market added. The prices (adjusted close, and the Bank of Canada's USD/CAD) are fetched by
  the new `prices.py` into `findata/ledgers/prices.json` when an import needs them, so the page
  still reads nothing at runtime. D27 fails prices for another fund and warns when they stop more
  than a week before the newest snapshot; the selftest plants both (55 faults). 18 pages.

- **Income follows the year** (2026-10-27). The page was "Overview" in the sidebar and half of it
  followed the month cursor, for a donut of two paycheques. It is Income now, on the year alone;
  the year by source carries the two notes the month card had (investment income never reaches
  chequing; what a borrower paid back is not income) and the chart's colours.

- **Spending is what was spent; Budget is the plan** (2026-10-27). Monthly plan held both the
  month (Free to spend, the paycheque flow) and the plan (the split, the funds), so picking a month
  at the top changed half the page, and the allowance was judged on two pages. This month now
  carries the whole month — Free to spend, three stat cards, the paycheque flow, the categories and
  big buys on a card of their own; Year gains "Inside the allowance, month by month"; the plan and
  the funds are Budget, in the Plan group, with no month pills. How the plan is holding is gone:
  its lines were Free to spend, the Rules page's pay-yourself-first and the funds card. The flow
  now draws refunds as a source coming in, so its total is the one Free to spend shows (it dropped
  them before and overstated the month), and a category in it opens the detail pane.

- **Net worth by purpose, defined** (2026-10-27). The rows were Invested / Earmarked / Cash /
  Other assets, with no definition on the page, and "Other assets" had become wherever an account
  with no other role landed — deposits abroad included, though they are cash. The rows are now
  For FIRE, Set aside, Cash, Cash in <abroad>, Owed to you and Other assets (things that are not
  money), each naming the accounts it counts, with its exact definition behind its ?. The
  definitions live in rebuild.py PART_ROWS; a row with no accounts is not shown.

- **Every investing rule on one page** (2026-10-27). The rules were in three places: the high-level
  ones on Overview, the detailed ones on Rules, the dates on Checkpoints. Rules now lists each
  high-level rule as it stands today, the detailed rules filed under it (rules.json notes, `under`),
  and under each of those its dates. The Overview card and the Checkpoints page are gone (17 pages);
  the sidebar's Rules dot carries a passed date too. D26 fails a note filed under a rule no
  principle checks.

- **High-level rules on the Investing overview** (2026-10-27). The card showed only what the page
  happened to compute — the band and the transfers — so the owner's most broken rule never
  appeared on it. rules.json `principles` now lists her rules in her words, each naming a check
  run on today's data: pay yourself first, the dry-powder band, a reason and a date ahead for every
  holding in a named bucket, each holding in the account `placement` says it belongs in, earmarked
  money kept out, money abroad never dry powder (and the holdings cap, where one is set). Without
  `principles` the card shows what it always did. The detailed rules stay on Rules. D26 fails a
  principle naming a check the page lacks, read from the page code.

- **The portfolio is split three ways** (2026-10-26). The Investing overview's one chart was
  "the Canadian side across your buckets", though more than half of that side was in US dollars.
  It is now three donuts of the same portfolio: by currency, by kind of asset, and by the buckets
  the rules are written in (at the broker, where they apply). A holding's kind comes from the
  export's security type — cash, crypto, a precious metal, a single stock — and, for an ETF,
  from rules.json `assetClass`; a fund abroad says it in foreign.json. D25 warns on a holding
  with no kind and fails a kind the page has no slice for.

- **Spending is net of refunds** (2026-10-26). A credit on a card statement that gives back an
  earlier purchase on the same card — or, for an annual-fee or interest credit, a charge the card
  made — is filed by the import as a negative `spending.csv` row in that purchase's category, so
  the month, the categories, the year and the medians are all after refunds. A credit that points
  at nothing (cash back) stays out and is listed for the owner as before. A refund of a big buy
  goes back to the Big buys fund. **D24** holds every negative row to a purchase on the same card,
  in its category, never more than was spent there; FINANCE.md §3c. Before this, every refund the
  import met was dropped and the purchase stayed in spending at full value.

- **Money you lent is in net worth** (2026-10-26). A loan is a register row with `role: owed` and
  `reach: lent`: the amount the borrower owed on an agreed date, less every repayment the ledgers
  show since, plus any further lending (`loans.py`, read by the build, the import and the
  checker). Net worth gains an "Owed to you" row and the reach table a "Lent out" row; the
  Accounts page has a card per borrower — still owed, paid back so far, last repayment — and a
  warning once nothing has come back for six months. Any number of borrowers; an e-Transfer
  naming one is typed `Repayment` coming in and the new type `Lent` going out, never income or
  spending. D19 knows the two new axis values, D23 re-derives each loan. Before this, a loan
  vanished from net worth the day it was made, and only its repayments showed, as a grey line.

- **The product is 玉蟾 · Jade Toad** (2026-09-14). It was Jade Rabbit. The owner wanted a name from
  Chinese myth that is a woman's, an animal's and a goal's at once, and the toad is all three: in the
  earliest telling (《淮南子》) Heng'e reaches the moon and becomes its toad, and 蟾宫折桂 — plucking
  the cassia in the toad palace — is the idiom for reaching a hard goal, which is what a FIRE number
  is. The mark is the Majiayao frog motif (c. 2500 BCE: round head, one spine, four bent limbs,
  three toes) inside a full moon; `docs/logo.svg` is the source, the sidebar coin and `docs/hero.png`
  are drawn from it, and the wordmark is still the one `PRODUCT` constant the page reads, never typed.
  The repository is named `jade-toad` and public since 2026-09-15; the old address redirects.
- `templates/dashboards/` holds the page code with every constant empty. `rebuild.py` builds
  `dashboards/` from the template and `findata/`, and lint **T1** fails if a page is edited in
  place or a template carries data. About twenty constants that used to live only in the HTML —
  the classified chequing rows, the net-worth history, the tasks, the filing grid, the planning
  assumptions, the investment theses and checkpoints — are findata files now.
- `tools/sync.py` pushes the tool into a workspace and touches nothing that is the owner's;
  `tools/demo.py` generates the demo owner's whole `findata/`. The scrub-and-scan release line is
  gone: there is nothing to scrub.
- `OWNER.md`, loaded by `CLAUDE.md`, is where one person's banks, traps and decisions live. The
  three governing documents say nothing about anyone.
- The `setup` skill writes a whole workspace from an interview; the investment page checks one
  thing (`rules.json` buckets against their target bands) and shows the rest as the owner's notes.
- **The page talks about your money, never about itself** (2026-09-10). The owner: "the UI
  language has too much AI in it." Copy that said "I", explained how a number was made, or put
  rule numbers and file names on screen was rewritten; DESIGN.md §5b carries the seven rules and
  lint S8 holds the page code to them.
- `alerts.json` is retired (findata schema 3; `tools/migrate_2to3.py` moves a workspace). Each
  update now appends one record to `imports.json` — the files, what changed, what was noticed,
  what was decided without asking, what the owner was asked — and every item still waiting for
  the owner sits in `decisions.json`. A new **Data → Updates** page renders both; the Portfolio
  page computes its rule status today instead of showing the sentences of one import for months;
  and one sentence under the net worth in the page header says how far the numbers reach, what is
  still missing and how many items are waiting. `profile.json` carries `schema`, and `sync.py`
  refuses to copy a tool that builds a newer shape than the workspace has.
- **Setup starts from the files** (2026-09-12). The first real clone showed the interview was
  about thirty answers typed by hand into a shape only the scaffold knew. Now the owner drops last
  month's files first and `setup/scripts/propose.py` drafts the answers from them: every PDF is
  offered to every parser, the broker exports are recognised by their columns, and the draft
  carries the accounts (bank, product, kind, number, balance, closing day), the monthly files
  (filename pattern, parser, where each lands) and a first plan (take-home from payroll, the
  investing amount from what reached the broker, an allowance from the cards) — with where each
  value came from, and the questions the files cannot answer. On the author's own August files it
  found 15 of 20 accounts and all 9 monthly files; the scaffold refuses a draft while a question
  is open, and the same files become the first import. The parsers now also report the product,
  the holder and the kind printed on a statement. Two scaffold fixes the run exposed: a refused
  setup no longer clears the demo ledgers first, and accounts abroad get a screenshot document so
  preflight can name the screenshots. The selftest drafts a setup from the synthetic statements.
- **The cash-flow rows are derived, and the Cash flow page is gone** (findata schema 9, 2026-09-10).
  `cashflow.json` was the one copy in the workspace nothing re-derived: the monthly income rows
  the Income page reads are sums of the typed ledgers, and are computed at build now
  (`cashflow_rows` in rebuild.py) — a retyped e-Transfer changes the page on the next rebuild
  instead of waiting for someone to rewrite the table. The counterparty (someone repaying a loan)
  is `counterparty` on their ledger's row in the register's `documents[]`, where D10 reads it.
  The Cash flow page itself went at the owner's word — nothing on it was worth a page; the
  pay-yourself-first check lives on Home and Monthly plan, judged on the broker's record. D22
  warns on a cash-flow ledger row with no type, since an untyped row now counts in nothing.
- **A fund's contribution is a flow** (findata schema 8, 2026-09-10). The `monthly` a fund used to
  carry was the one line of the plan not written as a flow; it is a `saving` row with `to: <fund
  key>` now, the page and D13 read it there, and D13 fails a fund that still carries `monthly`.
- **Set aside is an axis, not a list** (findata schema 7, 2026-09-10; `tools/migrate.py` moves a
  workspace through every step it is behind). `rules.json` `exclude.accounts` said the same thing
  as `role: set-aside` in the register; the Investing pages now read the axis and D19 fails a
  rules.json that still carries the list. `value: statement` is defined as "from any evidence the
  owner dropped in", screenshots included (FINANCE.md §8a).
- **findata/ is three folders** (schema 6, 2026-09-10; `tools/migrate_5to6.py` moves a workspace).
  One per layer of the information model, split by who writes the file: `register/` (the owner's
  declarations), `ledgers/` (the facts the import writes), `history/` (what each update leaves
  behind). Nothing inside a file changes; the register still names files bare, and every script
  resolves them through `layout.py`. The folder is still `findata/` (iCloud for Windows drops any
  folder named `data`).
- **Spending reads This month, then Year** (2026-09-10, the redesign's IA). The page that opens
  one month up — by category, with the line-by-line of the chosen slice — comes first and gains
  a fourth card, everyday spending against the allowance; the year page (total, by category,
  month by month, what stands out) comes second. The month is what gets looked at every week.
- **The Insights page is absorbed** (2026-09-10, the redesign's IA). Its lines had three different
  readers: what stood out about the year now sits on the Spending overview and follows the year
  being viewed, how the plan is holding (pay-yourself-first, the allowance, the funds) sits on
  Monthly plan, and the one check that wants a decision — a subscription whose merchant appeared
  once — sits on Updates under "Worth a second look". 20 pages.
- **Statements are read by parsers** (2026-09-10). `.claude/skills/update-dashboard/parsers/`
  holds one module per institution and kind — `rbc_banking`, `rbc_visa`, `bmo_banking`,
  `bmo_mastercard` — and `documents[].parser` in the register names which one reads a file.
  `scripts/parse.py` returns rows signed the ledger's way, dated with the right year, with a
  running balance, and reconciled the way the register says; the sign of a bank row is solved
  from the printed balances rather than guessed from the words. Step 1 of the import runs the
  parser first and reads by hand only what it refuses. `tools/pdfgen.py` writes PDFs from the
  standard library and `tools/fixtures.py` renders the demo's ledgers back into statements in
  the real text shapes, so the selftest holds every parser to 32 synthetic statements plus one
  tampered total it must refuse (38 faults); in an owner's workspace it also runs the parsers
  over every real statement in `archive/`. Needs `pypdf`, optional: without it the import reads
  by hand as before. D14 rejects a parser name the tool does not have.
- **The monthly plan is flows** (findata schema 5, 2026-09-10; `tools/migrate_4to5.py` moves a
  workspace). `funds.json` `plan.flows` holds one row per thing that happens to the paycheque —
  `income`, `committed` (rent, a mortgage, a loan, each with `until`, `afterFire`, `pays` where
  they apply), `saving`, `allowance` — and the take-home, invest and allowance figures are sums
  of them, read from one module (`flows.py`) by the page, rebuild.py and the checkers. The
  Monthly plan bar shows the committed payments first; Unallocated no longer claims to feed the
  funds. `plan.json` `imputedRent` is a committed flow that starts at FIRE, and the Baseline
  page's calibration adds every committed flow that continues after FIRE. Lint D21 looks for each
  committed payment in the ledgers and warns when none moved; selftest plants one (37). The
  setup interview asks what is paid before anything is chosen.
- **Every account row carries five axes** (findata schema 4, 2026-09-10; `tools/migrate_3to4.py`
  moves a workspace). `side` / `role` / `reach` / `value` / `against` replace the net-worth words
  that used to sit in `feeds`, and each total on the page reads exactly one axis: net worth reads
  `side`, the by-purpose card `role`, the reach table `reach` (netting a liability into the row of
  the asset it names), dry powder the rules' symbols inside `grow`. A home is an ordinary row —
  `asset · none · locked · stated` — and so is the mortgage on it. The demo's reach table had
  been dropping "Spoken for" and showing "Across a border $0" whenever there was nothing
  abroad; rows are now present exactly when the register has an item with that value. Lint D19
  rejects an illegal pair and D20 insists a stated balance carries a date; selftest plants both.
  The setup interview asks what each account is for instead of which tag it gets.
- **The information model is written down** (2026-09-10). CLAUDE.md names the five layers
  everything in a workspace sits in — evidence, facts, history, declarations, derived — with one
  writer each, and the rules that follow (one fact per layer, verified copies only, no back-edges,
  access by key, the page reads nothing at runtime). FINANCE.md §8 adopts the target shape for
  the register: a balance item with five axes (`side`, `role`, `reach`, `value`, `against`) and a
  flow with five (`kind`, `amount`, `until`, `afterFire`, `pays`), so a home, a mortgage and a
  fixed payment are ordinary rows. Design only — `rebuild.py` still reads `feeds`; the code lands
  with findata schema 4.
- **One dashboard** (2026-09-10). The investment dashboard was merged into the main page as the
  Investing group — Overview, Holdings, Rules, Checkpoints, Foreign — ending two sidebars, two
  templates and a Portfolio page that repeated the Overview. `rebuild.py --write` removes a built
  `investment_dashboard.html` whose template is gone. Data became **Records**, a secondary group
  closed at the foot of the sidebar; Data sources became **Statements**; the foreign-currency page
  is named by `foreign.json` and hidden when there are no accounts abroad; Coast & drawdown is
  Coast & care.
- **The skill docs are checked the way README is** (2026-09-13). The three SKILL.md files are
  what Claude reads before every import and setup, and nothing checked them: update-dashboard
  still named `dashboards/ly_finance_dashboard.html` and "both dashboards" three days after the
  page became one file, workspace-checks said the selftest plants "fifteen" faults when the table
  held 42, and `docs/pipeline.py` still drew a release step that no longer exists. S4 now resolves
  every path a skill hands the reader, in prose and in its fenced commands; S6 reads a skill's
  `LINT:FAULTS` marker and its prose the way it reads README's; `docs/pipeline.py` takes its
  counts from the code. Two planted faults cover the new checks. The first run found two more
  stale lines: an `inbox/README.txt` the import was told to keep updated, which the register's
  `documents[]` replaced, and the retired mock-up files still named as decision records.
- **README says what leaves the computer** (2026-09-13). "Nothing leaves your computer" was true of
  the files and false of their contents: what Claude reads to do its part — the rows a parser
  pulls out, a statement no parser can read, the owner's answers — goes to Anthropic like anything
  said in Claude Code. The three front doors (README, README.zh, the Chinese guide) now say so.
  Doing better than saying so — a local orchestrator that hands the model only a summary and the
  items needing judgement — is the next step, not this one.
- **The import is one local run** (2026-09-14). `update-dashboard/scripts/update.py` does
  Steps 0–7 of the skill for every file a parser can read — names the files, parses and
  reconciles each statement, files the purchases by merchant, writes the ledgers and the
  register's copies, rebuilds, checks, archives, appends the update record and the queue of
  decisions — and prints a summary, never the rows. What reaches the model is what a program
  cannot decide: a file it could not name or read, a row it could not type, a merchant seen for
  the first time, an e-Transfer with no name on the other side. The selftest strips the newest
  statement of every document out of a copy of the demo, runs the script on the synthetic
  statement, and expects the demo's own rows back, the checkers clean, the rebuild idempotent
  and a second drop to write nothing. The front doors now say what leaves the computer and what
  does not: a statement a parser read never does. Found on the way: the Mastercard fixture
  printed the merchant and the city with no space between them when the merchant was long; and
  the first dry run on a real workspace showed RBC downloads arrive as `20260819.pdf`, a name
  the register cannot match — such a PDF is now offered to every parser and named by the
  account the statement prints, the way setup drafts the register.
- **Who it is for, and which banks come next** (2026-09-15). The owner's call: people in a
  similar situation — a paycheque, accounts at the big five banks, one of the three brokers most
  people use. README says so, and names the parser order: RBC and BMO exist; TD, Scotiabank and
  CIBC next; then Questrade and Interactive Brokers beside Wealthsimple. Until a bank has a
  parser its statements are read by hand, and README says that too.
- **A statement read by eye is transcribed, not written** (2026-09-15). The owner's call: no
  new parsers for now; a bank without one is read by the model. So that path goes through the
  same script: the model hands the rows and the printed totals back as JSON (`update.py --hand`),
  the script reconciles them the way it reconciles a parser's — chain from opening to closing,
  debits and credits against the totals — refuses what does not add up, and files what does
  like everything else. The selftest takes the savings statement's parser away, drops it under
  a name nothing matches, expects the stop, then the demo's own rows back from a transcription,
  and a refusal for one that is ten dollars off.
- **The demo is complete on the day it shows** (2026-09-15). The owner's call: a first visitor
  sees a finished page, not "three statements are still missing". The demo's chequing and
  savings ledgers now run to the Sep 5 statement (the one due on its Sep 8 "today"), the
  documents that started in May or June carry `from` so the grid stops owing months before
  they existed, and the broker exports are filed every month since June. The header reads
  "Everything due has arrived" apart from the two open items, which stay: they are the queue
  the page is for. The unnamed $200 e-Transfer the demo asks about is now a real row in the
  ledger, typed Other income meanwhile, as the record says.

## How the design rules came about

Moved out of DESIGN.md on 2026-10-28, so the rules there can stay short. Newest last.

- **2026-08-11** — The Spending dashboard redesign: DESIGN.md is written from everything the
  owner said that day. White cards on a pale ground, small grey uppercase labels, big numbers,
  the seven English categories and their colours, settled against a published dashboard style
  the owner liked.
- **2026-08-13** — The dashboard shows data from the start of the owner's first full year. FIRE
  gets its own page; the trajectory chart's x-axis is anchored at that year so it does not drift
  across a new year. Income joins the monthly and yearly views in its own blue family. The
  Overview's charts are made symmetrical: income donut left, spending donut right. (Overview was
  later split up; see 2026-09-06.)
- **2026-08-14** — Overview loses its five stat cards. Page subtitles are deleted. "At a
  glance", one status row per tab, goes on Home. A compact layout: tighter padding, gaps and
  rows.
- **2026-08-20** — The investment pages are English too; the one language exception is gone.
  Definitions go in a `?`, one or two sentences — the first version was too long. The headline
  number of the investing pages is Portfolio, money actually invested.
- **2026-09-06** — The big UI review, measured page by page on the owner's 32-inch screen:
  - Desktop only. The page widened from 1280 to 1760px and the narrow-screen block went; what
    widens is the charts and tables, not the cards.
  - Charts lost their fixed heights: a fixed height with a `viewBox` had kept the trend chart at
    940×190 inside a 1434px box. Removing it took the drawing to 1434×290.
  - `--muted` went from `#898781` (3.50:1, below AA) to `#75736d` (4.62:1). A rule status line
    had run 242 characters across 1252px, so long text got caps. A 1306px card wrapped around
    720px of content looked unfinished, so `.tight`. Four stat cards in grid `auto-fit` fitted
    three, so flex.
  - Six pages held under 520px; the direction was to add content that answers the page's own
    question, not to merge pages.
  - Navigation moved from six top tabs, which had wrapped onto two lines, to a left sidebar,
    picked from two mock-ups. Every page got a `.pghead`, 38px of top margin ("the whole thing
    sits too high up"), and a shared `--headh` so the two dividing lines align.
  - The sidebar's `data through` line was deleted: it took the newest date of every source while
    three were past 30 days, reporting the best case as the general one.
  - Copy: no facts strung on `·` ("splitting sentences with dots… is exhausting to read"); one
    fact per line; sentences as sentences; warnings in a box. Eight tooltips were split onto
    lines.
  - The filing grid, in a paper-planner look: dot, ring, grey dot, judged by each statement's
    own closing day.
  - Motion, two things only: a 120ms page fade, and reduced motion honoured. Measured: page
    change fires it once, a month switch or a slider drag never.
  - The Transactions page was deleted: by category covers it. Chequing line by line, search by
    merchant and filter by account went with it, and are on the roadmap.
- **2026-09-07** — The budget is rebuilt as guilt-free spending: the old category caps had
  contradicted the money rules all along. The first version rendered a Chinese sentence from the
  data onto a card, hence `zh_` fields the page never reads. Home drops everything by month. The
  Accounts page is added, because the account list had to be assembled by hand from four files.
  Net worth by purpose and by reach on Home, after the idea of reporting the rings inside one
  net worth from Irene Zhu's 10-Year Wealth Dashboard — layered here by the cost of taking money
  out, since a Canadian RRSP is taxed rather than locked. Accumulating years: the year selector
  had never been read by the Year chart, and three years of test data showed 24 month pills on
  two rows and eighteen labels reading `Aug ’24 2024`; hence year as container, month as cursor,
  and every rolling statistic stating its window.
- **2026-09-08** — The Accounts table gets a total in the home currency, the second of the two
  places currencies are added. The import day moves to the 26th.
- **2026-09-10** — One dashboard: the investment dashboard, a second file with its own sidebar,
  becomes the Investing group. Records becomes a secondary group; Data sources is renamed
  Statements. The Updates page replaces a Rule status list that had shown one import's sentences
  as the state of things for months. Insights is absorbed. The page stops talking about itself
  ("the UI language has too much AI in it"): no first person, no provenance, no rule numbers.
  The header's pipeline strip ("Built · 3 checks ✓ · 10/12 sources fresh") becomes one sentence
  about the numbers.
- **2026-10-26** — Money in another currency stops being a page: its accounts move to Accounts,
  its funds to Holdings.
- **2026-10-27** — The whole-dashboard map: one page, one question, one kind of time. Spending
  becomes This month then Year; Investing gains Performance; Plan becomes FIRE, Drawdown & care
  and Spending baseline; Income follows the year only; every investing rule moves onto Rules.
  To do takes the waiting cards from Updates and the whole Tasks page. Home's two net-worth
  cards become one. The header's sentence becomes two dates ("no filler").
- **2026-10-28** — Words on a card: a label, one number, at most one fact; terms with a dotted
  underline and a Glossary, numbers that open their sum; no subtitles ("every word is designed").

