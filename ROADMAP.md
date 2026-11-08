# Roadmap

What is coming, said as what you will be able to do. These are aims, not promises; what has
already shipped is in [`CHANGELOG.md`](CHANGELOG.md).

## Next — 1.0.2

- **Without a Claude plan**: a double-clickable app that opens your folder in your browser —
  the setup as six screens, the month as five steps, in English or Chinese — running the same
  code Claude Code runs, on your computer only. A model is optional and off by default; when
  on, it is asked one thing (which category an unknown merchant is) and answers with a
  suggestion you confirm. Claude Code stays the other way in. Built and on the branch; signed
  for download once there is a developer certificate.
- **More banks and brokers**: TD, Scotiabank, CIBC, Tangerine, Simplii and EQ Bank confirmed on
  real files, and the first brokers beyond Wealthsimple. What is read today:
  [Supported banks and brokers](docs/banks.md).

## 2.0.0

- **Make it yours**: funds you name for what you are saving toward, and big purchases tracked on
  their own if you want them.
- **A faster page and a sturdier store for your data**, still only on your own computer.

## Being considered

- **From the web or a phone.** The app above still needs a computer. A way to use it from the
  web or a phone is considered only if your statements can still stay in your own hands.

## Version numbers

Three digits, `MAJOR.MINOR.PATCH`. What moves tells you what an update asks of you:

| to take the new version, your folder needs | the version moves | example |
|---|---|---|
| `python3 tools/sync.py <folder>` only — fixes, wording, the page, a check | **patch**: 1.0.1 → 1.0.2 | a statement layout read correctly |
| `python3 tools/migrate.py <folder>` too — your data changes shape | **minor**: 1.0.x → 1.1.0 | a new field in the account register |
| a new technology | **major**: 1.x → 2.0.0 | the move to a database |

The tag, the version at the foot of the sidebar and the CHANGELOG heading carry the same three
digits. A test version is `-beta.N`. What was built as 1.1, 1.2 and 1.3 was released as **1.0.0**
on 2026-11-03.
