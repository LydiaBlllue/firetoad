# Banks and files

Which files Jade Toad reads, bank by bank. Every file has to reconcile before it is let in: a statement to the totals it prints, an OFX download to the bank's own balance, a CSV to its balances or to the balance your app shows. **Prefer OFX / QFX** where your bank offers it, and always download a **date range**, never "since last download": the bank moves that mark every time you download.

| Bank | Accounts | File | Status | How to get it | Note |
|---|---|---|---|---|---|
| RBC | Chequing, savings, Visa | PDF statement | ✓ Confirmed on a real file | Online Banking → Statements, one PDF per account a month | Reconciled to the totals each statement prints. The best choice for chequing: it names who sent an e-Transfer. |
| RBC | Chequing, savings, Visa | OFX / QFX download | ✓ Confirmed on a real file | Account Services → Download Transactions → Money, a date range, all accounts in one file | Checks itself against the bank's balance. It does not name who sent an e-Transfer, so each one is asked. |
| RBC | Chequing, savings, Visa | CSV download | ✓ Confirmed on a real file | Download Transactions → Comma Delimited | No balance in the file: the balance your app shows is asked each month. Prefer OFX. |
| BMO | Chequing, savings, Mastercard | PDF statement | ✓ Confirmed on a real file | Online Banking → Statements | From October 2026 chequing and savings come as one statement. |
| BMO | Chequing, savings, US-dollar accounts | OFX / QFX download | ✓ Confirmed on a real file | Account → Transactions → Download → .ofx format, between two dates (two months at most) | Checks itself against the bank's balance. The first time, setup asks which account each id in the file is. |
| BMO | Mastercard | OFX / QFX download | Expected to work (a standard format), not yet seen | The card's page → Download → .ofx format | — |
| BMO | Chequing, savings | CSV download | ✗ Not read | — | Several accounts in one file with nothing saying which is which. Use OFX. |
| TD | Chequing, savings, Visa | OFX / QFX download | Expected to work (a standard format), not yet seen | EasyWeb → Download transactions → Quicken or Money | — |
| TD | Chequing, savings, Visa | CSV download | Layout from others' descriptions, not yet seen | EasyWeb → Download transactions → Spreadsheet (accountactivity.csv) | Chequing has a balance column; check against it. |
| Scotiabank | Chequing, savings, credit cards | OFX / QFX download | Expected to work (a standard format), not yet seen | Online banking → the account → Download → Quicken (QFX) | — |
| Scotiabank | Chequing, savings, credit cards | CSV download | Layout from others' descriptions, not yet seen | Online banking → the account → Download → CSV | A download stops at 100 rows: get one statement period at a time. |
| CIBC | Chequing, savings, credit cards | OFX / QFX download | Expected to work (a standard format), not yet seen | Online banking → Download Transactions → Quicken or Money | — |
| CIBC | Chequing, savings, credit cards | CSV download | Layout from others' descriptions, not yet seen | Online banking → Download Transactions → spreadsheet | — |
| Tangerine | Chequing, savings, credit card | OFX / QFX download | Expected to work (a standard format), not yet seen | Website (not the app) → the account → Download → QFX or Money | — |
| Tangerine | Chequing, savings, credit card | CSV download | Layout from others' descriptions, not yet seen | Website → the account → Download → CSV | — |
| Simplii | Chequing, savings | CSV download | Layout from others' descriptions, not yet seen | Online banking → Download → CSV | Its QFX download has been reported not to open in other programs. |
| EQ Bank | Savings | CSV download | Layout from others' descriptions, not yet seen | The account's transactions → the download arrow | Nothing describes its columns: setup reads the first lines with you and maps them. |
| Wealthsimple | TFSA, RRSP, FHSA, non-registered, crypto | Broker export | ✓ Confirmed on a real file | The holdings report and the activities export | — |
| Any other bank | — | OFX / QFX download | Expected to work (a standard format), not yet seen | The Money or Quicken choice in online banking | OFX is one standard; a file that does not check itself against its balance is refused, never guessed. |

*This page is written from the tool's own table (`parsers/support.py`); a status changes only when a real file has been read.*
