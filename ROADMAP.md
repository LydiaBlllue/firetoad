# Roadmap

What is coming, said as what you will be able to do, in the order it is planned. These are aims,
not promises; what has already shipped is in [`CHANGELOG.md`](CHANGELOG.md).

FIRE Toad follows four stages: getting started, setting a goal, staying on track, and after
FIRE. Everything below is there to make one of them simpler.

## Next

- **Setup that ends on a finished page.** The purchases and transfers the first import could not
  file are categorized inside the last step of the setup, so the first thing you see afterwards
  is your whole page, with nothing left to go and do elsewhere.
- **Your savings rate, and how many working years it means.** How much of your take-home pay you
  keep, and how long that takes to reach the day work is optional, with a curve you can drag.
  It needs no goal set first: income and spending are enough.
- **More banks and brokers**: TD, Scotiabank, CIBC, Tangerine, Simplii and EQ Bank confirmed on
  real files, and the first brokers beyond Wealthsimple. What is read today:
  [Supported banks and brokers](docs/banks.md).
- **A Windows build**, now that the Mac download is signed.

## After that

- **What to do next, every month.** The ideas behind the page, from an emergency fund to the 4%
  rule to drawing the money down, set in the order you meet them, each with your own number, its
  formula, a chart, and where it comes from. Home says which one is next for you; nothing is a
  lesson to sit through, and what you have already done is ticked from your own data.
- **Income that needs no work, of every kind.** Rent from a property, royalties, a pension, an
  annuity: each counts toward the day work becomes optional, beside what your investments can
  pay, by when it starts, when it ends and whether it keeps up with prices. The goal becomes
  "income that needs no work covers your spending", not "the portfolio reaches a number"; a
  property is counted by its rent or by its value, never both.

## 2.0.0

- **Make it yours**: funds you name for what you are saving toward, and big purchases tracked on
  their own if you want them.
- **The page in Chinese**, as the setup and the monthly import already are.
- **A faster page and a sturdier store for your data**, still only on your own computer.

## Being considered

- **From the web or a phone.** The app still needs a computer. A way to use it from the web or a
  phone is considered only if your statements can still stay in your own hands.

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
