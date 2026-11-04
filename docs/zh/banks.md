# 支持的银行和文件

Jade Toad 能读哪些银行的哪些文件。每个文件都要先核对通过才收进来：对账单要对上它印的合计，OFX 要对上银行给的余额，CSV 要对上文件里的余额或 app 上的余额。银行提供的话，**优先用 OFX / QFX**；下载时一律选**日期范围**，不要选「上次下载以来」，因为每下载一次银行都会改这个标记。

| 银行 / 券商 | PDF 对账单 | OFX / QFX | CSV |
|---|:---:|:---:|:---:|
| **RBC** | ✓ | ✓ | ✓ |
| **BMO** | ✓ | ✓ 支票、储蓄、美元账户 · ○ Mastercard | ✗ |
| **TD** | — | ○ | ○ |
| **Scotiabank** | — | ○ | ○ |
| **CIBC** | — | ○ | ○ |
| **Tangerine** | — | ○ | ○ |
| **Simplii** | — | — | ○ |
| **EQ Bank** | — | — | ○ |
| **Wealthsimple** | — | — | ✓ |
| **其他银行** | — | ○ | — |

✓ 已用真实文件读过并核对通过 · ○ 应该可用，还没用真实文件确认 · ✗ 不读取 · — 没有现成的读取方式（PDF 对账单仍可由 Claude 手读）

## 每种怎么下载、要注意什么

**RBC**

- ✓ PDF 对账单 · 支票、储蓄、Visa：网银 → Statements，每个账户每月一份 PDF — 按每份对账单印的合计核对。支票账户最好用这个：它写着 e-Transfer 是谁转的。
- ✓ OFX / QFX 下载 · 支票、储蓄、Visa：Account Services → Download Transactions → Money，选日期范围，所有账户一个文件 — 按银行给的余额自己核对。不写 e-Transfer 是谁转的，所以每笔都要问。
- ✓ CSV 下载 · 支票、储蓄、Visa：Download Transactions → Comma Delimited — 文件里没有余额：每月要报一次 app 上的余额。优先用 OFX。

**BMO**

- ✓ PDF 对账单 · 支票、储蓄、Mastercard：网银 → Statements — 2026 年 10 月起支票和储蓄合成一份对账单。
- ✓ OFX / QFX 下载 · 支票、储蓄、美元账户：账户 → Transactions → Download → .ofx 格式，选两个日期之间（最多两个月） — 按银行给的余额自己核对。第一次 setup 会问文件里每个编号对应哪个账户。
- ○ OFX / QFX 下载 · Mastercard：信用卡页面 → Download → .ofx 格式
- ✗ CSV 下载 · 支票、储蓄：一个文件里有几个账户，却没写哪段是哪个账户。请用 OFX。

**TD**

- ○ OFX / QFX 下载 · 支票、储蓄、Visa：EasyWeb → Download transactions → Quicken 或 Money
- ○ CSV 下载 · 支票、储蓄、Visa：EasyWeb → Download transactions → Spreadsheet（accountactivity.csv） — 支票文件有余额列，可以按它核对。

**Scotiabank**

- ○ OFX / QFX 下载 · 支票、储蓄、信用卡：网银 → 账户 → Download → Quicken（QFX）
- ○ CSV 下载 · 支票、储蓄、信用卡：网银 → 账户 → Download → CSV — 一次最多下载 100 行：按账单期分次下载。

**CIBC**

- ○ OFX / QFX 下载 · 支票、储蓄、信用卡：网银 → Download Transactions → Quicken 或 Money
- ○ CSV 下载 · 支票、储蓄、信用卡：网银 → Download Transactions → spreadsheet

**Tangerine**

- ○ OFX / QFX 下载 · 支票、储蓄、信用卡：网页版（不是 app）→ 账户 → Download → QFX 或 Money
- ○ CSV 下载 · 支票、储蓄、信用卡：网页版 → 账户 → Download → CSV

**Simplii**

- ○ CSV 下载 · 支票、储蓄：网银 → Download → CSV — 有人反映它的 QFX 在别的软件里打不开。

**EQ Bank**

- ○ CSV 下载 · 储蓄：账户交易页 → 下载箭头 — 查不到它的列格式：setup 会和你一起看前几行，再起草对应表。

**Wealthsimple**

- ✓ CSV 下载 · TFSA、RRSP、FHSA、非注册、加密：从 App 导出的两个 CSV：持仓报告和活动导出

**其他银行**

- ○ OFX / QFX 下载 · —：网银下载里的 Money 或 Quicken — OFX 是统一标准；对不上自己余额的文件会被拒，不会去猜。

*这一页由工具自己的表（`parsers/support.py`）生成；只有读过真实文件，状态才会改。*
