# Roadmap

What is planned for the next releases, and roughly when. Dates are targets, not promises; what
shipped is in [`CHANGELOG.md`](CHANGELOG.md).

Every release goes out the same way: a privacy scan of every changed file and commit message, a
fresh clone that must rebuild to the committed page with every checker clean and every planted
fault caught, then one squashed commit on `main`.

## v1.1 — 2026-11-04

- **Words on a card, everywhere.** Income, Investing, Plan and Records follow the card rules
  (DESIGN.md §5b′) the way Home, the header and Spending already do: a label, one number, at
  most one fact; terms with a Glossary entry, numbers that open their sum. The last `?` marks
  and page subtitles go.
- **A fresh clone checks clean.** The demo's exchange rate is dated, so a clone a few weeks old
  greets its first run with a stale-rate warning. The demo dates it relative to today.
- **The year's stacked bar counts refunds**, so it adds up to the cards above it.
- **Investment income fills its page.**

## v1.2 — 2026-11-24

- **The monthly import as a panel.** Everything to bring this month (statements, broker
  exports, phone screenshots, balances no file carries, open questions), each with the one
  button that moves it forward. Released after it has run through one real import.

## v1.3 — 2026-12-15

- **Government pensions in the drawdown.** CPP and OAS, from the owner's own statement, so the
  plan stops overstating what has to be saved.
- **Chequing, transaction by transaction.** Transfers, fees and e-Transfers one row each, with
  search by merchant and a filter by account.

## v1.4 — January 2027

- **Setup, tested end to end.** A fresh workspace set up the way a new owner would, then
  compared with a real one: what the interview misses becomes the next list.
- **A checker for charts drawn by month**: the months must have an end (DESIGN.md §5f).
- **Charts draw in** the first time they appear (optional).
