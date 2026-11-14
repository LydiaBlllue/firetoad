# Roadmap

What is coming, said as what you will be able to do. These are aims, not promises; what has
already shipped is in [`CHANGELOG.md`](CHANGELOG.md).

## Next — 1.0.5

- **Setup ends on a finished page.** The few merchants and transfers the first import could not
  file are answered inside the last setup screen, so the first thing you open is complete.
- **Your savings rate, and how many more years of work it means**, on the page with a curve you
  can drag. A first number for anyone, with or without a goal.
- **The same numbers everywhere.** Every figure is worked out once and shown wherever it is
  needed. Nothing you see changes; what follows is built on it.

## 1.1.0

- **What to do next, beside your own numbers.** The things worth understanding on the way —
  an emergency fund, fees, compounding, when to take a pension — set out in order, each in one
  sentence, with a formula or a chart, its source, and where you stand on it today.

## 1.2.0

- **Income that needs no work, of every kind.** Rent from a property, royalties, a pension, an
  annuity: each counts toward the day work becomes optional, beside what your investments can
  pay. The goal becomes "income that needs no work covers your spending", not "the portfolio
  reaches a number"; a property is counted by its rent or by its value, never both.

## In any version, as they are ready

- **More banks and brokers**: TD, Scotiabank, CIBC, Tangerine, Simplii and EQ Bank confirmed on
  real files, and the first brokers beyond Wealthsimple. What is read today:
  [Supported banks and brokers](docs/banks.md).
- **A Windows build**, now that the Mac download is signed (1.0.4).

## 2.0.0

- **A faster page and a sturdier store for your data**, still only on your own computer.
- **Make it yours**: funds you name for what you are saving toward, and big purchases tracked on
  their own if you want them.
- **The dashboard in Chinese.**

## Being considered

- **From the web or a phone.** The app above still needs a computer. A way to use it from the
  web or a phone is considered only if your statements can still stay in your own hands.
- **A connection to your bank or broker that you authorise yourself**, so the page moves between
  two imports.

## Version numbers

Three digits, `MAJOR.MINOR.PATCH`. What moves tells you what an update asks of you:

| to take the new version, your folder needs | the version moves | example |
|---|---|---|
| `python3 tools/sync.py <folder>` only — fixes, wording, the page, a check | **patch**: 1.0.2 → 1.0.3 | a statement layout read correctly |
| `python3 tools/migrate.py <folder>` too — your data changes shape | **minor**: 1.0.x → 1.1.0 | a new field in the account register |
| a new technology | **major**: 1.x → 2.0.0 | the move to a database |

The tag, the version at the foot of the sidebar and the CHANGELOG heading carry the same three
digits. A test version is `-beta.N`. What was built as 1.1, 1.2 and 1.3 was released as **1.0.0**
on 2026-11-03.
