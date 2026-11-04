# 支持的银行和券商

Jade Toad 能读哪些银行、券商的哪些文件。每个文件都要先核对通过才收进来：对账单要对上它印的合计，OFX 要对上银行给的余额，CSV 要对上文件里的余额或 app 上的余额。

## 用哪种

1. **OFX / QFX**：首选。一次下载包含这家银行所有账户，日期自己选，还会自己对上银行的余额。
2. **PDF 对账单**：信息最全，写着 e-Transfer 是谁转的，印着合计可以核对。但每个账户每月一份。
3. **CSV**：最后选。多数文件没有余额，每月要报一次 app 上的余额。
4. **只记余额**：以上都读不了的时候，每月报一次 app 上的总数。算进净资产，但没有交易明细。
5. 不管下载哪种，都选**日期范围**，不要选「上次下载以来」：每下载一次，银行都会改这个标记。

## 银行

| 银行 | PDF 对账单 | OFX / QFX | CSV |
|---|:---:|:---:|:---:|
| [RBC](#rbc) | ✓ | ✓ | ✓ |
| [BMO](#bmo) | ✓ | ✓ 支票、储蓄、美元账户 · ○ Mastercard | ✗ |
| [TD](#td) | — | ○ | ○ |
| [Scotiabank](#scotiabank) | — | ○ | ○ |
| [CIBC](#cibc) | — | ○ | ○ |
| [Tangerine](#tangerine) | — | ○ | ○ |
| [Simplii](#simplii) | — | — | ○ |
| [EQ Bank](#eq-bank) | — | — | ○ |
| [其他银行](#其他银行) | — | ○ | — |

## 券商

| 券商 | 持仓导出 | 交易记录导出 |
|---|:---:|:---:|
| [Wealthsimple](#wealthsimple) | ✓ | ✓ |
| [Questrade](#questrade) | — | — |
| [Interactive Brokers](#interactive-brokers) | — | — |
| [RBC Direct Investing](#rbc-direct-investing) | — | — |
| [TD Direct Investing](#td-direct-investing) | — | — |
| [BMO InvestorLine](#bmo-investorline) | — | — |
| [CIBC Investor's Edge](#cibc-investors-edge) | — | — |
| [Scotia iTRADE](#scotia-itrade) | — | — |
| [National Bank Direct Brokerage](#national-bank-direct-brokerage) | — | — |
| [Qtrade](#qtrade) | — | — |
| [其他券商](#其他券商) | — | — |

✓ 已用真实文件读过并核对通过 · ○ 应该可用，还没用真实文件确认 · ✗ 不读取 · — 没有现成的读取方式（PDF 对账单仍可由 Claude 手读）

## 银行：每种怎么下载

### RBC

**推荐**：**OFX**：一次下载包含所有账户。如果你常收 e-Transfer，支票账户改用 PDF 对账单：它写着每笔是谁转的，就不用一笔笔回答。

- ✓ PDF 对账单 · 支票、储蓄、Visa：网银 → Statements，每个账户每月一份 PDF — 按每份对账单印的合计核对。支票账户最好用这个：它写着 e-Transfer 是谁转的。
- ✓ OFX / QFX 下载 · 支票、储蓄、Visa：Account Services → Download Transactions → Money，选日期范围，所有账户一个文件 — 按银行给的余额自己核对。不写 e-Transfer 是谁转的，所以每笔都要问。
- ✓ CSV 下载 · 支票、储蓄、Visa：Download Transactions → Comma Delimited — 文件里没有余额：每月要报一次 app 上的余额。优先用 OFX。

### BMO

**推荐**：支票、储蓄、美元账户用 **OFX**，一次下完。Mastercard 先用 **PDF 对账单**，等它的 OFX 确认了再换。

- ✓ PDF 对账单 · 支票、储蓄、Mastercard：网银 → Statements — 2026 年 10 月起支票和储蓄合成一份对账单。
- ✓ OFX / QFX 下载 · 支票、储蓄、美元账户：账户 → Transactions → Download → .ofx 格式，选两个日期之间（最多两个月） — 按银行给的余额自己核对。第一次 setup 会问文件里每个编号对应哪个账户。
- ○ OFX / QFX 下载 · Mastercard：信用卡页面 → Download → .ofx 格式
- ✗ CSV 下载 · 支票、储蓄：一个文件里有几个账户，却没写哪段是哪个账户。请用 OFX。

### TD

**推荐**：先用 **OFX**；读不了再用 CSV。

- ○ OFX / QFX 下载 · 支票、储蓄、Visa：EasyWeb → Download transactions → Quicken 或 Money
- ○ CSV 下载 · 支票、储蓄、Visa：EasyWeb → Download transactions → Spreadsheet（accountactivity.csv） — 支票文件有余额列，可以按它核对。

### Scotiabank

**推荐**：先用 **OFX**；读不了再用 CSV。

- ○ OFX / QFX 下载 · 支票、储蓄、信用卡：网银 → 账户 → Download → Quicken（QFX）
- ○ CSV 下载 · 支票、储蓄、信用卡：网银 → 账户 → Download → CSV — 一次最多下载 100 行：按账单期分次下载。

### CIBC

**推荐**：先用 **OFX**；读不了再用 CSV。

- ○ OFX / QFX 下载 · 支票、储蓄、信用卡：网银 → Download Transactions → Quicken 或 Money
- ○ CSV 下载 · 支票、储蓄、信用卡：网银 → Download Transactions → spreadsheet

### Tangerine

**推荐**：用网页版下载 **OFX**（app 里没有）；读不了再用 CSV。

- ○ OFX / QFX 下载 · 支票、储蓄、信用卡：网页版（不是 app）→ 账户 → Download → QFX 或 Money
- ○ CSV 下载 · 支票、储蓄、信用卡：网页版 → 账户 → Download → CSV

### Simplii

**推荐**：**CSV**。

- ○ CSV 下载 · 支票、储蓄：网银 → Download → CSV — 有人反映它的 QFX 在别的软件里打不开。

### EQ Bank

**推荐**：**CSV**；第一次 setup 会和你一起认它的列。

- ○ CSV 下载 · 储蓄：账户交易页 → 下载箭头 — 查不到它的列格式：setup 会和你一起看前几行，再起草对应表。

### 其他银行

**推荐**：网银里有 Money 或 Quicken 下载，就用 **OFX**。没有的话用 **PDF 对账单**，由 Claude 手读。

- ○ OFX / QFX 下载 · —：网银下载里的 Money 或 Quicken — OFX 是统一标准；对不上自己余额的文件会被拒，不会去猜。

## 券商：怎么导出

### Wealthsimple

**推荐**：每月导出**两个 CSV**：持仓和交易记录。现金账户没有导出文件，余额从 App 里看。

- ✓ 持仓导出（CSV） · TFSA、RRSP、FHSA、非注册、加密：在 App 里导出持仓报告（CSV） — 每个账户现在持有什么、按今天的价格值多少。
- ✓ 交易记录导出（CSV） · TFSA、RRSP、FHSA、非注册、加密：在 App 里导出交易记录（CSV），选日期范围 — 存入、买入、卖出和分红；汇率也从这里取。

### Questrade

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### Interactive Brokers

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### RBC Direct Investing

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### TD Direct Investing

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### BMO InvestorLine

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### CIBC Investor's Edge

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### Scotia iTRADE

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### National Bank Direct Brokerage

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### Qtrade

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

### 其他券商

**推荐**：还没有读取方式。**只记余额**：每月从 App 或网站看一次账户总值，告诉 Claude。它算进净资产，但投资页面看不到它持有什么。

*这一页由工具自己的表（`parsers/support.py`）生成；只有读过真实文件，状态才会改。*
