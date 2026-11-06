# tests/ — unit tests for the pure modules

The workspace already has three kinds of test, each for a different layer. This folder is the
fourth, and the smallest:

| layer | what proves it | where |
|---|---|---|
| a function's arithmetic (`flows.py`, `loans.py`, `categories.py`, `layout.py`, `clock.py`) | **unit tests, here** — a hand-written input of five lines and the number it must give | `tests/test_*.py` |
| a migration step on a user's data | **golden chain, here** — the demo as each release shipped it (`tests/fixtures/schema<N>/`) is copied, migrated to the tool's schema, reconciled and built | `tests/test_migrate.py` |
| a parser against a real statement shape | fixtures: the demo ledgers rendered back into statements and parsed again | `tools/fixtures.py`, run by the selftest |
| a checker still checks | the selftest plants a fault in a copy and asserts the rule fires | `selftest.py` |
| the page draws for every owner | headless Chromium at four widths | `check_render.py` |

## What a test here is for

One test = **one rule from FINANCE.md, pinned**. The name says the rule; the body is the smallest
input that exercises it. Two kinds:

- **the normal path** — a repayment after the agreed date comes off the loan;
- **the edge** — the repayment dated *on* the agreed day does not (the agreed figure already
  settles that day). An edge test pins a decision, so that when someone changes `<=` to `<` six
  months from now the test says "this was a rule, not a typo".

A test that only proves "the function runs" is not worth its line.

## How far to take it

- Only modules that are **pure** (a dict in, a number out; no files, no findata) and whose
  interface has **stopped moving**. Today: `flows.py`, `loans.py`, `categories.py`, `layout.py`,
  `clock.py` (the last two against a temporary folder, never the real `findata/`).
- `rebuild.py`, `update.py` and the page's JavaScript stay under the selftest and check_render
  until their interfaces settle; the parsers stay under fixtures.
- No coverage number. The measure is: every rule in FINANCE.md §8a/§8b that one of these modules
  implements has one test naming it.
- A behaviour that is known wrong but not yet fixed is still written down, as
  `@unittest.expectedFailure` with the reason — so the gap lives in the suite, not in someone's
  head. When the fix lands the test turns green and the decorator comes off.

## The migration fixtures

`tests/fixtures/schema<N>/findata/` is the demo owner's data as a release left it — never anyone's
real data. One per schema a release shipped, because that is the only schema a real user can be at:
`schema9` (the first public commit) and `schema18` (release 1.0.0). When `SCHEMA` goes up, the
tests need nothing: the chain runs the new step over every fixture, and `CurrentDemo` fails until
`demo.py` writes the new number. When a release ships a new schema, copy its `findata/` in as the
next fixture. The migrated result is not compared to today's demo byte for byte: the demo's own
data changes between releases, and the comparison would fail for reasons that are not the
migration's. What is asserted is that the money reconciles and the page builds.

## Running

Standard library only, no pytest:

    python3 -m unittest discover -s tests -v

`checks.py . --level release` runs the same thing as its first step, and skips it in a workspace
that has no `tests/` folder. `tests/_paths.py` puts the skill script folders on `sys.path`; every
test file starts with `import _paths`.
