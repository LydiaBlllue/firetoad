#!/usr/bin/env python3
"""Build the live demo's site: the front page in English and Chinese, beside the demo itself.

    python3 docs/site/make.py OUT --base https://<owner>.github.io/<repo>

writes OUT/index.html, OUT/zh/index.html, the pages of "FIRE questions" (docs/site/path.py) under
OUT/path/ and OUT/zh/path/, OUT/sitemap.xml and copies the demo
(dashboards/finance_dashboard.html → OUT/dashboard.html), the logo and docs/screens/ beside them.
When the site is the whole domain (a custom domain, no /<repo>/ path) it also writes
OUT/robots.txt naming the sitemap; under a path it does not, because a search engine reads
robots.txt only at the domain's root.
The Pages workflow runs it; run it locally to look at the site before a release.

The front page is the page a search finds, so everything on it is plain HTML, never written by a
script. One layout, two tables of words: the two languages say the same things in the same order.
The screenshots are the demo owner's, retaken at every release by tools/demo.py (the panel's from
the app itself, on a copy of the demo set one month back). Facts only: nothing here that the tool does not do today — no phone app, no
bank connection, no Windows download.
"""
import argparse
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GH = "https://github.com/lydiablllue/firetoad"
# Every Release carries the dmg twice: FIRE-Toad-X.Y.Z.dmg and FIRE-Toad.dmg, the same bytes under a
# name that never changes (since 1.0.7), so the button downloads the newest one directly.
DOWNLOAD = GH + "/releases/latest/download/FIRE-Toad.dmg"
DOWNLOAD_INTEL = GH + "/releases/latest/download/FIRE-Toad-Intel.dmg"   # from 1.0.9 on

# The demo's person is the one tools/demo.py invents; the page names her from there.
sys.path.insert(0, os.path.join(REPO, "tools"))
from demo import P as DEMO  # noqa: E402
sys.path.insert(0, HERE)
import path as road  # noqa: E402  "FIRE questions": one page a question, and an index
CITY_ZH = {"Ottawa": "渥太华", "Toronto": "多伦多", "Vancouver": "温哥华", "Montreal": "蒙特利尔", "Calgary": "卡尔加里"}

EN = dict(
    lang="en", path="", other="zh/", other_name="中文", other_lang="zh",
    title="FIRE Toad — Free budget app for Canada, no bank login",
    desc=("Free, open-source Mac app for Canadians. Drop in your RBC, BMO or any bank's statements "
          "and see your spending, net worth and years to FIRE. No bank login, no account."),
    name="FIRE Toad",
    nav=[("path/", "FIRE questions"), ("#how", "A month with the app"), ("#banks", "Banks"), ("#faq", "Questions")],
    h1="See where your money goes, what you've built, and how many years until work is optional.",
    lede=("Once a month, drop your bank statements into a folder. FIRE Toad reads them on your Mac, "
          "checks that each one adds up, sorts every purchase, and builds one page: what you spent, "
          "what you own, and how many years until financial independence."),
    demo="Try the live demo", download="Download for Mac — free",
    mac=("For Macs with Apple silicon, macOS 11 or later. Intel Mac (macOS 10.15 or later)? ",
         "Download the Intel version", "."),
    fine=(f"The demo shows {DEMO['first']}'s money — a made-up {DEMO['age']}-year-old in {DEMO['city']}. "
          "Nothing to install. The app is signed and notarised by Apple, works in English and Chinese, "
          "and is free and open source (MIT)."),
    phone="The demo is made for a computer screen. On a phone, the pictures below show what it looks like.",
    hero_alt="The FIRE page: about 29 to 37 years to financial independence, and what investing more each month changes",
    points=[("No bank login.", "You download your statements; the app reads them on your computer. "
                               "Nothing is uploaded, and there's no account to create."),
            ("Every number adds up.", "A statement only gets in if it matches the totals printed on it."),
            ("A FIRE plan, not just a budget.", "Years to financial independence, how long your money "
             "will last, your TFSA, RRSP and FHSA, and accounts abroad — all in one net worth.")],
    how_lab="A month with the app", how_h="Once a month, three things to do", you="You", app="The app",
    steps=[("Get your files", "Download last month's statements from your bank, plus your broker's export if you have one.",
            "Tells you which ones are still missing and where to find each.",
            "In the app: each account and what is still needed, and the files in the folder"),
           ("Import", "Drag them in and press Import.",
            "Reads each one on your Mac — nothing is uploaded — and only lets it in if it matches the "
            "statement's own totals. You can undo it.",
            "In the app: what the import will add, before anything is written"),
           ("Categorize", "Answer what only you know: a new shop, an e-Transfer with no name. Some months "
                          "there's nothing to ask.",
            "Remembers every shop and sender you name.",
            "In the app: one question at a time, here an e-Transfer with no sender")],
    then_h="Then", then_p="Your page updates with the new month: what you spent, and where your net worth moved.",
    then_alt="In the app: what changed, with the net worth before and after",
    panel="panel",
    q_lab="What it tells you",
    qs=[("Where do I stand?", "Your net worth across every account and currency — each part labelled "
                              "by what it's for, its bar coloured by how easily you can get to it.",
         "crop-home.png", "Home: net worth, years to financial independence, this month's investing and spending"),
        ("Where did my money go?", "Your year by category and by month, with what stands out: "
                                   "the biggest category, subscriptions, the priciest month.",
         "crop-year.png", "The year: spending by category and what stands out"),
        ("What do I own?", "Your investments by currency, by type of asset, and by account.",
         "crop-port.png", "Portfolio: by currency, kind of asset and account"),
        ("Is everything in?", "Which statements have arrived each month, and what's still missing.",
         "crop-src.png", "Statements: a dot for each month each statement arrived")],
    banks_lab="Banks it reads", banks_h="Straight from your bank's own files",
    banks=[("Read directly", ["RBC · PDF", "BMO · PDF", "Wealthsimple · exports"]),
           ("Via an OFX or QFX download", ["TD", "Scotiabank", "CIBC", "Tangerine", "most other banks"]),
           ("Anything else", "Type in the balance once a month, from your bank's app.")],
    banks_more="See every bank and broker →", banks_doc="docs/banks.md",
    faq_lab="Questions", faq_h="Before you try it",
    faq=[("Is it free?", "Yes — free and open source (MIT), with nothing to subscribe to. There's no "
          "company server behind it: the app runs on your Mac, so there's no account and nothing of "
          "yours to sell. The code is public, so anyone can check."),
         ("I already track my money in a spreadsheet. Why switch?", "Keep it if it works for you. "
          "FIRE Toad does the parts a spreadsheet leaves to you — typing in every row, sorting it into "
          "categories, checking it against the bank — and draws the charts. Everything it keeps is "
          "plain CSV, so your spreadsheet can still open it."),
         ("Does it connect to my bank?", "No. Once a month you sign in to your bank as usual and "
          "download your statements. FIRE Toad never signs in, so it never makes you log in again — "
          "and it never sees your bank password."),
         ("Do I have to categorize everything myself?", "Mostly, no. Once you've categorized a shop, "
          "it stays that way. Only a shop it hasn't seen before is asked — one tap, with common "
          "Canadian chains already filled in for you to confirm. \"Not sure\" is an answer too."),
         ("Where does my data live?", "In a folder on your Mac: plain CSV and JSON files, plus one page. "
          "Nothing is sent anywhere unless you turn on the optional AI suggestions, which send only "
          "shop names. Backing up the folder is up to you."),
         ("Do I need Claude?", "No. The app works on its own. Claude Code is another way to use it — "
          "for a statement the app can't read, accounts abroad, or a question in plain words."),
         ("Which computers does it run on?", "A Mac: one download for Apple silicon (macOS 11 or later), "
          "one for Intel (macOS 10.15 or later). To check which you have: Apple menu → About This Mac, "
          "the Chip or Processor line. There is no Windows download yet; there it runs from Python "
          "(python3 app.py)."),
         ("My bank isn't on the list.", "Download your transactions as OFX or QFX (the Quicken or "
          "Money option) — most Canadian banks offer it. If yours doesn't, use a CSV, or type in the "
          "balance once a month.")],
    end_h="Try it on sample data first.",
    foot=[(GH, "FIRE Toad on GitHub"), (GH + "/blob/main/docs/install.md", "Install guide")],
)

ZH = dict(
    lang="zh-CN", path="zh/", other="../", other_name="English", other_lang="en",
    title="FIRE蛙 FIRE Toad — 加拿大免费记账 app，不用连银行",
    desc=("免费开源的 Mac 记账 app，为在加拿大生活的人做。放进 RBC、BMO 或其他银行的对账单，就能看到钱花在哪、"
          "净值多少、还要几年财务自由。不用连银行，也不用注册。"),
    name="FIRE蛙 FIRE Toad",
    nav=[("path/", "FIRE 问答"), ("#how", "每月怎么用"), ("#banks", "支持的银行"), ("#faq", "常见问题")],
    h1="钱花在哪、攒了多少、还要几年财务自由——一页看清。",
    lede=("每个月把银行对账单放进一个文件夹。FIRE蛙在你的 Mac 上逐份读取、核对金额，把每笔消费分好类，"
          "生成一页总览：花了多少、有多少、还要几年财务自由。"),
    demo="看在线演示", download="免费下载 Mac 版",
    mac=("适用于 Apple 芯片的 Mac，macOS 11 及以上。Intel 芯片的 Mac（macOS 10.15 及以上）请",
         "下载 Intel 版", "。"),
    fine=(f"演示里是 {DEMO['first']} 的钱：一位住在{CITY_ZH.get(DEMO['city'], DEMO['city'])}的 {DEMO['age']} 岁上班族，"
          "人物是虚构的。不用安装，打开就能看（演示页面是英文的）。app 已通过 Apple 签名和公证，支持中英文，免费开源（MIT）。"),
    phone="演示适合在电脑上看；用手机的话，可以先看下面的截图。",
    hero_alt="FIRE 页：离财务自由大约 29 到 37 年，每月多投一点会怎样",
    points=[("不用连银行。", "对账单你自己下载，app 在你的电脑上读取，不上传任何东西，也不用注册。"),
            ("每个数都对得上。", "每份对账单都要和它自己印的合计一致，才会收进来。"),
            ("不只是记账，还有 FIRE 计划。", "还要几年财务自由、退休后钱能撑多久；TFSA、RRSP、FHSA 和海外账户，都算进同一个净值。")],
    how_lab="每月怎么用", how_h="每个月，你只做三件事", you="你", app="app",
    steps=[("下载文件", "从网银下载上个月的对账单；有券商账户的话，再导出一份券商记录。",
            "提醒你还差哪几份、每份去哪下载。",
            "app 里：每个账户还差什么，文件夹里已经有哪些文件"),
           ("导入", "把文件拖进来，点「导入」。",
            "在你的 Mac 上逐份读取，不上传；和对账单自己印的合计一致才收进来。导入后也可以撤销。",
            "app 里：写进去之前，先告诉你会加进来什么"),
           ("归类", "回答只有你知道的事，比如第一次出现的商户、没写付款人的 e-Transfer。有的月份一个问题都没有。",
            "你说过的商户和付款人，它都会记住。",
            "app 里：一次只问一件事，这里是一笔没写付款人的 e-Transfer")],
    then_h="然后", then_p="你的总览页加上新的一个月：花了多少，净值怎么变。",
    then_alt="app 里：这次改了什么，净值前后各是多少",
    panel="panel-zh",
    q_lab="它能回答",
    qs=[("我现在有多少家底？", "所有账户、所有币种合在一起的净值：每一行是这笔钱的用途，色条的颜色表示取用有多方便。",
         "crop-home.png", "首页：净值、还要几年财务自由、这个月的投资和花销"),
        ("钱都花到哪了？", "按分类、按月份看一整年，并标出值得注意的：最大的分类、订阅、花得最多的月份。",
         "crop-year.png", "这一年：按分类的花销和值得注意的地方"),
        ("我的投资怎么分布？", "投资组合按币种、资产类别和账户拆开看。",
         "crop-port.png", "投资组合：按币种、资产类别和账户"),
        ("对账单都齐了吗？", "每份对账单哪个月到了、还差哪些，一目了然。",
         "crop-src.png", "对账单：每份每个月到了就是一个点")],
    banks_lab="支持哪些银行", banks_h="直接用银行提供的文件",
    banks=[("直接读取", ["RBC · PDF", "BMO · PDF", "Wealthsimple · 导出"]),
           ("下载成 OFX 或 QFX 格式", ["TD", "Scotiabank", "CIBC", "Tangerine", "大多数其他银行"]),
           ("其他", "每月看一眼银行 app 里的余额，手动填一次。")],
    banks_more="查看所有银行和券商 →", banks_doc="docs/zh/banks.md",
    faq_lab="常见问题", faq_h="试用之前，你可能想知道",
    faq=[("免费吗？", "免费、开源（MIT），没有订阅。背后没有公司服务器：app 在你的 Mac 上运行，不用注册，"
          "也就没有你的数据可以拿去卖。代码公开，谁都可以检查。"),
         ("我已经在用表格记账了，为什么要换？", "用得顺手就继续用。表格里要你亲手做的事——一行行录入、"
          "一笔笔分类、和银行对账——FIRE蛙替你做，图表也画好了。数据都存成普通的 CSV 文件，你的表格照样能打开。"),
         ("需要连接我的银行吗？", "不需要。每月一次，你像平时一样登录网银、下载对账单。FIRE蛙从不登录银行，"
          "所以不会让你反复验证，也永远拿不到你的银行密码。"),
         ("分类要我一条条自己弄吗？", "基本不用。归过一次类的商户，之后都会自动归到同一类。只有第一次出现的商户才会"
          "问你，点一下就行；常见的加拿大连锁店已经预先填好，你确认一下即可。选「不确定」也可以。"),
         ("数据存在哪里？", "存在你 Mac 上的一个文件夹里：普通的 CSV、JSON 文件和一个页面。除非你开启可选的 AI 建议"
          "（只发送商户名称），否则什么都不会发出去。文件夹需要你自己备份。"),
         ("需要用 Claude 吗？", "不需要，app 可以单独使用。Claude Code 是另一种用法，适合处理 app 读不了的对账单、"
          "海外账户，或者想直接用一句话提问。"),
         ("哪些电脑能用？", "Mac 都能用：Apple 芯片的 Mac 一个安装包（macOS 11 及以上），Intel 芯片的 Mac 一个"
          "（macOS 10.15 及以上）。查法：左上角苹果菜单 →「关于本机」，看「芯片」或「处理器」那一行。Windows 还没有"
          "安装包，可以用 Python 运行（python3 app.py）。"),
         ("我的银行不在列表里怎么办？", "把交易记录下载成 OFX 或 QFX 格式（选 Quicken 或 Money 那一项），"
          "加拿大大多数银行都支持。实在不行，也可以用 CSV，或者每月手动填一次余额。")],
    end_h="先用示例数据试试看。",
    foot=[(GH, "FIRE蛙的 GitHub"), (GH + "/blob/main/docs/zh/install.md", "安装说明")],
)

CSS = """
/* Warm grey (2026-11-17, user 001 chose it from three greys): the page and its cards a shade warmer
   than the app's white, so the screenshots sit on it like paper; one deep warm grey for the main
   button, the step numbers and the closing band. Every text colour is 4.5:1 or more on --page. */
:root { --page:#eeece8; --surface:#f7f6f3; --ink:#2e2c29; --ink-2:#5c5853; --muted:#6b665f;
        --grid:#dcd8d1; --border:rgba(46,44,41,.12); --pill:#e2ded7; --ok:#1e7a46;
        --btn:#4d4842; --btn-hover:#3d3934; --band:#3a3733; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--page); color:var(--ink);
       font:16px/1.55 system-ui,-apple-system,"Segoe UI","PingFang SC","Hiragino Sans GB",sans-serif; }
a { color:inherit; }
.wrap { max-width:1120px; margin:0 auto; padding:0 24px; }
@media (max-width:600px) { .wrap { padding:0 16px; } }
.top { position:sticky; top:0; z-index:5; background:rgba(238,236,232,.92); backdrop-filter:blur(8px);
       border-bottom:1px solid var(--border); }
.top .wrap { display:flex; align-items:center; gap:22px; height:60px; }
.brand { display:flex; align-items:center; gap:10px; font-weight:700; font-size:17px; text-decoration:none; }
.brand img { width:30px; height:30px; }
.top nav { display:flex; gap:20px; margin-left:auto; font-size:15px; color:var(--ink-2); }
.top nav a { text-decoration:none; }
.top nav a:hover { color:var(--ink); }
@media (max-width:760px) { .top nav .sec { display:none; } }
/* "FIRE questions" stays in the bar on a phone (2026-11-17): nothing in the bar wraps, and below
   400px the wordmark gives way to the logo alone, which still goes home */
.top a { white-space:nowrap; }
@media (max-width:400px) { .top .brand { font-size:0; gap:0; } .top nav { gap:14px; font-size:14px; } }
.lab { font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0 0 10px; }
.hero { display:grid; grid-template-columns:1fr 1.15fr; gap:48px; align-items:center; padding:64px 0 56px; }
@media (max-width:980px) { .hero { grid-template-columns:1fr; gap:36px; padding:40px 0; } }
h1 { font-size:clamp(30px,3.3vw,44px); line-height:1.1; letter-spacing:-.025em; margin:0 0 18px; }
:lang(zh) h1, :lang(zh-CN) h1 { letter-spacing:0; line-height:1.25; }
.lede { color:var(--ink-2); font-size:18px; margin:0 0 26px; max-width:34em; }
.actions { display:flex; flex-wrap:wrap; gap:10px; }
.btn { display:inline-block; border-radius:9px; padding:12px 18px; font-size:16px; font-weight:600; text-decoration:none; }
.primary { background:var(--btn); color:#fff; }
.primary:hover { background:var(--btn-hover); }
.secondary { background:var(--pill); color:var(--ink); }
.secondary:hover { background:var(--grid); }
.fine { color:var(--muted); font-size:14px; margin:14px 0 0; max-width:36em; }
.phone { display:none; }
@media (max-width:799px) { .phone { display:block; } }
.shot { margin:0; background:var(--page); border:1px solid var(--border); border-radius:14px; overflow:hidden;
        box-shadow:0 1px 2px rgba(46,44,41,.05), 0 12px 32px rgba(46,44,41,.09); }
.shot img { display:block; width:100%; height:auto; }
.points { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:0; padding:0; list-style:none; }
@media (max-width:760px) { .points { grid-template-columns:1fr; } }
.points li { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px; }
.points b { display:block; font-size:17px; margin-bottom:6px; }
.points span { color:var(--ink-2); font-size:15px; }
section { padding:72px 0 0; scroll-margin-top:60px; }
h2 { font-size:clamp(24px,3vw,32px); letter-spacing:-.015em; line-height:1.2; margin:0 0 28px; }
/* Once a month, three things to do (2026-11-17, user 001): what you do is one short line, what the
   app does the longer one under it; then the result, which asks nothing of you. One step a row, the
   words beside the whole picture: in two columns the panel's tall and short views left holes. */
.walk { display:grid; grid-template-columns:1fr; gap:20px; margin:0; padding:0; list-style:none; }
.wk { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:28px;
      display:grid; grid-template-columns:5fr 6fr; gap:20px 40px; align-items:center; }
@media (max-width:980px) { .wk { grid-template-columns:1fr; padding:22px; } }
.wk .txt { display:flex; flex-direction:column; gap:16px; }
.wk h3 { display:flex; align-items:center; gap:12px; font-size:20px; margin:0; letter-spacing:-.01em; }
.wk h3 i { flex:none; width:28px; height:28px; border-radius:50%; background:var(--btn); color:#fff; font-style:normal;
           font-size:14px; font-weight:700; display:inline-flex; align-items:center; justify-content:center; }
.who { display:grid; grid-template-columns:auto 1fr; gap:8px 14px; margin:0; font-size:15.5px; line-height:1.5; }
.who dt { color:var(--muted); font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase;
          padding-top:3px; white-space:nowrap; }
.who dd { margin:0; color:var(--ink-2); }
.who dd.you { color:var(--ink); }
.wk .pic { margin:0; }
.wk .pic img { display:block; width:100%; height:auto; border-radius:10px; border:1px solid var(--border);
               box-shadow:0 1px 2px rgba(46,44,41,.05), 0 10px 28px rgba(46,44,41,.08); }
.wk.then { background:#eaf1ea; border-color:rgba(30,122,70,.22); }
.wk.then h3 i { background:var(--ok); }
.wk.then p { margin:0; font-size:15.5px; color:var(--ink-2); }
.qs { display:grid; gap:56px; }
.q { display:grid; grid-template-columns:4fr 7fr; gap:40px; align-items:center; }
.q:nth-child(even) { grid-template-columns:7fr 4fr; }
.q:nth-child(even) .qt { order:2; }
@media (max-width:980px) { .q, .q:nth-child(even) { grid-template-columns:1fr; gap:18px; }
                           .q:nth-child(even) .qt { order:0; } }
.q h3 { font-size:24px; letter-spacing:-.01em; margin:0 0 8px; }
.q p { color:var(--ink-2); margin:0; font-size:16px; }
.banks { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
@media (max-width:760px) { .banks { grid-template-columns:1fr; } }
.bank { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px; }
.bank b { display:block; margin-bottom:10px; }
.bank p { margin:0; color:var(--ink-2); font-size:15px; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin:0; padding:0; list-style:none; }
.chips li { background:var(--pill); border-radius:999px; padding:4px 11px; font-size:14px; color:var(--ink-2); }
.more { display:inline-block; margin-top:16px; color:var(--ink-2); font-size:15px; }
.faq { display:grid; grid-template-columns:1fr 1fr; gap:28px 48px; margin:0; }
@media (max-width:760px) { .faq { grid-template-columns:1fr; } }
.faq dt { font-weight:700; font-size:17px; margin:0 0 6px; }
.faq dd { margin:0; color:var(--ink-2); font-size:15px; }
.end { margin:88px 0 0; background:var(--band); color:#fff; border-radius:18px; padding:44px 40px;
       display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:20px; }
.end h2 { margin:0; color:#fff; font-size:clamp(22px,2.6vw,28px); }
.end .primary { background:#fff; color:var(--ink); }
.end .primary:hover { background:var(--pill); }
.end .secondary { background:rgba(255,255,255,.12); color:#fff; }
.end .secondary:hover { background:rgba(255,255,255,.2); }
@media (max-width:600px) { .end { padding:28px 20px; } }
footer { padding:36px 0 48px; color:var(--muted); font-size:14px; display:flex; flex-wrap:wrap; gap:20px; }
footer a { color:var(--ink-2); }
"""


def page(t, base):
    e = html.escape
    up = "../" if t["path"] else ""
    url = f"{base}/{t['path']}"
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "FIRE Toad",
          "operatingSystem": "macOS", "applicationCategory": "FinanceApplication",
          "description": t["desc"], "url": url, "downloadUrl": DOWNLOAD, "inLanguage": t["lang"],
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CAD"}}
    panel = lambda i: f"{t['panel']}-{i}.png"   # the app's monthly panel at step i, taken by tools/demo.py
    img = lambda f, alt, lazy=True: (f'<img src="{up}screens/{f}" alt="{e(alt)}"'
                                     + (' loading="lazy"' if lazy else "") + ">")
    btns = (f'<a class="btn primary" href="{DOWNLOAD}">{e(t["download"])}</a>'
            f'<a class="btn secondary" href="{up}dashboard.html">{e(t["demo"])}</a>')
    out = [f"""<!doctype html>
<!-- Built by docs/site/make.py; edit that, not this. -->
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['desc'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{base}/">
<link rel="alternate" hreflang="zh" href="{base}/zh/">
<link rel="alternate" hreflang="x-default" href="{base}/">
<link rel="icon" href="{up}logo.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="FIRE Toad">
<meta property="og:title" content="{e(t['title'])}">
<meta property="og:description" content="{e(t['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}/screens/crop-fire.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script>
  // An old link to a page of the demo (…/firetoad/#fire) still opens that page.
  if (location.hash.length > 1 && !document.getElementById(location.hash.slice(1)) &&
      !/^#(how|banks|faq)$/.test(location.hash)) location.replace('{up}dashboard.html' + location.hash);
</script>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="{up or './'}"><img src="{up}logo.svg" alt="">{e(t['name'])}</a>
  <nav>{''.join(f'<a class="{"road" if h == "path/" else "sec"}" href="{h}">{e(n)}</a>' for h, n in t['nav'])}<a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_name']}</a></nav>
</div></header>
<main class="wrap">
  <div class="hero">
    <div>
      <h1>{e(t['h1'])}</h1>
      <p class="lede">{e(t['lede'])}</p>
      <div class="actions">{btns}</div>
      <p class="fine">{e(t['mac'][0])}<a href="{DOWNLOAD_INTEL}">{e(t['mac'][1])}</a>{e(t['mac'][2])}</p>
      <p class="fine">{e(t['fine'])}</p>
      <p class="fine phone">{e(t['phone'])}</p>
    </div>
    <figure class="shot">{img('crop-fire.png', t['hero_alt'], lazy=False)}</figure>
  </div>
  <ul class="points">{''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in t['points'])}</ul>

  <section id="how">
    <p class="lab">{e(t['how_lab'])}</p>
    <h2>{e(t['how_h'])}</h2>
    <ol class="walk">{''.join(f'<li class="wk"><div class="txt"><h3><i>{i}</i>{e(a)}</h3><dl class="who"><dt>{e(t["you"])}</dt>'
                              f'<dd class="you">{e(y)}</dd><dt>{e(t["app"])}</dt><dd>{e(d)}</dd></dl></div>'
                              f'<figure class="pic">{img(panel(i), alt)}</figure></li>'
                              for i, (a, y, d, alt) in enumerate(t['steps'], 1))}<li class="wk then"><div class="txt"><h3><i>✓</i>{e(t['then_h'])}</h3>
      <p>{e(t['then_p'])}</p></div><figure class="pic">{img(panel(4), t['then_alt'])}</figure></li></ol>
  </section>

  <section>
    <p class="lab">{e(t['q_lab'])}</p>
    <div class="qs">"""]
    for h, p, f, alt in t["qs"]:
        out.append(f"""
      <div class="q"><div class="qt"><h3>{e(h)}</h3><p>{e(p)}</p></div><figure class="shot">{img(f, alt)}</figure></div>""")
    out.append(f"""
    </div>
  </section>

  <section id="banks">
    <p class="lab">{e(t['banks_lab'])}</p>
    <h2>{e(t['banks_h'])}</h2>
    <div class="banks">{''.join(f'<div class="bank"><b>{e(h)}</b>' + (f'<p>{e(xs)}</p>' if isinstance(xs, str) else '<ul class="chips">' + ''.join(f'<li>{e(x)}</li>' for x in xs) + '</ul>') + '</div>' for h, xs in t['banks'])}</div>
    <a class="more" href="{GH}/blob/main/{t['banks_doc']}">{e(t['banks_more'])}</a>
  </section>

  <section id="faq">
    <p class="lab">{e(t['faq_lab'])}</p>
    <h2>{e(t['faq_h'])}</h2>
    <dl class="faq">{''.join(f'<div><dt>{e(q)}</dt><dd>{e(a)}</dd></div>' for q, a in t['faq'])}</dl>
  </section>

  <div class="end"><h2>{e(t['end_h'])}</h2><div class="actions">{btns}</div></div>
  <footer>{''.join(f'<a href="{h}">{e(n)}</a>' for h, n in t['foot'])}<a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_name']}</a></footer>
</main>
</body>
</html>
""")
    return "".join(out)


def build(dst, base):
    base = base.rstrip("/")
    os.makedirs(os.path.join(dst, "zh"), exist_ok=True)
    for t in (EN, ZH):
        with open(os.path.join(dst, t["path"], "index.html"), "w", encoding="utf-8") as f:
            f.write(page(t, base))
    stops = road.build(dst, base, CSS, REPO, DOWNLOAD)
    with open(os.path.join(dst, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"  <url><loc>{base}/{p}</loc></url>\n" for p in ["", "zh/", "dashboard.html"] + stops)
                + "</urlset>\n")
    if not urlparse(base).path.strip("/"):
        with open(os.path.join(dst, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
    shutil.copy(os.path.join(REPO, "docs", "logo.svg"), dst)
    shutil.copy(os.path.join(REPO, "dashboards", "finance_dashboard.html"), os.path.join(dst, "dashboard.html"))
    shutil.copytree(os.path.join(REPO, "docs", "screens"), os.path.join(dst, "screens"), dirs_exist_ok=True)
    broken = dead_links(dst)
    if broken:
        raise SystemExit("links that point nowhere:\n  " + "\n  ".join(broken))


def dead_links(dst):
    """Every relative href and src in the built site that names no file: a page links only to a
    page that was written (a stop not yet published is never linked)."""
    bad = []
    for d, _, files in os.walk(dst):
        for n in files:
            if not n.endswith(".html") or n == "dashboard.html":
                continue
            src = os.path.join(d, n)
            for ref in re.findall(r'(?:href|src)="([^"#?]*)', open(src, encoding="utf-8").read()):
                if not ref or re.match(r"[a-z]+:", ref):
                    continue
                target = os.path.normpath(os.path.join(d, ref))
                if os.path.isdir(target) or ref.endswith("/"):
                    target = os.path.join(target, "index.html")
                if not os.path.exists(target):
                    bad.append(f"{os.path.relpath(src, dst)} → {ref}")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--base", required=True, help="the site's own address, no trailing slash")
    a = ap.parse_args()
    build(a.out, a.base)
    print(f"site written to {a.out}")
