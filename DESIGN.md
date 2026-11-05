# DESIGN.md — the dashboard design rules

> This file owns **how the page looks and talks**. It states the rules that hold today; where an
> old habit conflicts with it, this file wins. A rule changes only once the owner has confirmed
> it, and the story of how each one came about — the dates, the measurements, what was there
> before — is in [`CHANGELOG.md`](CHANGELOG.md).

## 1. Brand and language

- Title: **Jade Toad · `<owner>`**, the owner from `findata/register/profile.json`, never typed
  into the markup. In the sidebar it is the product name, **Jade Toad**, with the owner's name in
  small type beneath it.
- Interface language: **English throughout** — labels, buttons, hints, empty states, every page.
- Fifteen fixed spending categories in two groups, in English (FINANCE.md §3a,
  `categories.py`): Housing, Bills · Groceries, Dining, Transport, Shopping, Software & tools, Entertainment,
  Health, Travel, Family & gifts, Cash, Fees & interest, Other · Education. The category name
  *is* the definition; never mix languages in it. Subscription is a mark on a repeating charge,
  not a category.
- **Every word that reaches the page is English.** A field in `findata/` that gets rendered is
  written in English; reasoning in another language goes in a `zh_`-prefixed field the page never
  reads.

## 2. Visual style

- **White cards on a pale ground**: page `#f9f9f7`, cards `#fcfcfb` with a 10px radius and a
  hairline border.
- **Small grey uppercase labels**: every card title is 10.5px, letter-spaced, uppercase, grey.
- **Big numbers**: a statistic is bold, tabular numerals, 23px or more.
- Typeface: the system sans (system-ui / Segoe UI). No serifs, nothing decorative.
- **Light theme only**: the page stays on a white ground whatever the system is set to.
- Month and year switching use **pill selectors**, the selected one black on white.
- **Compact**: card padding 12/15px, grid gap 10px, list rows 3–5.5px apart. Density first, but
  the line height stays readable.

## 3. Colour

- **Every category has its own colour; Other is grey** (2026-10-29, user 001's choice). In stack
  order, bottom up: Groceries `#2a78d6` blue / Dining `#eb6834` orange / Housing `#1baf7a` aqua /
  Shopping `#eda100` yellow / Transport `#e87ba4` magenta / Software & tools `#008300` green /
  Bills `#6250d6` violet / Travel `#e34948` red — the eight dataviz-validated slots in their
  validated order, so no two that touch are hard to tell apart — then Entertainment `#8a5a2b`
  brown / Health `#5bc4d6` cyan / Family & gifts `#c2185b` rose / Cash `#7a8b2e` olive /
  Fees & interest `#1f3f74` navy / Education `#b07ad6` lilac / Other `#a8a69e` grey. Past eight no
  palette keeps every pair apart for a colour-blind reader, so a category's name is always beside
  its colour: in the list, the legend and the tooltip. A legend lists only the categories its
  period has.
- **Colour follows the category, permanently. It is never reassigned by rank or by size.**
- **Income is one blue family** (Payroll `#1c5cab` / Gift `#9ec5f4` / Rewards
  `#4a6fa5`), so income
  and spending read as two domains.
- **The plan's parts do not use the category palette**: Invest blue `#2a78d6` / Everyday orange
  `--c-dining` / Unallocated
  `--pill`; committed payments in `--muted`. Home's net-worth rows use the same semantic set.
- Anything semantic — up or down, good or bad — carries **colour *and* a symbol or arrow**.
  Colour alone is never the signal.

## 4. Page structure

- **One self-contained HTML file**, no external dependencies.
- **Desktop, down to 800px**: `body` is `min-width:800px; max-width:1760px`. Below 1120px one
  `@media` block collapses what would run past the page (2026-11-03, the owner): cards that sit
  side by side stack, a table drops its `.opt` columns (secondary detail the row's hover or another
  page still carries — Accounts' *For*, Holdings' *Accounts* and *Qty*), and a long value in a
  `.meta` row wraps. A new wide table marks its secondary columns `.opt`. **What widens is the charts and the wide tables, not everything**:
  - Stat cards and long text are capped (§5d); charts and wide tables are not.
  - ⚠ **A chart is `width:100%; height:auto`, never a fixed pixel height.** With a `viewBox`,
    `preserveAspectRatio="xMidYMid meet"` and a fixed height, the drawing scales to its height
    and a wider window only adds white space beside it. `check_render.py` measures the painted
    width, not the box.
  - **A chart is drawn at the size it is shown** (`fit(id, h)`): the `viewBox` is the card's
    real width and a height that follows the window's (`h` × window height ÷ 1000, between
    0.72 and 1.1), redrawn when the window changes. A `viewBox` of fixed width scaled up with
    the window — a wide screen got a tall chart and text larger than the page's, and a laptop
    screen got the chart below the fold.
- **One left sidebar** (`aside.side`, 210px, sticky) beside `main.main`, rendered from the `NAV`
  constant. Home sits above the sections under no heading.
  - **A new page is one entry in `NAV` plus one `<section data-pg="key" hidden>`**, nothing
    else; `setPage()` is driven entirely by `NAV`.
  - **Every group is open.** No section folds away; Monthly import is listed like the others. The one
    fold is **Waiting for data**, above the Glossary: a page whose data has not arrived yet
    (`WAITS` — Income without a chequing ledger, Investing and FIRE with nothing invested) is
    listed there with what it waits for, closed by default, and returns to its section by itself
    the day the data arrives. A workspace with only a credit card is then a complete product.
  - **The Glossary is on its own at the foot**, below Monthly import and above the version,
    under no heading: it is a reference for reading the page.
  - **Dots**: `pageFlags()` hangs a 6px dot on a sidebar entry when its page has something on
    it — amber `#c98500` = look at this, red `#d03b3b` = a rule is broken or something is due.
    A new rule is wired into it.
  - The month pills appear only on `PILL_PAGES`, the year pills only on `YEAR_PAGES`.
  - The foot of the sidebar carries the tool version (`VERSION`) in muted 10.5px. MAJOR.MINOR.PATCH,
    by the rule in ROADMAP.md, Version numbers: a patch needs only a sync, a minor also a migration, a
    major a change of technology.
- **One page, one question, one kind of time**: a page follows the month cursor, the year cursor
  or no time at all, never half of each; a thing is judged in one place, and Home only
  summarises.

- **Components** (1.0.1): every stat card is drawn by `StatCard(label, value, line, options)` and
  every plain table by `DataTable(columns, rows, options)`, where one column spec sets a column's
  heading and cells together (text left, numbers right). **Lint rule S10** fails a stat card or a
  hand-aligned table heading written outside them; the two grouped tables not yet moved (Accounts,
  Statements) say so on their line. In 2.0 the two become the component library's Card and Table.

<!-- LINT:PAGES pages=18 sections=4 -->
- **The pages**: 18 pages under 4 sidebar sections, ordered the way someone starting out reads them (1.0.1). **Lint rule S4 checks this table against
  `NAV`**, so changing the navigation means changing this table too — and the page count, the
  sidebar list and the minimum width stated in `README.md`, and every path the README hands the
  reader:
  | Section | Pages |
  |---|---|
  | — | Home (four cards, net worth in one card, net worth over time) |
  | Money in & out | This month · Year · Income · Subscriptions · Spending baseline |
  | Plan | Budget · Safety net · FIRE · Drawdown & care |
  | Investing | Portfolio · Performance · Holdings · Investment income |
  | — | Accounts |
  | Monthly import | Updates · Statements |
  | — | Glossary, at the foot of the sidebar, under the pages still waiting for their data |

  **What a page waits for** (`WAITS`): Income and Safety net a chequing statement; Portfolio,
  Performance and Holdings a broker's holdings; Investment income a broker's activity; FIRE a FIRE
  goal; Drawdown & care a FIRE goal and something invested. A page that waits is folded under
  *Waiting for data*, saying what it waits for, and comes back by itself.

### Home

- **Follows no time**: in neither `PILL_PAGES` nor `YEAR_PAGES`. Home answers *where do I stand
  now*; everything by month lives in Spending and Income.
- **No list of things to do on Home** (taken off 2026-10-28 with Rules): what waits for the owner
  is asked in the conversation with Claude at each import, and a page that needs attention
  carries its dot in the sidebar.
- **Each net-worth row opens in place** to the accounts behind it, largest first, each with its
  institution, amount, share of the row, the date of its balance and any currency not the
  home one; the amounts sum to the row. So does *Less what you owe*.
- **Net worth over time** under the net-worth card: one point per month, what really was, nothing
  projected, from two months on. It is not the FIRE chart, which follows the portfolio to a target.
- **Four stat cards**, chosen by two signals, something invested and a FIRE goal (1.0.1). Invested
  with a goal: **Portfolio** (with its dry-powder share), **FIRE progress** (with the on-track
  year), **Invested in \<month\>** (pay-yourself-first, from the broker's record), **Spent in
  \<month\>** (the month's whole spending, bills & housing and everyday beneath it; today's month
  once it has a purchase, otherwise the newest one the statements reach. What is left of Everyday
  is This month's to say, 2026-11-03). Invested, no goal: Portfolio · Invested. A goal, nothing
  invested: FIRE progress. The rest fill from one list, in order, taking only a card with a
  number: Card interest (only when a statement charged some) · Spent in \<month\> · Months covered ·
  Kept this year · A year of subscriptions · Biggest category. So no owner sees an empty card.
- **Net worth in one card, cut both ways at once**: one row per `role`, cash split by where it
  is — For FIRE / Set aside / Cash / Cash in \<abroad\> / Owed to you / Other assets (only for
  things that are not money). Each row's bar is as long as its share and coloured by `reach`
  (Spendable today / Taxed to take out / Promised to a goal / Lent out / In property / Held
  abroad); each `NWPARTS` row carries `by`, its reach split, rounded per piece and settled on the
  largest so the pieces sum to the row. Then total assets, less what you owe, and what is
  reachable today. A row appears only when the register has an item with that value. **Both
  cuts total `NW_GLOBAL`**, and rebuild.py refuses to build otherwise.
- The reach colours layer by **the cost of taking money out**, not by an age it unlocks: a
  Canadian RRSP is not locked, it is taxed.

### Spending

- **This month** — the month on the cursor, all of it: **Everyday** (the headline: the
  everyday less this month's everyday spending, no categories, a track bar with an even-pace
  marker for the current month only); three stat cards (spent, split into the parts that month has, biggest category, against a usual
  month); **Where the paycheque went** (the plan as flows, each marked planned, and titled for the plan rather than the paycheque when it asks for more than take-home; the everyday amount fanning out into that
  month's categories — refunds a source coming in, an overspend a second source from savings, so every band is its real size and the total is Everyday's); the category
  list and the line-by-line of the chosen category.
- **Year** — the year pills, the yearly stat cards, "What stands out" and the year by category
  side by side, the monthly stacked chart, and **Everyday, month by month** (everyday spending against
  today's everyday amount, the overspend in red, the open month faded).
- **Subscriptions** follows no time.
- No transactions page: a month's purchases are reached through a category on This month.

### Income

- **Follows the year only**: Income / Spent / Kept, the year by source — Investment and Rewards
  (a card's cash back) carry their explanation, since neither reaches chequing — a line for what
  a borrower paid back, which is never income, and the months by source.
- **Every row in chequing** (1.0.1), under them: each typed ledger row of the year — transfers,
  fees and e-Transfers one row each, newest first, sixty at a time — with a search that reads the
  label and the bank's own words, and one pill per account when there is more than one.
- **Investment income**: what was paid, a month on average, its share of spending, the tax
  withheld; the months, each split into dividends, interest, lending and tax; and **By holding**
  — which funds paid the dividends, how often each pays (every month, every quarter), and its
  share — because the months swing with the funds' rhythms.

### Investing

- **The headline number is Portfolio**, money that is actually invested: the `grow` accounts. It
  is the group's only denominator; dry powder is measured on its home-currency part, and holdings
  in other currencies are listed separately.
- **Portfolio**: the stat cards, the three ways the portfolio splits, and the exchange-rate card
  that goes with the by-currency split.
- **Performance**: *Against \<benchmark\>* — the same money bought into the fund `rules.json`
  `benchmark` names, on the days it actually went in, drawn as that fund's daily line against the
  growth accounts' snapshots, dashed marks where money moved; three stat cards (your growth
  accounts, the same money in the fund, the difference); under a year of history, a note that it
  is too short to judge. Then *What you put in, and what the market added*.
- **Holdings**: every position, by role or by account; the Accounts column is always visible.
  A fund held in another currency shows that amount beside its home-currency value.
- **No Rules page, and no rule judged anywhere** (taken off 2026-10-28, until the basics are
  finished). `rules.json` still carries the buckets, the band and the principles; the page shows
  the dry-powder share as a number, with no band, mark or dot, and the old link to Rules opens
  Portfolio.
- Money held in another currency is not a page: its accounts are a card on **Accounts**, its
  funds are rows in **Holdings**.

### Plan

- **Safety net** (1.0.1): three cards — Months covered, The money, What a month costs — each
  opening its sum, then where the money is and what is owed on no asset. No band, colour or
  target; money abroad only in the line under Months covered (FINANCE.md §8d).

- **Budget** follows no time: the plan, no category caps. Below the split, a Funds card appears
  only when the owner has a fund: each one's set-aside amount against its goal, what the plan adds,
  and when that pace reaches the goal.
  - **How each paycheque is split**: one stacked bar cutting take-home into the committed
    payments (one segment each) / Invest / Everyday / Unallocated, with one
    line per part beneath it. Take-home, Invest and Everyday are sums of `funds.json`
    `plan.flows`, derived at load; Unallocated is what nothing names and stays where the
    paycheque landed.
  - Invest and Everyday can be edited on the page (`.bud-edit[data-pk]`, kept in the
    URL hash and localStorage, never written back). Parts that add to more than take-home get a
    `noteBox`.
- **FIRE** answers *when*: the stat cards, the progress bar, the trajectory, and *If you stopped
  adding today* — the age today's money reaches the target alone, with the year and the return
  assumed.
  - **The trajectory**: the portfolio under today's contribution at three real returns, drawn to
    the target's dashed line, each curve stopping where it arrives, the legend giving
    "X.X years · month year". A money y-axis on nice steps; **the x-axis is calendar time**
    (quarters, years or every five years, by span). **Four spans**: 1 year, 5 years, 10 years, and
    To FIRE, the default, which stops just past the month the middle return arrives; the choice is
    kept. A span that does not reach the target says so, and its y-axis fits what it shows.
    The real snapshots are a black line with dots, first in the legend as Actual; the projections
    continue from the current month.
- **Drawdown & care** answers *does it last*: a headline sentence; two sliders (the age you stop
  contributing, the age you start drawing); a three-colour line on an **age** x-axis to 95 (blue
  contributing, green compounding alone, amber drawing down); a list of the portfolio at
  drawdown, the yearly withdrawal, its share and how long it lasts. Then *Would it have lasted?* —
  the same drawdown replayed through every whole stretch of real years since 1928 (`RET_HIST`,
  the portfolio's mix today, real returns): three stats (lasted to the end, worst start or
  closest call, the middle case), one bar per start year (green up = what is left, red down = how
  early it ran out), and a note that this is American history and the stretches overlap. Only
  the years of taking money out are replayed; the first day's pot is the steady path's.
- **Spending baseline**: the planning figure against what is really spent, with a 12-month bar
  chart, the months in the average highlighted, the average of up to twelve usable months a red
  dashed line.

### Accounts, and the Monthly import

- **Accounts sits under Home**, not with the import (2026-11-03): it answers *where is my money*,
  which is net worth opened up, while Updates and Statements answer *is the data in, and what
  did each update change*.

- **No To do page** (taken off 2026-10-28). `tasks.json` and `decisions.json` are still
  written and read by the import; nothing on the page lists them, and an old link opens Updates.
- **Updates**: where an update leaves its trace — three stat cards (last update, files on record,
  updates on file), then one card per update from `findata/history/imports.json`: what changed
  (label, from, to), what was noticed, what was decided without asking, what you were asked.
  **The story of an update lives here and nowhere else; every other page shows a status computed
  today.**
- **Accounts**: one row per place money sits — a bank or broker account, a card, a loan, money
  lent. **A home, a car or anything else that is not money (`role: none`) is not an account**: it
  is on Home under Other assets, and here only in the reconciliation (2026-11-03, the owner).
  Grouped by institution, the biggest first and the biggest account first inside it; each
  institution a band in ink with a gap above it. Four columns: the account (its type and number
  beneath, a long number cut to its last four), what it is for in one line, the date (with the
  year when it is not this year; amber, with its age on hover, past 30 days — never a ⚠, which
  is kept for what is unaccounted for), the balance, the heaviest thing on the row; a balance under a
  dollar is muted. **The balance column is in the home currency throughout**: an institution is
  one figure, and an account held in another currency shows its dollar value with its own amount
  beneath and the rate on hover (§7). **A grouped table taller than the window folds to its group
  rows** — Accounts by institution, Holdings by role or account — each saying how many rows it
  holds ("Wealthsimple ▸ 10 accounts"); a click opens or closes one. Decided the first time the
  table is seen; a short one stays open. The **last row is all accounts in the home currency**,
  and beside it what is owned outside accounts and that the two make the header's net worth (⚠
  when they do not); its explanation states each rate. Money lent is a row like any other; its
  balance opens what was agreed and what has come back. No card for money abroad and none for
  money lent: the table already says both. **What is still unaccounted for sits on its row**
  (2026-11-03, the owner): a ⚠ beside the balance of the account a gap belongs to (`gap` in the
  register), or of a borrower gone quiet, with what, why and how to close it on hover; a gap that
  belongs to no account (`standalone`) is one small line above the table. With none, nothing is
  shown — no card saying all is well. The source is `findata/register/accounts.json`, **a
  register, not a second set of books**.
- **Statements**: the filing grid (§5c), and every source's date.

### Glossary

- At the foot of the sidebar, in no group: every finance term and every coined word (§5b′),
  finance terms first, grouped by letter.
- A concept entry may carry a second layer, **Why it works**: folded under the entry on this
  page only, never in the hover. A few short paragraphs on the reason behind the concept, then
  *What people get wrong*. Like the entry it is the same for anyone — no owner's numbers, no
  advice ("you should"), and no figure that changes by year (a yearly contribution limit), since
  the page would carry it stale. Entries that share one reason share one text.

## 5. Interaction

- Affordances are **shown, not explained**. Clickability is carried by pill states, hover
  backgrounds, and highlighting or dimming; an "everything" state is an All pill, never a "click
  again to show all".
- Charts have hover tooltips (dark bubble, white text), **one fact per line** — break with
  `<br>`, never string them on `·`.
- Legends isolate a single category on click: the selection is highlighted and the rest dim.
- **Explanations** (§5b′): a term with a dotted underline shows its dictionary entry on hover
  and opens the Glossary on click; a tappable number shows its sum. Both use one floating light
  card, clamped to the viewport, closed by clicking away or Esc.
- **There is no `?` mark.** Every explanation is a term or a sum.

## 5a. The top of the page, and the page header

- `body` has **38px** of top margin, 24px sides, 72px bottom; the sidebar is sticky at
  `top:38px`. Content never touches the top of the window.
- **Every page has a `.pghead`**, a 1px rule below it and `margin-bottom:20px`:
  - Left: an **eyebrow** (its section, 10.5px uppercase grey) and the **title at 25px**. No
    line of description under it.
  - Right: **Net worth**, on every page, a tappable sum, and under it **two dates, nothing
    else** — *Complete to* (the oldest of every required source's newest statement: the day all
    accounts are in up to) and *Updated* (the last update). Clicking them opens Statements. What
    is missing is said once, on Statements.
  - **The two rules line up**: the sidebar wordmark and `.pghead` share `--headh:92px` and are
    both fixed-height with a bottom border, so both rules land on the same y on every page.
    Change the variable, never one side of it.
- The top of the sidebar holds only the coin mark and **Jade Toad** with the owner's name
  beneath (it clicks back to Home): flat colour, no gradients or shadows. No data date there —
  freshness belongs to Statements and the sidebar dots.
- **A number in the page header is not repeated in the page**: no page has a Net worth card.
- **Checks never appear on the page.** A page whose checks fail is not built.

## 5b. How copy is written

- ❌ **Never string facts on `·`.** ✅ `·` only between **parallel nouns** — a list of account
  names, a list of tiers — never between sentences.
- **One fact per line**: several data points are label-left / value-right rows (`metaList()`,
  `.meta`), not squeezed into a sentence.
- **Sentences are written as sentences**, with a subject and a full stop:
  `You are 34% of the way to $800,000, on track for Jun 2036.` — not
  `34% of $800,000 · base case (5%) Jun 2036`.
- **Warnings use `noteBox()`** (pale yellow with a `!`), and only for something that needs
  action.
- Plain words over jargon: `after refunds`, not `net of refunds`. A term the page keeps gets a
  Glossary entry.

**The page talks about your money, never about itself.** Lint **S8** scans the page code, not
the owner's own prose in the data:

1. **No first person.** The page never says "I": `Last received`, not `Newest I have`.
2. **Conclusions and actions, not provenance.** How a number was made goes in its sum or on
   Updates, never in a card.
3. **No rule numbers, file names, constant names or account IDs on screen.** A rule is called by
   what it means (`set aside`, not `rule 2`); an account by its name in `accounts.json`.
4. **A status is a status; a report is a report.** A rule on the Investing pages is one line
   computed today, ✓ or how far off. What an update noticed lives on Updates.
5. **A warning ends with what you can do.** `Not filed yet — the Sep 5 statement is ready to
   download.`
6. **Numbers about your money, not the pipeline.** Never `10 of 12 sources fresh`; instead
   `Chequing and savings are older than a month`.
7. **No lecturing.** No `worth knowing`, no `read this as`, no `that is X, not Y`. Your own
   principle may be shown, in one sentence, marked as yours.

The prose fields of `imports.json`, `decisions.json`, `plan.json` and `rules.json` reach the page
too, and the import writes them to the same rules (update-dashboard, Step 7).

## 5b′. Words on a card

A card carries at most three lines of text, and each has one job. Anything that does none of
these jobs is deleted, not shortened.

| line | job | rule |
|---|---|---|
| **label** | names the thing | a noun phrase of at most four words: `Net worth`, `Spent in Oct`. No verb, no sentence, no colon, no "your". |
| **value** | answers it | one number with its unit; `$838 of $1,300` is still one number. |
| **status** | the one fact the value cannot show | optional; at most seven words, one fact, no `·`, never a restatement of the label, never where a number came from. `On track for May 2039`, `Both transfers landed`. |

- **Explanations are never on the card.** A word that needs one is a **term**: dotted underline,
  hover for its entry, click for the Glossary page. A number that needs one is **tappable**:
  hover or tap it for how yours is worked out.
- **A term's entry is a dictionary entry**, the same for anyone: the word, its part of speech,
  one sentence, a formula where there is one, an example in round numbers, *see also*. Never the
  owner's numbers, never a name in another language. Words the page coined (`Set aside`, `Held
  abroad`) get an entry too, saying what they mean on this page — and it does not look like a
  dictionary entry: no part of speech, a gold rule down its side, headed *A word on this page*.
- **A number's explanation is a sum**: the parts as label / value rows, a total line only when
  they add up, then one line of what is in it or left out. It is where the owner's own
  descriptions in `plan.json` appear.
- **One name per thing, everywhere.** The Glossary is the authority: a word that is in it is
  spelled that way on every page (`Set aside`, never `Earmarked`).
- **A summary is a row, not a warning.**
- **Money is written one way**: `$1,300`, `−$61.02` (a real minus, before the dollar sign, never
  `$-61.02`); a date as `Oct 25`.
- **No instructions and no provenance in the text.** Not "Click a category to read it on the
  right", not "Projected from each subscription's own rhythm since your newest statement".
- **No subtitles**, on a card or under a page title.

## 5c. The filing grid

- The first card on Statements is **Filed each month**: one row per source going down, twelve
  months across, a mark when it has been filed.
- Three marks, their meanings in a list below rather than beside the cells:
  - **Filled black dot** = filed for that month
  - **Hollow amber ring** = due, and never arrived
  - **Small grey dot** = not owed yet — the account did not exist that month (`from`), or its
    statement has not closed
- **"Due" is judged by each source's own closing day** (`documents[]` in the register), not by
  the calendar month; a source with no statement uses `IMPORT_DAY`. The current month shows as
  missing only once its closing day has passed.
- The current month's column has a deeper background (`td.now`); the year pills are derived from
  `SUBMITTED`, never written down.
- The "Months in" column gives the count filed, with an amber "missing N" only when something
  is missing.

## 5d. Measured constraints

Each of these is checked by `check_design.py`.

- **Contrast**: `--muted` is `#75736d` (4.62:1 on a card). It carries the 10.5–11.5px label
  text, so recompute the contrast whenever a grey changes.
- **Line width**: long text is capped so a line stays 60–90 characters — `.meta` 720px, `.say`
  820px, `.note-box` 900px, an alert line 880px, sliders 560px.
- **A card is not drawn far outside its content**: a card holding only one capped list gets
  `.tight` (780px).
- **Stat cards are flex**, `flex:1 1 190px; max-width:340px`, never grid `auto-fit` with a
  fixed maximum, which lays its tracks at the maximum and wraps a fourth card.
- **A page is as long as what it has to say.** A short page is not padded and not merged into
  another (2026-10-29: the rule that every page fill a screen was retired; Home is short on
  purpose).

## 5e. Motion — two things only

- **A 120ms fade and 4px rise on page change**, `ease-out`, so a change of page is seen without
  reading the title.
- **Pure CSS**: `section[data-pg]:not([hidden]){animation:pageIn .12s ease-out}`. Toggling
  `hidden` replays it by itself, once per page change — never on a month switch or a slider drag,
  which a class added in JS would also trigger.
- **`prefers-reduced-motion: reduce` turns motion off globally.** An accessibility floor, not an
  option. (Lint L2 forbids only width-based `@media`.)
- **Not done**: numbers that count up (the eye reads the false values on the way), donuts that
  spin in, any looping animation, anything over 500ms.
- **The test**: motion **expresses a change**; it never **performs an entrance**. A curve
  answering a slider live is the first kind.

## 5f. Accumulating years

File size is not the constraint: ten years of ledgers is well under a megabyte and the page still
opens instantly, so data is never split or moved out of the page because there is more of it.
What breaks is **how much fits on one screen**.

- **① The month axis is bounded.** Any chart drawn by month, any selector listing months, gets
  an array **filtered by year** (`MONTHS_IN(viewYear)`) or a **tail window** (`.slice(-N)`).
  Iterating `MONTHS` directly is never allowed.
  - The shape is **year as container, month as cursor**: one row of year pills, always twelve
    month pills (the empty ones `disabled`). The filing grid is the model.
  - `ymLabel()` already appends a short year for a month outside the current year (`Jun ’25`):
    never append it again. `ymFull()` gives "Jun 2026".
- **② A rolling statistic states its window and never means "all of history".** A reference
  value — "typical", a median — takes a tail window (`CAT_WINDOW` closed months) and **says that
  window on screen** ("vs the last 5 closed months"), with the real count when there are fewer.
  The gates compose: `covEnd` first (only months where every card has closed), then the window.

## 6. Restraint in copy

- **No footer disclaimer**, and no long redundant explanatory sentences.
- Explanatory text appears only where it is needed, within one line, in small grey type.

## 7. Principles for presenting data

- **The view starts at a year the owner chooses**; earlier history stays in `findata/` but does
  not enter it.
- Every source is labelled with its own as-of date. Amounts are kept per currency, home
  currency first, and never mixed into a total. **Two exceptions, both explicit conversions
  carrying their rate**: the header Net worth (`NW_GLOBAL`) and the Accounts table, which shows
  every balance, institution and total in the home currency (2026-11-03, the owner: several
  currencies in one column read as a mess), an account held in another currency carrying its own
  amount beneath and its rate on hover. Adding currencies anywhere else is a bug.
- Refunds and negative amounts are shown as green negatives.
- Restraint in labelling chart values: totals on top of bars, amounts in the legend — never a
  number stacked on every data point.
