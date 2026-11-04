# Supported banks and brokers

Which files Jade Toad reads, institution by institution. Every file has to reconcile before it is let in: a statement to the totals it prints, an OFX download to the bank's own balance, a CSV to its balances or to the balance your app shows.

## Which to use

1. **OFX / QFX** — the first choice. One download carries every account at the bank, for the dates you pick, and it checks itself against the bank's balance.
2. **PDF statement** — the most complete: it names who sent an e-Transfer and prints totals to check against. But it is one file per account a month.
3. **CSV** — the last choice. Most carry no balance, so the balance your app shows is asked each month.
4. **Balance only** — when none of these can be read: the total from the app, once a month. It counts in net worth, with no transactions behind it.
5. Whatever you download, pick a **date range**, never "since last download": the bank moves that mark every time you download.

## Banks

| Bank | PDF statement | OFX / QFX | CSV |
|---|:---:|:---:|:---:|
| [RBC](#rbc) | ✓ | ✓ | ✓ |
| [BMO](#bmo) | ✓ | ✓ Chequing, savings, US-dollar accounts · ○ Mastercard | ✓ |
| [TD](#td) | — | ○ | ○ |
| [Scotiabank](#scotiabank) | — | ○ | ○ |
| [CIBC](#cibc) | — | ○ | ○ |
| [Tangerine](#tangerine) | — | ○ | ○ |
| [Simplii](#simplii) | — | — | ○ |
| [EQ Bank](#eq-bank) | — | — | ○ |
| [Any other bank](#any-other-bank) | — | ○ | — |

## Brokers

| Broker | Holdings export | Activities export |
|---|:---:|:---:|
| [Wealthsimple](#wealthsimple) | ✓ | ✓ |
| [Questrade](#questrade) | — | — |
| [Interactive Brokers](#interactive-brokers) | — | — |
| [RBC Direct Investing](#rbc-direct-investing) | — | — |
| [TD Direct Investing](#td-direct-investing) | — | — |
| [BMO InvestorLine](#bmo-investorline) | — | — |
| [CIBC Investor's Edge](#cibc-investors-edge) | — | — |
| [Scotia iTRADE](#scotia-itrade) | — | — |
| [National Bank Direct Brokerage](#national-bank-direct-brokerage) | — | — |
| [Qtrade](#qtrade) | — | — |
| [Any other broker](#any-other-broker) | — | — |

✓ read here from a real file and reconciled · ○ should work, not yet confirmed on a real file · ✗ not read · — no reader here (a PDF statement can still be read by Claude, by hand)

## Banks: how to download each

### RBC

**Recommended**: **OFX**: one download carries every account. If you receive many e-Transfers, use the PDF statement for chequing instead: it names who sent each one, so nothing has to be asked.

- ✓ PDF statement · Chequing, savings, Visa: Online Banking → Statements, one PDF per account a month — Reconciled to the totals each statement prints. The best choice for chequing: it names who sent an e-Transfer.
- ✓ OFX / QFX download · Chequing, savings, Visa: Account Services → Download Transactions → Money, a date range, all accounts in one file — Checks itself against the bank's balance. It does not name who sent an e-Transfer, so each one is asked.
- ✓ CSV download · Chequing, savings, Visa: Download Transactions → Comma Delimited — No balance in the file: the balance your app shows is asked each month. Prefer OFX.

### BMO

**Recommended**: **OFX** for chequing, savings and US-dollar accounts, in one download. The Mastercard is a separate download from the card's own page: the **CSV** (it asks the balance your app shows) or the **PDF statement** (it asks nothing).

- ✓ PDF statement · Chequing, savings, Mastercard: Online Banking → Statements — From October 2026 chequing and savings come as one statement.
- ✓ OFX / QFX download · Chequing, savings, US-dollar accounts: Account → Transactions → Download → .ofx format, between two dates (two months at most) — Checks itself against the bank's balance. The first time, setup asks which account each id in the file is.
- ○ OFX / QFX download · Mastercard: A separate download, from the card's own page → Download → .ofx format
- ✓ CSV download · Chequing, savings, US-dollar accounts: Account → Transactions → Download → .csv format, one account at a time — The file has a section for every account and nothing saying which is which, so a file with rows for more than one is refused. No balance in it: the balance your app shows is asked. Prefer OFX.
- ✓ CSV download · Mastercard: A separate download, from the card's own page → Download → .csv format — No balance in it: the balance your app shows is asked.

### TD

**Recommended**: **OFX** first; the CSV if the OFX will not read.

- ○ OFX / QFX download · Chequing, savings, Visa: EasyWeb → Download transactions → Quicken or Money
- ○ CSV download · Chequing, savings, Visa: EasyWeb → Download transactions → Spreadsheet (accountactivity.csv) — Chequing has a balance column; check against it.

### Scotiabank

**Recommended**: **OFX** first; the CSV if the OFX will not read.

- ○ OFX / QFX download · Chequing, savings, credit cards: Online banking → the account → Download → Quicken (QFX)
- ○ CSV download · Chequing, savings, credit cards: Online banking → the account → Download → CSV — A download stops at 100 rows: get one statement period at a time.

### CIBC

**Recommended**: **OFX** first; the CSV if the OFX will not read.

- ○ OFX / QFX download · Chequing, savings, credit cards: Online banking → Download Transactions → Quicken or Money
- ○ CSV download · Chequing, savings, credit cards: Online banking → Download Transactions → spreadsheet

### Tangerine

**Recommended**: **OFX**, from the website rather than the app; the CSV if it will not read.

- ○ OFX / QFX download · Chequing, savings, credit card: Website (not the app) → the account → Download → QFX or Money
- ○ CSV download · Chequing, savings, credit card: Website → the account → Download → CSV

### Simplii

**Recommended**: **CSV**.

- ○ CSV download · Chequing, savings: Online banking → Download → CSV — Its QFX download has been reported not to open in other programs.

### EQ Bank

**Recommended**: **CSV**; the first time, setup reads its columns with you.

- ○ CSV download · Savings: The account's transactions → the download arrow — Nothing describes its columns: setup reads the first lines with you and maps them.

### Any other bank

**Recommended**: **OFX**, if online banking offers a Money or Quicken download. If not, the **PDF statement**: Claude reads it by hand.

- ○ OFX / QFX download · —: The Money or Quicken choice in online banking — OFX is one standard; a file that does not check itself against its balance is refused, never guessed.

## Brokers: how to export

### Wealthsimple

**Recommended**: **Both CSV exports** each month: holdings and activities. A cash account has no export: its balance is read from the app.

- ✓ Holdings export (CSV) · TFSA, RRSP, FHSA, non-registered, crypto: In the app: the holdings report, as CSV — What each account holds today, at today's prices.
- ✓ Activities export (CSV) · TFSA, RRSP, FHSA, non-registered, crypto: In the app: the activities export, as CSV, a date range — Deposits, buys, sells and dividends; the exchange rate is taken from it too.

### Questrade

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### Interactive Brokers

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### RBC Direct Investing

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### TD Direct Investing

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### BMO InvestorLine

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### CIBC Investor's Edge

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### Scotia iTRADE

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### National Bank Direct Brokerage

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### Qtrade

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

### Any other broker

**Recommended**: No reader yet. **Balance only**: once a month, tell Claude the account's total from the app or website. It counts in net worth; the Investing pages do not show what it holds.

*This page is written from the tool's own table (`parsers/support.py`); a status changes only when a real file has been read.*
