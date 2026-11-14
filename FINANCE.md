# FINANCE.md — the money logic

> This file owns **the money logic**: how the target is computed, how each month is divided, what
> counts as income. `CLAUDE.md` owns how the work is done, `DESIGN.md` owns how the dashboard
> looks, and the owner's own decisions — why these numbers, which account does what — are in
> `OWNER.md`. The figures table below is kept current by `rebuild.py` and checked by D15; the
> prose refers to it and never restates a number.

## 1. The goal: FIRE

<!-- LINT:FIGURES — check_data's D15 verifies this table against the dashboard constants and
     findata/. ⚠ Every current figure is written HERE AND NOWHERE ELSE. The prose refers to the
     table; it never restates a number. Before 2026-09-08 net worth appeared four times in this
     file, two of them still measured against a target abandoned the day before, and nobody
     noticed. A historical figure must say which month it belongs to.
     Column 1 is a stable key; column 2 is the label, in whatever language this file is in. -->

| key | Figure | Value | Source |
|---|---|---|---|
| plan_base | Planning spend | $2,950 /mo | `PLAN_BASE_DEFAULT`, set by hand |
| fire_target | FIRE target | $885,000 | planning spend × 12 × 25 |
| net_worth | Net worth | $65,655 | `INVEST.netWorth` + `FOREIGN_CAD`, all currencies |
| portfolio | Portfolio | $51,290 | `INVEST.portfolio` — the number FIRE is measured on |
| progress | Progress | 5.8% | portfolio ÷ target |
| gap | Gap | $833,710 | target − portfolio |
| invest_monthly | Monthly contribution | $700 | `funds.json` flows: `saving` to the broker |
| everyday | Everyday | $1,500 | `funds.json` flows: `everyday` |
| dry_powder | Dry powder | 16.6% | `INVEST.dryPct`, band 40–45% |
<!-- LINT:FIGURES:END -->

- The target is **planning spend × 12 × 25** (the 4% rule), and progress is measured on the
  **portfolio** — the money that will be drawn down — not on net worth, which also holds
  earmarked accounts, bank cash and money abroad. Planning spend (`plan.json`
  `planBase`) is set by hand; the Baseline page shows the measured average beside it and warns past
  10% of drift, but **never changes the target by itself**.
- **Where these come from.** The 25 is research; the spending figures are this tool's own.
  - Bengen, "Determining Withdrawal Rates Using Historical Data", *Journal of Financial Planning*,
    October 1994: US data from 1926, 50% stocks and 50% intermediate Treasuries, inflation-adjusted
    withdrawals, tax-deferred accounts. 4% never ran out before 33 years; 3 to 3.5% lasted 50.
  - Cooley, Hubbard and Walz (the Trinity study), *AAII Journal*, February 1998: US data, 1926–1995.
  - Pfau, "An International Perspective on Safe Withdrawal Rates", *Journal of Financial Planning*,
    December 2010: 17 countries, 30 years. 4% held in only four of them; Canada was the highest, 4.42%.
  - Anarkulova, Cederburg, O'Doherty and Sias, *Journal of Pension Economics and Finance* 24(3), 2025,
    doi:10.1017/S1474747225000010: 38 developed countries; 2.31% for a couple aged 65 accepting a 5%
    chance of running out.
  - Early Retirement Now, "The Ultimate Guide to Safe Withdrawal Rates", part 1 (2016; a blog, not a
    journal; US data from 1871): a 50/50 portfolio at 4% succeeds 95% of the time over 30 years and
    65% over 60.
  - So 25 fits a retirement of about 30 years and has no margin for a much longer one. The target
    stays × 25 until the owner chooses otherwise.
  - The average of up to twelve months, and adding fixed costs to it, have no outside source:
    they are this tool's calibration of the planning figure.
- Net worth covers every account in every currency: the Canadian side plus foreign-currency
  accounts at the reference rate in `foreign.json`.
- The trajectory chart anchors at `plan.json` `retirement.anchorYear` and projects the three
  scenarios there; the late-life care model (home care, then long-term care tiers) is data in the
  same file.

## 2. Income: in the system

- **Payroll** is what lands in the account whose `feeds` include "Income" (`accounts.json`).
- **Not income**: transfers between your own accounts; a counterparty paying you back (their
  ledger is the register document that carries `counterparty`, and D10 checks that every
  matching e-Transfer is typed Repayment); dividends and interest that stay with the broker.
- **Money from family** (a parent paying toward tuition, support sent from abroad) and other
  gifts are income, on the **Gift** line and never pay. Money that went straight into the broker
  shows in no ledger, and the export cannot say whose it was: the owner declares it in `plan.json`
  `brokerGifts` (date, amount, currency, why, and `counted` when only part of the deposit was
  for the owner), D29 holds each to a deposit in the export, and a US-dollar one counts at today's
  rate. **Government** money (a tax refund, the
  GST/HST credit, a benefit) is counted with Other income. Rent, a bill, cash taken
  out and a bank's fee are money out, never income: they are spending (§3a).
- Investment income (dividends, interest, stock lending, withholding tax) is shown on its own on
  the Income → Investment income page and is not part of the income figure.
- **Rewards** — a card's cash back, points turned into money — are income, on a line of their
  own in the year by source and never pay. The import files a card credit that names cash back
  or a redemption into `rewards.csv` (a fact, tagged with its statement like every row); like
  investment income, it never reaches chequing: it stays on the card.

## 3. The budget method: pay-yourself-first

- The `saving` flow to the broker in `funds.json` goes out each month in **two transfers of half that**,
  before anything else is spent.
- Whether the rule held is judged on the EFTs reaching the broker's chequing account in the
  activities export (`WSDEP`), because they run ahead of the bank statement.

## 3a. What spending is

**Spending is money that leaves and buys nothing you still own — whatever paid it** (2026-10-29,
for someone starting out as much as for someone who invests). A card purchase, a debit purchase, and from chequing: rent,
a bill, a payment to anyone outside the register, cash taken out, a bank's fee or interest
charged, money sent to family. Each is a row in `spending.csv`; a chequing one keeps its ledger
row too (so the chain closes) and is tagged with that account's spending tag, which every chequing
account has; D30 fails a row typed as spending that is not in `spending.csv`. **Not spending**:
money between your own accounts (one abroad included), investing, a card payment, lending, being
repaid, a loan's principal.

- **Fifteen categories in two groups** (`categories.py`, the one definition):

  | group | categories | counts for |
  |---|---|---|
  | bills | Housing, Bills | the spending FIRE is planned on; never the everyday amount |
  | everyday | Groceries, Dining, Transport, Shopping, Software & tools, Entertainment, Health, Travel, Family & gifts, Cash, Fees & interest, Other | the everyday amount, and the spending FIRE is planned on |
  
  The owner may move a category to another group (`plan.json` `categoryGroups`).
- **Spending that ends before FIRE** is a mark on a category, not a kind of spending: `plan.json`
  `notInFire`, Education (tuition, books, exams, credential assessments) by default. It counts like
  any other category today, and is left out of the FIRE target.
- **A merchant is filed once and asked once.** `merchants.json` wins; a merchant it does not know
  takes the starter map's category (`setup/data/starter_merchants.json`: public chains, and words
  that name a kind of business — DENTAL, MASSAGE, PHARMACY) or Other, and is asked. A pharmacy is
  Health, a phone or internet plan Bills. A workspace filed before the fifteen categories has
  every merchant held against the map once (schema 12): a better fit is asked as a suggestion and
  nothing moves until the owner confirms it.
- **A chequing row is filed by its type**: a till purchase and a payment by its payee, looked up
  like any merchant; a bill by its payee too, or Bills (a tax: Housing); rent Housing, cash Cash,
  a fee or charged interest Fees, a fee given back a negative Fees row.
- **A subscription is a mark, not a category.** A charge that repeats — one price to the cent
  in most of the months a merchant is paid, or an amount that holds month to month seven times
  in ten — is marked at build time (`categories.recurring`), whatever it bought; the
  Subscriptions page lists the marked charges. A brand seen once can never be one. A
  Rent, cash and fees are never marked.
- **A bill paid once a year is spread when months are compared.** Insurance for the year, a
  card's annual fee: one large row in one month makes that month look unusual and the others
  cheap. A merchant the owner says is paid once a year (`merchants.json` `every: "year"`), or
  whose charges come back eleven to thirteen months apart within a tenth of the amount, has its
  rows marked at build time (`categories.yearly`), and every comparison between months — a
  usual month, a category's usual, the planning baseline — counts a twelfth of each in the twelve
  months from the one it was paid in. A month's own total and the year's keep it whole. Rent and
  cash are never spread.
- **Money sent to someone nobody named** is a transfer until the owner says otherwise, because a
  program cannot tell a parent from the owner's own account abroad; answered with a category
  (`confirm.py --set N=Family`) it becomes spending.

### A month adds up

Every row of spending is in exactly one part, so the parts always sum to the month's total:

> **spent = bills & housing + everyday**

| part | what is in it | measured against |
|---|---|---|
| bills & housing | the `bills` group | nothing yet |
| everyday | the `everyday` group | the `everyday` flow |

Money that leaves and nobody has named is a transfer, outside the sum, until the owner answers.

**There is one word for each part**, and a part the month does not have is not shown.
The same words are used in the page, this file, the code and the register. A reader is never asked to learn these rules first: the page shows their own
month split, and the definitions wait behind the question mark.

## 3b. Guilt-free spending

The monthly waterfall, from `funds.json`:

1. Invest — the `saving` flow to the broker
2. Everyday — the `everyday` flow; below that line there are no categories and no caps
3. Whatever everyday is left stays where it is

These are the flows of §8b: `saving` and `everyday`. A `committed` flow — rent, a mortgage, a loan — sits above them and is paid before
anything is chosen; `income` is the whole paycheque, before it.


## 3c. Refunds

Spending is counted **net of refunds**. A refund is a fact on a card statement, so it is a row in
`spending.csv` like the purchase it gives back: dated the day it posted, in the statement it came
from, with a **negative** amount and **the purchase's category**. Every total that adds spending
rows up — the month, a category, the year, the average the planning figure is calibrated on — is
therefore after refunds without any of them knowing refunds exist.

- **A refund points at a purchase**: an earlier row on the same card at the same merchant, with
  at least that much not yet refunded. A fee or interest credit (an annual-fee rebate) has no
  merchant; it gives back a charge the card made, so it points at an earlier fee or interest row
  on that card and takes its category. D24 holds every negative row to this.
- **What points at nothing is not a refund.** Cash back is a reward, income (§2). A credit for
  a purchase made before the books begin, or one that points at nothing on the card, the import
  leaves out of spending and lists (`credit not filed`) for the owner. Counting it would lower
  the spending baseline with money that was never spent.
- **A refund lands in the month it posted**, not the month of the purchase, so a category can be
  negative in a month with a large refund and nothing else. The month's total is still exact; a
  chart that stacks categories cannot stack a negative one, so it takes it off the top of the
  month's bar as a hatched band and labels the month with its net — the bars add up to the
  year's total.
- A card payment (`PAYMENT`, `THANK YOU`, a transfer in) is neither spending nor a refund.

## 4. The rhythm

- **Import day** (`profile.json` `importDay`): statements and the broker export go into
  `inbox/`, then say "update dashboards". A scheduled task can remind you that morning and list
  what has arrived and what is missing.
- Each quarter: go through Investing → Rules and Investing → Checkpoints.

## 5. The tool landscape

This workspace is all of it. No budgeting app, no cloud connector; the data exists only in this
folder.

## 6. Naming

The interface and the documents do not call the dashboard a "barbell" (the strategy itself may
still be called that). The categories are fixed and English, fifteen of them (§3a).

## 7. Earmarked accounts

An account whose `role` is `set-aside` in the register is set aside for a purpose — a first
home, an emergency fund. It is outside Portfolio and outside the dry-powder denominator, whatever
it holds, and it shows "—" in the percentage column. It is one value of one axis (§8a); the
`exclude.accounts` list `rules.json` used to carry said the same thing twice and is gone since
findata schema 7.

## 8. The model: balance items and flows

> **Both halves are live**: 8a since findata schema 4, 8b since schema 5 (2026-09-10;
> `tools/migrate_3to4.py` and `tools/migrate_4to5.py` move a workspace). Nothing in this section
> is a figure.

### 8a. A balance item

Every place money sits, and every thing owed, is one row with five axes. Each total the page
shows reads exactly one axis, so a home, a mortgage, a car loan or a pension is an ordinary row
and needs no special case.

| axis | values | what reads it |
|---|---|---|
| `side` | asset · liability | net worth = Σ assets − Σ liabilities, every currency |
| `role` | grow · set-aside · buffer · owed · none | Portfolio, the number FIRE is measured on, is `grow`; net worth by purpose is one slice per role (For FIRE, Set aside, Cash — split into home and abroad —, Owed to you, Other assets); §7's earmarked accounts are `set-aside`; money lent is `owed`; `none` is only for what is not money (a home, a car) |
| `reach` | today · costs · spoken · lent · locked · abroad | the reach table: no gate; taxed on the way out; reachable but spoken for; back only as it is repaid; not liquid; across a border |
| `value` | export · statement · stated | how the balance is known: `export` from a file the broker produced, `statement` from any evidence the owner dropped in — a bank statement, a screenshot of an app, a balance read off it and typed into `banks.json` or `foreign.json` — and `stated` typed by hand with an `asof`, the one value nothing can re-derive |
| `against` | the asset a liability sits on | the reach table shows equity: a home less its mortgage, on the `locked` row |

- **Every balance is signed from the owner's side**, in every file: what she has is positive,
  what she owes is negative. A credit card owing $500 is −500; one paid $90 past zero is +90,
  and counts as spendable cash, because the bank owes her the difference. A statement prints a
  card's balance as the amount owed; the import turns it once, when it writes the file, and
  nothing downstream turns it again.
- A home is `asset · none · locked · stated`. It counts in net worth, not in Portfolio and not in
  dry powder. On the reach cut it is "In property", net of what is secured against it;
  on the by-purpose card it is "Other assets".
- A mortgage is `liability` with `against: home`. A credit card is `liability` with no `against`.
- **Money lent** is `asset · owed · lent · stated`, kind `Lent`, one row per borrower. The owner
  declares `agreed` — what the borrower owed on a date, in the loan's currency (`cur`) — and
  `names`, the names the borrower appears under on a statement. What is owed today is derived:
  the agreed amount, less every ledger row typed `Repayment` that names the borrower after that
  date, plus every row typed `Lent` that does (`loans.py`). The row's `balance` is a copy the
  import writes and D23 re-derives. It counts in net worth ("Owed to you", "Lent out"), not in
  Portfolio, not in dry powder, and a repayment is never income nor a loan spending. Settling
  a new amount with the borrower means a new `agreed`; nothing before it is counted again.
- An account a broker export shows that is not the owner's money — opened in their login for
  someone else — is not a row. It goes in the register's `notOwned` list (`id`, `whose`, `why`,
  `asof`), and every read of a broker export drops it, so it reaches no total, position or
  income figure. An export carrying an account in neither list stops the import until the owner
  says which it is.
- Dry powder is not an axis: `rules.json` names the symbols, counted inside `grow`.
- The two cuts of net worth — by purpose, by reach — read the same rows and agree by
  construction. The assert stays, because `against` netting is new and negative equity is a real
  case.

### 8b. A flow

Every monthly line of the plan is one row with five axes. The waterfall is the flows in kind
order.

| axis | values | what reads it |
|---|---|---|
| `kind` | income · committed · saving · everyday | the waterfall, top down; §3's pay-yourself-first is `saving` placed before `everyday` |
| `amount` | per month, or `null` when never given | the waterfall; `null` counts as nothing and reads *Not set* |
| `starts` | absent, or `fire` | a flow that begins only after FIRE — rent an owner will pay but does not yet — is out of this month's split and inside the planning figure |
| `until` | a date, or open | the FIRE projection drops a flow after its end — a loan paid off |
| `afterFire` | keep · drop | rent keeps, a mortgage payment drops, property tax keeps |
| `pays` | the liability it repays | the principal part is saving, not spending |
| `estimate` | absent, or `true` | one figure for several bills; D21 notes it and does not look for one payment of that size |
| `to` | `broker` (the default), a fund's key, or an account's key | pay-yourself-first counts only the broker |

- **A number never given is `null`, not 0** — take-home, the investing transfer, the everyday amount,
  `plan.json` `planBase` and `profile.json` `born`. The page says *Not set* where it would show
  one, the figures table below says the same, and what is a share of a missing number (the
  target, progress, the drawdown) is not drawn. A $0 that looks like a fact is the failure this
  rule exists for.
- **Unallocated** is income less every other kind. It is a hard constraint: below zero the plan
  does not hold and the page says so in red.
- **Planning spend** is still set by hand and §1's target is still planning spend × 12 × 25.
  The calibration beside it is the measured average of bills, housing and everyday spending (§3a) plus
  every committed flow marked `keep` that spending does not already show: one that starts at
  FIRE, and a repayment (`pays`). Rent or a tax paid today is in spending, so it is not added. What used to be
  `plan.json` `imputedRent` is an ordinary committed flow with `starts: "fire"`.
- **The calibration is an average, not a median.** It covers up to the last twelve usable months, so
  the big months count, which a lifetime of spending also has to pay for. It needs three months,
  and the drift warning reads it. It sets nothing.
- **A fund is the owner's own** (2026-11-03). `funds.json` `funds` is a list, empty or absent
  when there are none. Each has a `key`, a `name`, the `account` (a register key, an asset) whose
  money it is a label on, and optionally a `goal`, a `by` month, a `why`, and `saved` — an amount
  and its `asof`, as the owner says it. What the plan adds is a `saving` flow with `to` naming the
  fund, so it is a line of the split like any other. Nothing is moved into a fund and no
  statement can say what is in one, so `saved` is never advanced by the page: *At this pace* is
  `saved` plus that flow from `asof`, and the owner restates `saved` when it changes. A month's
  leftover goes to no fund by itself. D13 fails a fund on an account the register does not have
  or on a liability, and a saving flow whose `to` is no fund and no account, and warns when what
  is set aside on one account is more than it holds.
- **A committed flow is declared, not observed.** D21 matches each one paid today against the
  ledgers the way the investing transfers are matched against the broker's activities — a
  payment of that size in the two whole months before the newest ledger date — and reports an
  unmatched one.

### 8c. What is deliberately simplified

- **Principal and interest.** Without the loan's own ledger the split is unknown, so a payment
  with `pays` is counted whole as committed.
  Estimating an amortization table would be guessing; bringing the loan statement in as a ledger
  is the honest fix, and it belongs with the parsers.
- **A `stated` value has no evidence behind it.** It is the only number in the workspace nothing
  can re-derive, so it gets its own staleness rule — a home is not stale at thirty days, a car
  is — and FIRE progress stays on Portfolio, which never contains one.
- **`role` is this tool's own vocabulary.** An owner who does not earmark money uses `grow`,
  `buffer` and `none`, and the by-purpose card simply has fewer slices.

Mapping today's `feeds` onto the axes: Portfolio → asset · grow · today (registered retirement
accounts: costs); Earmarked → asset · set-aside · spoken; Bank cash → asset · buffer · today;
Debts → liability; a foreign-currency account → asset · abroad, role per account.

### 8d. The FIRE goal, the Emergency fund and card interest (1.0.1)

- **The FIRE goal is a declaration**: `plan.json` `fire` `{goal, asked}`. Setup asks once, in plain
  words, whether retiring early is something they are working toward; skipped leaves it out. It
  changes by saying so. Never answered reads as yes for someone with money invested, so no page
  an investor had disappears, and as no otherwise; the next import asks once.
- **Emergency fund**, how long the money would last without a paycheque:

  > **months covered = (Spendable today − what is invested in it − what is owed on no asset) ÷ a usual month**

  The money starts from Home's own *Spendable today* row, so the two pages cannot disagree, and
  takes out what in it is invested (a TFSA can be spent today, but it is held to grow). **A usual
  month** = the average of up to twelve full months of spending (the Monthly spending page) + the repayments the plan pays today (active
  committed flows with `pays`, `flows.py` `repayNow`). Rent and bills paid today are in
  `spending.csv` already, so they are not added; `COMMITTED_KEEP` is not used, because it holds
  rent that starts only at FIRE. Money abroad is its own line, never in the headline. Below zero
  is 0; without three closed months the page says so instead of a figure. It judges nothing: no
  band, colour or target. The usual three to six months is the Glossary's *emergency fund*.
- **Card interest** is a fact, never a verdict: the Interest total each card statement prints,
  which the card parsers already read to reconcile, kept one row per statement in
  `card_interest.csv` (0.00 included). Never read off a merchant name. The first import after
  1.0.1 reads it out of every card statement already in `archive/`. It stays spending where the
  statement lists it as a row; the file only says how much was interest. Shown only when there is
  some: Home's first fill card (the last 12 months, split by card), a line in the Year's *What
  stands out*, and an amber dot on Year while the newest statement of any card charged interest.
  No rate is read, and the page never says what to do.
- **Government pensions** in the drawdown: `plan.json` `retirement.pensions`, each
  `{name, monthly, from, asof, source}` — CPP and OAS as the owner's own My Service Canada
  statement estimates them, in today's dollars, said by the owner and never estimated here. From
  the age each starts they pay part of what is taken out (spending and care), so the portfolio
  takes only the rest; a pension that starts before the drawdown does not add to the pot. The FIRE
  target is unchanged: it still has to carry the years before the pensions start.
