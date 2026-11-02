# Jade Toad 是怎么工作的

[README](../../README.zh.md) 背后的细节。

## 每一页

| 分组 | 页面 | 回答什么 |
|---|---|---|
| — | Home | 你现在在哪儿，值多少 |
| Spending | This month | 这个月还能花多少，钱花到哪了 |
| | Year | 这一年按分类、按月怎么样 |
| | Subscriptions | 哪些在重复扣钱、一年多少、下一笔什么时候 |
| Income | Income | 收入从哪来，留下了多少 |
| | Investment income | 不卖任何东西，投资组合付给你多少，哪只持仓什么时候付 |
| Investing | Portfolio | 投了多少，按币种、资产类别、分组怎么分布 |
| | Performance | 和同一天买入一只基准基金相比表现如何 |
| | Holdings | 每个持仓，按角色或按账户 |
| Plan | Budget | 每份工资做什么用，基金里有多少 |
| | FIRE | 离目标还有多远，哪年到 |
| | Drawdown & care | 钱够不够用（含养老护理），历史上多少段真实年份里撑得住 |
| | Spending baseline | 目标所依据的月支出，和实际花了多少 |
| Records | Updates | 每次更新改了什么 |
| | Accounts | 钱放在哪些地方 |
| | Statements | 哪份对账单哪个月到了，还缺什么 |
| — | Glossary | 每个金融术语，以及页面自己起的每个词 |

## 每个月实际怎么走

1. **导入日**（默认每月 26 日；会有提醒列出哪些到了、哪些还缺）。把这个月的对账单下载进 `inbox/`。
   文件名别改 —— 它就是靠文件名认出每个账户的。
2. **说「更新仪表盘」。** 一个本地脚本把这个月做完：动手之前先把每份文件认出来、查重；每份对账单
   由它的解析器读取，必须和对账单自己的合计对平才允许写入；消费按商户归类；页面重建；原件移进
   `archive/`。Claude 只读脚本的摘要，把程序决定不了的事拿来问你 —— 没见过的商户、解析器读不了的
   对账单 —— 然后给你一份简短的报告：变了什么、注意到什么、替你做了哪些判断、哪些要你拍板。
3. **打开页面。** Records → Statements 是一张打卡表，哪个月缺了哪份文件一眼可见。

Emma 每月要丢八份文件：RBC 三份 PDF、BMO 三份 PDF、Wealthsimple 两份导出。你的是你注册表里写的那些。

## 为什么数字可信

页面上每个数字都是从数据文件夹算出来的，没有一个是手打的。四个检查器守着这条线，第五个检查
前四个：

- **钱对不对得上** —— 每本账的余额链闭合，每份对账单和自己的合计对平，还款永远不算收入，
  注册表和它的来源一致。
- **页面是否守着设计规则** —— 图表高度、行宽、对比度、导航和页面对应、这份 README 和真实页面对应。
- **真的画得出来** —— 无头浏览器在三种宽度打开每一页，找没渲染出来的东西。
- **检查器自己还在不在工作** —— selftest 在工作区副本上种下 59 个故障，逐个断言会被抓住。
  它存在是因为有一次检查器 lint 了一个空目录还报了通过。

干净时一声不吭。出了问题就是一条带编号的发现，按出错的种类分组。

<details>
<summary>自己跑一遍</summary>

```bash
python3 .claude/skills/workspace-checks/scripts/check_data.py .
python3 .claude/skills/workspace-checks/scripts/check_design.py dashboards/finance_dashboard.html
python3 .claude/skills/workspace-checks/scripts/check_render.py dashboards/finance_dashboard.html
python3 .claude/skills/workspace-checks/scripts/selftest.py .
```

先跑 `check_data.py`；加 `-v` 列出通过的项。`check_render.py` 需要 Playwright
（`pip3 install --user playwright && python3 -m playwright install chromium`）。
</details>

## 底下是怎么回事

<details>
<summary>文件夹</summary>

```
inbox/        往这里丢新文件，处理完自动移进 archive/
findata/      唯一事实来源，按「谁写它」分三层：
  register/     你的声明 —— 账户、计划、规则、商户
  ledgers/      导入写下的事实 —— 每本账、消费、券商导出
  history/      每次更新留下的记录 —— 更新、决定、归档、快照
dashboards/   造出来的页面（一个自包含的 HTML）
templates/    页面代码，所有数字为空；dashboards/ 由它造出
archive/      处理过的原件，按 <日期>_<来源>_<原名> 归档
docs/         流程图和中文向导
.claude/      三个技能：setup、update-dashboard、workspace-checks
tools/        demo 数据、迁移脚本、同步进工作区
```

文件夹叫 `findata/` 而不是 `data`，是因为 iCloud for Windows 会拒绝同步任何叫 `data` 的文件夹。
这个坑花了一天。
</details>

<details>
<summary>流程图</summary>

![流程](../pipeline.svg)

*可编辑的源文件：[`../pipeline.drawio`](../pipeline.drawio)，由 `../pipeline.py` 生成。*
</details>

<details>
<summary>纲领文件</summary>

| 文件 | 管什么 |
|---|---|
| [`PRODUCT.md`](../../PRODUCT.md) | 产品为谁、回答什么问题、原则，以及刻意不做什么 |
| `CLAUDE.md` | Claude 在这里怎么工作：信息模型、导入、检查器 |
| `FINANCE.md` | 钱的逻辑：FIRE 目标、pay-yourself-first、什么算收入 |
| `DESIGN.md` | 页面长什么样、怎么说话：配色、导航、文案 |
| `OWNER.md` | **你的** —— 你的银行、你踩过的坑、你的决定；另外三份不提任何人 |

它们是规则不是笔记：每一行都是出过问题之后写下的，每次改动前都会被读。口头约定必须落回其中
一份，否则下次会话不作数。

**更详细的中文介绍见 [`docs/zh/guide.md`](docs/zh/guide.md)。**
</details>

<details>
<summary>工具与你的工作区</summary>

这个仓库是工具。你的工作区 —— 那个文件夹，装着你的 `findata/`、`inbox/`、`OWNER.md`
—— 是它的一个实例。`tools/sync.py <workspace>` 把技能、模板和纲领文件复制进去，不碰任何属于你
的东西；工具的数据形状比你的文件夹新时，`tools/migrate.py <workspace>` 会一步一步把文件夹迁上来。

页面共 17 页、5 个侧栏分组 ——
Home · Spending · Income · Investing · Plan · Records · Glossary
—— 仅桌面，窗口至少 1120px 宽。
</details>
