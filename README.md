<p align="right"><b>English</b> · <a href="README.zh.md">中文</a></p>

<p align="center">
  <img src="docs/hero.png" alt="" width="180">
</p>

# Jade Toad

**Your money on one page, for working toward financial independence in Canada.**

**[Open the live demo →](https://lydiablllue.github.io/jade-toad/)** a made-up owner's page,
nothing to install.

Once a month you drop your bank statements into a folder and say *"update dashboards"*. Claude
Code reads them, checks that every statement adds up, files every purchase and rebuilds one HTML
page: what you spent, what you own, how far you are from FIRE. No bank login, no server.

![The Home page](docs/screens/home.png)

## What you need

| | |
|---|---|
| **Claude plan** | Pro, Max, Team or Enterprise. The free plan does not include Claude Code. Nothing else to pay for |
| **Claude desktop app** | On a **Mac or Windows** computer, using its **Code** tab, not Chat. Claude Code comes with it |
| **Python 3 and pypdf** | Setup checks for them and gives you the one command if one is missing |
| **Your statements** | Last month's PDFs. A single credit card is enough to start |
| **A screen** | The page needs a window at least 1120px wide; a phone shows screenshots only |

**Banks.** RBC and BMO statements and Wealthsimple exports are read by a local parser. Any other
bank works too, but Claude reads those statements by hand: slower, and it means Claude sees them.

**Built for Canada.** Canadian dollars, TFSA / RRSP / FHSA, CPP and OAS. Accounts abroad count in
net worth.

## Get started

About twenty minutes.

1. **Install the [Claude desktop app](https://claude.com/download)** and sign in.
2. **Download this folder** (*Code → Download ZIP*) and unzip it anywhere on your computer.
3. **Open the app's Code tab and choose that folder.**
4. **Drop last month's files into `inbox/`**, filenames untouched.
5. **Say "set this up".** It reads your files, drafts your accounts and plan, and asks only what
   the files cannot say. Skip a question and it shows *Not set*, never a made-up number.

## Each month

Download the month's statements into `inbox/` and say **"update dashboards"**. You get a short
report and any questions a program cannot answer, like a merchant it has not seen.

## Your data

- **It stays in the folder on your computer**: plain CSV and JSON, and one HTML page. Back the folder up; there is no other copy.
- **A statement a parser reads never goes to Anthropic.** What Claude does read is the import's
  summary, a merchant it has not seen, and your answers, the way anything you say in Claude Code does.
- **It stays out of git**: setup keeps your data out of commits, and a guard refuses one that would carry it.

## More

- **[How it works](docs/how-it-works.md)**: every page, the monthly run, the folder, and the
  checkers that keep the numbers honest.
<!-- LINT:FAULTS n=59 -->
  Four checkers hold every figure to its source; a selftest plants 59 faults to prove they still catch them.
- **[Roadmap](ROADMAP.md)** and **[Changelog](CHANGELOG.md)**.
- **[What the product is for](PRODUCT.md)**.

<!-- LINT:NAV main=17/5 minwidth=1120 -->
The page is 17 pages in 5 sidebar groups —
Home · Spending · Income · Investing · Plan · Records · Glossary
— desktop only, at least 1120px wide.

MIT licence: see [`LICENSE`](LICENSE).
