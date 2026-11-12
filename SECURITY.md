# Security and privacy

FIRE Toad's promise is that your statements and your numbers never leave your computer. A way
around that promise is the most serious kind of bug it can have.

## What to report

- anything that sends a statement, a balance or a merchant to another machine;
- a way your own data could end up in a commit or a pull request;
- the page loading something from the internet, or running code from a file it reads;
- anything in this repository that looks like a real person's data.

## How to report

Privately, through GitHub: the repository's **Security** tab → **Report a vulnerability**. Only
the maintainer sees the report. Please do not open a public issue for these, and do not include
real statements — describe what happens with made-up numbers.

You will get an answer as soon as possible. This is a one-person project, so there is no fixed
response time, but a privacy problem is fixed before anything else.

## Supported versions

Only the latest release. An older workspace takes a fix with `python3 tools/sync.py <workspace>`.
