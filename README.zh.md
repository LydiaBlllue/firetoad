<p align="right"><a href="README.md">English</a> · <b>中文</b></p>

<p align="center">
  <img src="docs/hero.png" alt="" width="180">
</p>

# Jade Toad · 玉蟾

**你的钱，一页看完。给在加拿大追求财务自由的人。**

**[打开在线 demo →](https://lydiablllue.github.io/jade-toad/)** 一位虚构用户的页面，什么都不用装。

每个月把银行对账单丢进一个文件夹，说一句 *"更新仪表盘"*。Claude Code 读取它们，核对每份对账单
是否对平，给每笔消费归类，再生成一个 HTML 页面：花了多少、有多少、离 FIRE 还有多远。不用登录银行，
也没有服务器。

![Home 页](docs/screens/home.png)

## 你需要什么

| | |
|---|---|
| **Claude 会员** | Pro、Max、Team 或 Enterprise。免费版不含 Claude Code。除此之外不用再付费 |
| **Claude 桌面应用** | 装在 **Mac 或 Windows** 电脑上，用里面的 **Code** 标签页，不是 Chat。Claude Code 已包含在内 |
| **Python 3 和 pypdf** | setup 会检查，缺什么就给你一条安装命令 |
| **你的对账单** | 上个月的 PDF。只有一张信用卡也能开始 |
| **屏幕** | 页面要求窗口至少 1120px 宽；手机上只能看截图 |

**银行。** RBC、BMO 的对账单和 Wealthsimple 的导出由本地解析器读取。其他银行也能用，但要由 Claude
逐份手读：更慢，而且 Claude 会看到对账单内容。

**按加拿大设计。** 加元、TFSA / RRSP / FHSA、CPP 和 OAS。国内账户也计入净资产。

## 开始

大约二十分钟。

1. **安装 [Claude 桌面应用](https://claude.com/download)** 并登录。
2. **下载这个文件夹**（*Code → Download ZIP*），解压到电脑上任意位置。
3. **打开应用的 Code 标签页，选择这个文件夹。**
4. **把上个月的文件放进 `inbox/`**，不要改文件名。
5. **说"set this up"。** 它会读取文件，起草你的账户和计划，只问文件里看不出来的事。跳过的问题会显示
   *Not set*，绝不会填一个编造的数字。

## 每个月

把当月对账单下载到 `inbox/`，说 **"更新仪表盘"**。你会收到一份简短的报告，以及程序决定不了的问题，
比如一个没见过的商户。

## 你的数据

- **留在你电脑上的文件夹里**：普通的 CSV 和 JSON，加一个 HTML 页面。请自己备份这个文件夹，别处没有副本。
- **解析器读成功的对账单不会发给 Anthropic。** Claude 会读到的是导入摘要、没见过的商户和你的回答，和你在 Claude Code 里说的任何话一样。
- **不会进 git**：setup 会把你的数据排除在提交之外，还有一道守卫拦住会带上它的提交。

## 更多

- **[工作原理](docs/zh/how-it-works.md)**：每一页、每月流程、文件夹结构，以及保证数字可信的检查器。
<!-- LINT:FAULTS n=59 -->
  四个检查器让每个数字都对得上来源；selftest 埋下 59 个问题，证明它们还抓得到。
- **[路线图](ROADMAP.md)** 和 **[更新记录](CHANGELOG.md)**。
- **[产品的目的](PRODUCT.md)**。

<!-- LINT:NAV main=17/5 minwidth=1120 -->
页面共 17 页、5 个侧栏分组 ——
Home · Spending · Income · Investing · Plan · Records · Glossary
—— 仅桌面端，至少 1120px 宽。

MIT 许可：见 [`LICENSE`](LICENSE)。
