# Roadmap

What is planned for the next releases, and roughly when. Dates are targets, not promises; what
shipped is in [`CHANGELOG.md`](CHANGELOG.md).

Every release goes out the same way: a privacy scan of every changed file and commit message, a
fresh clone that must rebuild to the committed page with every checker clean and every planted
fault caught, then one squashed commit on `main`.

Items marked *(first user)* came from the first person other than the owner to set the tool up
from scratch: one credit card, nine statements, a cloud session.

## v1.1 — 2026-11-04

- **Your data stays out of a public clone.** *(first user)* Setup adds `findata/` to
  `.gitignore` the moment the data is yours, and a commit carrying real data into a repository
  with a public remote is refused.
- **The first import is already sorted.** *(first user)* A starter map of common Canadian
  merchants suggests a category for each one seen for the first time, and every suggestion is
  confirmed in one table, instead of every purchase waiting as Other.
- **A credit card in credit is read.** *(first user)* A Mastercard statement whose balance ends
  in `CR` reconciles like any other, and the selftest carries one.
- **Words on a card, everywhere.** Income, Investing, Plan and Records follow the card rules
  (DESIGN.md §5b′) the way Home, the header and Spending already do: a label, one number, at
  most one fact; terms with a Glossary entry, numbers that open their sum. The last `?` marks
  and page subtitles go.
- **A fresh clone checks clean.** The demo's exchange rate is dated, so a clone a few weeks old
  greets its first run with a stale-rate warning. The demo dates it relative to today.
- **The year's stacked bar counts refunds**, so it adds up to the cards above it.
- **Investment income fills its page.**

## v1.2 — 2026-11-24 — a first setup that works for someone else

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
- **Setup, tested end to end.** A fresh workspace set up the way a new owner would, then
  compared with a real one: what the interview misses becomes the next list.

## v1.3 — 2026-12-15

- **The monthly import as a panel.** Everything to bring this month (statements, broker
  exports, phone screenshots, balances no file carries, open questions), each with the one
  button that moves it forward. Released after it has run through one real import.
- **A renamed file is still recognised.** *(first user)* A statement whose spaces and commas
  were turned into underscores on the way in is named the same as the original.
- **An account seen only in payments is offered.** *(first user)* When the statements show money
  arriving from an account nobody registered, setup asks whether to add it, so a card-only
  owner's net worth is not just the card's debt.
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
  owner's hands, so it waits until that can be kept.
