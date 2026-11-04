# Banks and files

Which files Jade Toad reads, bank by bank. Every file has to reconcile before it is let in: a statement to the totals it prints, an OFX download to the bank's own balance, a CSV to its balances or to the balance your app shows. **Prefer OFX / QFX** where your bank offers it, and always download a **date range**, never "since last download": the bank moves that mark every time you download.

| Bank or broker | PDF statement | OFX / QFX | CSV |
|---|:---:|:---:|:---:|
| **RBC** | ✓ | ✓ | ✓ |
| **BMO** | ✓ | ✓ Chequing, savings, US-dollar accounts · ○ Mastercard | ✗ |
| **TD** | — | ○ | ○ |
| **Scotiabank** | — | ○ | ○ |
| **CIBC** | — | ○ | ○ |
| **Tangerine** | — | ○ | ○ |
| **Simplii** | — | — | ○ |
| **EQ Bank** | — | — | ○ |
| **Wealthsimple** | — | — | ✓ |
| **Any other bank** | — | ○ | — |

✓ read here from a real file and reconciled · ○ should work, not yet confirmed on a real file · ✗ not read · — no reader here (a PDF statement can still be read by Claude, by hand)

## How to download each, and what to know

**RBC**

- ✓ PDF statement · Chequing, savings, Visa: Online Banking → Statements, one PDF per account a month — Reconciled to the totals each statement prints. The best choice for chequing: it names who sent an e-Transfer.
- ✓ OFX / QFX download · Chequing, savings, Visa: Account Services → Download Transactions → Money, a date range, all accounts in one file — Checks itself against the bank's balance. It does not name who sent an e-Transfer, so each one is asked.
- ✓ CSV download · Chequing, savings, Visa: Download Transactions → Comma Delimited — No balance in the file: the balance your app shows is asked each month. Prefer OFX.

**BMO**

- ✓ PDF statement · Chequing, savings, Mastercard: Online Banking → Statements — From October 2026 chequing and savings come as one statement.
- ✓ OFX / QFX download · Chequing, savings, US-dollar accounts: Account → Transactions → Download → .ofx format, between two dates (two months at most) — Checks itself against the bank's balance. The first time, setup asks which account each id in the file is.
- ○ OFX / QFX download · Mastercard: The card's page → Download → .ofx format
- ✗ CSV download · Chequing, savings: Several accounts in one file with nothing saying which is which. Use OFX.

**TD**

- ○ OFX / QFX download · Chequing, savings, Visa: EasyWeb → Download transactions → Quicken or Money
- ○ CSV download · Chequing, savings, Visa: EasyWeb → Download transactions → Spreadsheet (accountactivity.csv) — Chequing has a balance column; check against it.

**Scotiabank**

- ○ OFX / QFX download · Chequing, savings, credit cards: Online banking → the account → Download → Quicken (QFX)
- ○ CSV download · Chequing, savings, credit cards: Online banking → the account → Download → CSV — A download stops at 100 rows: get one statement period at a time.

**CIBC**

- ○ OFX / QFX download · Chequing, savings, credit cards: Online banking → Download Transactions → Quicken or Money
- ○ CSV download · Chequing, savings, credit cards: Online banking → Download Transactions → spreadsheet

**Tangerine**

- ○ OFX / QFX download · Chequing, savings, credit card: Website (not the app) → the account → Download → QFX or Money
- ○ CSV download · Chequing, savings, credit card: Website → the account → Download → CSV

**Simplii**

- ○ CSV download · Chequing, savings: Online banking → Download → CSV — Its QFX download has been reported not to open in other programs.

**EQ Bank**

- ○ CSV download · Savings: The account's transactions → the download arrow — Nothing describes its columns: setup reads the first lines with you and maps them.

**Wealthsimple**

- ✓ CSV download · TFSA, RRSP, FHSA, non-registered, crypto: Two CSV exports from the app: the holdings report and the activities export

**Any other bank**

- ○ OFX / QFX download · —: The Money or Quicken choice in online banking — OFX is one standard; a file that does not check itself against its balance is refused, never guessed.

*This page is written from the tool's own table (`parsers/support.py`); a status changes only when a real file has been read.*
