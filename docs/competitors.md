# Competitors — the open-source tools nearby

> A dated survey (2026-10-29), not a spec: what the nearest open-source tools do, and where Jade
> Toad differs. Star counts and feature claims are from that day; only Actual's were read off
> its own repository, the rest come from directories, reviews and forum threads. Re-check before
> quoting one.

## The field

| tool | what it is for | how data gets in | investments / currencies | relation to Jade Toad |
|---|---|---|---|---|
| [**Actual Budget**](https://github.com/actualbudget/actual) (MIT, ~29.8k stars) | envelope budgeting — every dollar given a job in advance | bank sync (region-dependent) or CSV / OFX import | multi-currency **not supported** natively (an experimental workaround with rule templates); investments are not its focus | local-first like this one; it answers "where did this month go", this one answers "does the plan still hold" |
| [**Firefly III**](https://openalternative.co/alternatives/firefly-iii) (AGPL, ~24k stars) | bookkeeping and budgets, with rules and reports | CSV import, bank sync connectors | multi-currency yes; investments weak | a self-hosted server (Docker), closer to double-entry bookkeeping |
| [**Ghostfolio**](https://github.com/ghostfolio/ghostfolio) (AGPL) | investments only — allocation, net worth | trades entered or imported | multi-currency yes | often run beside Firefly III; roughly what the Investing group covers |
| **Sure** (community fork of Maybe Finance) | a net-worth dashboard across banks, stocks and crypto | bank sync | both | Maybe itself is no longer maintained |
| [**Beancount + Fava**](https://beancount.io/compare/beancount-vs-hledger) | plain-text double-entry accounting, with a web UI | import scripts the owner writes | both; Fava draws net worth over time | **the closest in spirit**: plain files, auditable, reconciled. FIRE users compute the target by hand or copy the totals into ProjectionLab |
| LLM statement readers — [Finlytics](https://github.com/DrDonoso/Finlytics), [FiscAI](https://github.com/hansbug/fiscai), [expense-ai](https://github.com/simplynd/expense-ai), [Finsight](https://hn.svelte.dev/item/47306144), [finance_agent](https://tomevault.io/tome/LPDavidbdeb/finance_agent) | an AI model parses PDF statements and categorises them | PDF / image upload | mostly none | the nearest in method. FiscAI reads Alipay and WeChat statements; finance_agent is a Claude Code configuration. All early-stage |

## Where Jade Toad differs

**What most of them lack:**

- **The FIRE plan is the product** — target, progress, the drawdown replay, the late-life care
  rule. Elsewhere a net-worth line is the most there is, and the FIRE arithmetic lives in a
  second tool.
- **Every currency in one figure**, including accounts held outside Canada. Actual cannot.
- **Numbers that reconcile**: balance chains must close, and the selftest plants faults to prove
  the checkers still check. Only Beancount has comparable rigour, and there the owner writes the
  scripts.
- **No bank credentials kept anywhere.**

**What they have and this does not:**

- **A lower entry cost** — install and use, no Claude plan (PRODUCT.md §2 names that price).
- **Daily use** — a phone app, entering a purchase on the spot, automatic bank sync. This is
  monthly by design (PRODUCT.md §9).
- **Community size** — tens of thousands of stars each for Actual and Firefly III.

**Worth borrowing:**

- Actual's payee rules (rename and categorise on import) — compare with `merchants.json`.
- Fava's query language: an arbitrary question answered from the data, where this tool has only
  fixed pages.

## Connecting to Canadian banks (2026-10-29)

- **Canada's open banking** (consumer-driven banking): the law has passed, the Bank of Canada now
  oversees it, phase 1 is read-only, and there is no launch date.
- **Plaid / Flinks production**: cover the big Canadian banks, but sold to companies after review.
- **SimpleFIN** (Actual's North American route): no sign of any Canadian bank.
- **Free for personal use**, each owner bringing their own key:
  [Plaid Trial](https://support.plaid.com/hc/en-us/articles/39994173227159-What-is-the-Plaid-Trial-plan)
  (US and Canadian institutions, real data, ten connections; which Canadian banks are on it is
  not listed) and [SnapTrade Personal](https://snaptrade.com/personal) (brokers; Wealthsimple
  read and trade, Questrade read only). On the roadmap under *Later*, to try.

## Other sources

- [Actual multi-currency docs](https://actualbudget.org/docs/budgeting/multi-currency)
- [Actual Budget review 2026](https://getfinny.app/blog/actual-budget-review-2026)
- [Firefly III alternatives (beancount.io)](https://beancount.io/compare/firefly-iii-alternatives)
- [Self-hosted finance / investment apps thread](https://piefed.jeena.net/post/160691)
- [FIRE in 2026 with Beancount (forum)](https://beancount.io/forum/t/fire-in-2026-why-i-track-50-accounts-with-beancount-instead-of-mint-rip-or-ynab/2528)
- [ProjectionLab vs Empower vs Beancount](https://beancount.io/forum/t/projectionlab-vs-empower-vs-beancount-the-fire-tool-reconciliation-challenge/3228)
- [FIRE tools and apps 2026](https://freenance.io/fire/fire-tools-and-apps/)
