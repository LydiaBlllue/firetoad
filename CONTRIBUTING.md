# Contributing

Thank you for trying Jade Toad. It is a small personal project, so the most useful thing you
can send is what happened when you used it.

## Reporting a problem or an idea

Open an issue (the repository's **Issues** tab) and say:

- what you did, and what you expected;
- what you saw instead — the words on the page or the line the checker printed;
- your bank and the kind of statement (chequing, a credit card, a broker's export), if a file
  was involved;
- the version, at the foot of the sidebar.

**Never attach a statement, a screenshot with your numbers, or anything from your `findata/`
folder.** An issue is public. If a statement is read wrong, describe the line's shape with the
numbers changed ("a description on one line, the two amounts alone on the next").

A privacy or security problem goes privately: see [SECURITY.md](SECURITY.md).

## Changing the tool

- Work on the current version branch (the newest `v*` branch), not on `main`: `main` is the
  released tool. Version numbers follow the rule at the top of [ROADMAP.md](ROADMAP.md).
- Read `CLAUDE.md`, then `FINANCE.md` before touching a number and `DESIGN.md` before touching
  the page. The page is built, never edited: change `templates/dashboards/` and run
  `rebuild.py`.
- Before a pull request, every checker is clean and every planted fault is caught:

  ```bash
  python3 .claude/skills/workspace-checks/scripts/check_data.py .
  python3 .claude/skills/workspace-checks/scripts/check_design.py dashboards/finance_dashboard.html
  python3 .claude/skills/workspace-checks/scripts/selftest.py .
  ```

- Test data is the made-up demo owner's. No real name, account number or amount goes into
  code, comments, fixtures or commit messages.
