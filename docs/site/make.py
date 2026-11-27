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
    title="FIRE Toad — Free FIRE tracker for Canada, no bank login",
    desc=("Free, open-source Mac app for Canadians: how many years until financial independence, worked "
          "out from your own RBC, BMO or other bank statements. No bank login, no account."),
    name="FIRE Toad",
    nav=[("path/", "FIRE questions"), ("#setup", "Setting up"), ("#how", "A month with the app"), ("#banks", "Banks"), ("#ai", "AI assist"), ("#faq", "FAQ")],
    h1="How many years until work is optional?",
    lede=("Once a month, drop your bank statements into a folder. FIRE Toad reads them on your Mac, "
          "checks that each one adds up, and works out what you spend, what you keep, and how many years "
          "until financial independence — then how long the money lasts once you stop, with CPP and OAS counted."),
    demo="Try the live demo", download="Download for Mac — free",
    mac=("For Macs with Apple silicon, macOS 11 or later. Intel Mac (macOS 10.15 or later)? ",
         "Download the Intel version", "."),
    fine=(f"The demo shows {DEMO['first']}'s money — a made-up {DEMO['age']}-year-old in {DEMO['city']}. "
          "Nothing to install. The app is signed and notarised by Apple, works in English and Chinese, "
          "and is free and open source (MIT)."),
    phone=("For now, FIRE Toad is a download for Mac only.", "There is no phone or Windows version. "
           "The live demo opens in any computer's browser; on a phone it is too narrow and scrolls sideways.",
           "Send yourself the link", "Link copied", "Open the demo anyway",
           "Paste it into a message or an email to yourself, then open it on your Mac."),
    hero_alt="The FIRE page: how many years to financial independence, and what investing more each month changes",
    points=[("Years, not just a budget.", "How many years until financial independence at what you really "
             "invest, and what $400 more a month would change. Your TFSA, RRSP and FHSA in one net worth."),
            ("No bank login.", "You download your statements; the app reads them on your computer. "
                               "Nothing is uploaded, and there's no account to create. Each statement is "
                               "checked against the totals your bank printed on it, so nothing is missed "
                               "or counted twice."),
            ("AI assist, if you want it.", "A shop the app doesn't know gets a suggested category from "
             "Claude, ChatGPT or DeepSeek, with your own key. Only the shop's name is sent, and you still choose.")],
    setup_lab="The first time", setup_h="Set up in 20–30 minutes", setup_img="setup",
    setup=[("Bring 1–3 months", "Download your last one to three months of statements, plus your broker's export "
            "if you have one, and drop them in.",
            "Recognises each file and drafts your accounts from them.",
            "In the app: the files dropped in, and three accounts drafted from them"),
           ("Check what it filled in", "Change only what's wrong: your accounts, your income and everyday spending, "
            "whether to track FIRE, the day you'll import each month.",
            "Fills in every screen from your files: each account and its balance, your pay, what your cards spend.",
            "In the app: each account filled in, with its balance and what it is for"),
           ("Build your page", "Press Build it, then categorize the shops it couldn't place.",
            "Reads every file, checks each one adds up, and makes your page. Common Canadian chains are already filed.",
            "In the app: everything you set, checked once before the page is built")],
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
    ai_lab="AI assist — optional", ai_h="A shop it doesn't know? AI suggests, you choose.",
    ai=[("Suggests, never decides", "A shop the app has never seen comes with a suggested category: the first "
         "button on its card, marked as AI assist's. You still tap the answer, and nothing accepts them all at once.",
         "ai-card.png", "A card in the panel: AI assist's suggestion is the first button"),
        ("Your AI, and you see what it got", "Claude, ChatGPT or DeepSeek with your own API key, or Ollama if it "
         "already runs on your Mac. Only shop names go out, once a month — never an amount, a date or an account. "
         "Settings lists every one sent and how many suggestions you kept. Off until you turn it on; off again "
         "deletes the key.",
         "ai-settings.png", "Settings, AI assist: the service, the key, how often it was asked, what was sent")],
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
    road_lab="FIRE questions", road_h="What to know on the way to financial independence",
    road_lede="One question a page, answered in a sentence, with the sources and a calculator you can try.",
    road_more="See all FIRE questions →",
    banks_lab="Banks it reads", banks_h="Straight from your bank's own files",
    banks=[("Read directly", ["RBC · PDF", "BMO · PDF", "Wealthsimple · exports"]),
           ("Via an OFX or QFX download", ["TD", "Scotiabank", "CIBC", "Tangerine", "most other banks"]),
           ("Anything else", "Type in the balance once a month, from your bank's app.")],
    banks_more="See every bank and broker →", banks_doc="docs/banks.md",
    install_more="Install guide →", install_doc="docs/install.md",
    # the words that open the code, where the page says it is open: "anyone can check" is a promise
    code_links=["open source", "anyone can check"],
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
          "Canadian chains already filled in for you to confirm. \"Not sure\" is an answer too. Turn on "
          "AI assist and the rest come with a suggestion as well."),
         ("Where does my data live?", "In a folder on your Mac: plain CSV and JSON files, plus one web page. "
          "FIRE Toad never sends your financial data to anyone. The only exception is if you turn on "
          "AI assist and choose an online AI. Then your shop names are sent to it. If the AI runs "
          "on your own computer, nothing is sent. Backing up the folder is up to you."),
         ("I'm not planning to retire early. Is it for me?", "Yes. Without a goal, it's your spending, what "
          "you keep each month, and how long your savings would last without a paycheque. The years to "
          "financial independence are there when you want them."),
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
    title="FIRE蛙 FIRE Toad — 加拿大免费 FIRE 工具，不用连银行",
    desc=("免费开源的 Mac app，为在加拿大想财务自由的人做：用你自己的 RBC、BMO 或其他银行对账单，"
          "算出还要几年财务自由。不用连银行，也不用注册。"),
    name="FIRE蛙 FIRE Toad",
    nav=[("path/", "FIRE 问答"), ("#setup", "建账"), ("#how", "每月怎么用"), ("#banks", "支持的银行"), ("#ai", "AI 辅助"), ("#faq", "常见问题")],
    h1="离财务自由，还有几年？",
    lede=("每个月把银行对账单放进一个文件夹。FIRE蛙在你的 Mac 上逐份读取、核对金额，算出你花多少、存下多少、"
          "还要几年财务自由，再算停工以后钱能撑多久，CPP 和 OAS 也算进去。"),
    demo="看在线演示", download="免费下载 Mac 版",
    mac=("适用于 Apple 芯片的 Mac，macOS 11 及以上。Intel 芯片的 Mac（macOS 10.15 及以上）请",
         "下载 Intel 版", "。"),
    fine=(f"演示里是 {DEMO['first']} 的钱：一位住在{CITY_ZH.get(DEMO['city'], DEMO['city'])}的 {DEMO['age']} 岁上班族，"
          "人物是虚构的。不用安装，打开就能看。app 已通过 Apple 签名和公证，支持中英文，免费开源（MIT）。"),
    phone=("目前只支持 Mac 下载。", "目前没有手机版和 Windows 版。在线演示用任何电脑的浏览器都能看；手机屏幕太窄，要左右滑动。",
           "把链接发给自己", "链接已复制", "仍在手机上看演示",
           "粘贴到微信或邮件里发给自己，再在 Mac 上打开。"),
    hero_alt="FIRE 页：还要几年财务自由，每月多投一点会怎样",
    points=[("不只是记账，是还要几年。", "按你实际投进去的钱，算还要几年财务自由，每月多投 400 元能早多少。"
             "TFSA、RRSP、FHSA 都算进同一个净值。"),
            ("不用连银行。", "对账单你自己下载，app 在你的电脑上读取，不上传任何东西，也不用注册。"
             "每份对账单都与银行印出的合计核对，不漏记、不重记。"),
            ("想用的话，有 AI 辅助。", "app 不认识的商户，由 Claude、ChatGPT 或 DeepSeek 建议一个分类，用你自己的 key。"
             "只发商户名，最后还是你定。")],
    setup_lab="第一次", setup_h="建账，20–30 分钟", setup_img="setup-zh",
    setup=[("带上 1–3 个月的文件", "从网银下载最近一到三个月的对账单；有券商账户的话，再导出一份券商记录，一起拖进来。",
            "认出每份文件，用它们替你起好账户。",
            "app 里：拖进来的文件，和据此起好的三个账户"),
           ("核对它填好的", "只改不对的：你的账户、每月收入和日常开销、要不要跟踪 FIRE、每月哪天导入。",
            "每一屏都从你的文件里填好：每个账户和余额、你的工资、卡上每月花多少。",
            "app 里：每个账户都已填好，带余额和用途"),
           ("生成你的页面", "点「开始生成」，再给它认不出的商户归类。",
            "读每份文件、核对合计，做出你的页面。常见的加拿大连锁店已经归好类。",
            "app 里：生成之前，把你定的都核对一遍")],
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
    ai_lab="AI 辅助——可选", ai_h="不认得的商户？AI 给建议，你来选。",
    ai=[("只建议，不替你定", "第一次出现的商户会带一个建议的类别：卡片上第一个按钮，标明是 AI 辅助的建议。"
         "还是你自己点，也没有「全部接受」。",
         "ai-card-zh.png", "面板里的一张卡片：AI 辅助的建议是第一个按钮"),
        ("用你自己的 AI，发了什么都看得到", "Claude、ChatGPT 或 DeepSeek，用你自己的 API key；或者 Mac 上已经装好的 Ollama。"
         "每月一次，只发商户名，从不发金额、日期和账户。设置里列着发过的每一个、它的建议你收下了几个。"
         "默认关闭；关掉时 key 一起删掉。",
         "ai-settings.png", "设置里的 AI 辅助：服务、key、问过几次、发了什么")],
    q_lab="它能回答",
    qs=[("我现在的净值是多少？", "所有账户、所有币种合在一起的净值：每一行是这笔钱的用途，色条的颜色表示取用有多方便。",
         "crop-home.png", "首页：净值、还要几年财务自由、这个月的投资和花销"),
        ("钱都花到哪了？", "按分类、按月份看一整年，并标出值得注意的：最大的分类、订阅、花得最多的月份。",
         "crop-year.png", "这一年：按分类的花销和值得注意的地方"),
        ("我的投资怎么分布？", "投资组合按币种、资产类别和账户拆开看。",
         "crop-port.png", "投资组合：按币种、资产类别和账户"),
        ("对账单都齐了吗？", "每份对账单哪个月到了、还差哪些，一目了然。",
         "crop-src.png", "对账单：每份每个月到了就是一个点")],
    road_lab="FIRE 问答", road_h="走向财务自由，要先弄懂的几个问题",
    road_lede="一页一个问题，一句话答案，带出处，还有可以自己试的计算器。",
    road_more="看全部 FIRE 问答 →",
    banks_lab="支持哪些银行", banks_h="直接用银行提供的文件",
    banks=[("直接读取", ["RBC · PDF", "BMO · PDF", "Wealthsimple · 导出"]),
           ("下载成 OFX 或 QFX 格式", ["TD", "Scotiabank", "CIBC", "Tangerine", "大多数其他银行"]),
           ("其他", "每月看一眼银行 app 里的余额，手动填一次。")],
    banks_more="查看所有银行和券商 →", banks_doc="docs/zh/banks.md",
    install_more="安装说明 →", install_doc="docs/zh/install.md",
    code_links=["开源", "谁都可以检查"],
    faq_lab="常见问题", faq_h="试用之前，你可能想知道",
    faq=[("免费吗？", "免费、开源（MIT），没有订阅。背后没有公司服务器：app 在你的 Mac 上运行，不用注册，"
          "也就没有你的数据可以拿去卖。代码公开，谁都可以检查。"),
         ("我已经在用表格记账了，为什么要换？", "用得顺手就继续用。表格里要你亲手做的事——一行行录入、"
          "一笔笔分类、和银行对账——FIRE蛙替你做，图表也画好了。数据都存成普通的 CSV 文件，你的表格照样能打开。"),
         ("需要连接我的银行吗？", "不需要。每月一次，你像平时一样登录网银、下载对账单。FIRE蛙从不登录银行，"
          "所以不会让你反复验证，也永远拿不到你的银行密码。"),
         ("分类要我一条条自己弄吗？", "基本不用。归过一次类的商户，之后都会自动归到同一类。只有第一次出现的商户才会"
          "问你，点一下就行；常见的加拿大连锁店已经预先填好，你确认一下即可。选「不确定」也可以。打开 AI 辅助的话，其余的也会带一个建议。"),
         ("数据存在哪里？", "存在你 Mac 上的一个文件夹里：普通的 CSV、JSON 文件和一个网页。FIRE蛙不会把你的财务数据"
          "发给任何人。只有一种情况例外：你自己开了 AI 辅助，而且用的是网上的 AI。这时商户名字会发给它。"
          "如果 AI 装在你自己的电脑上，就什么都不会发出去。文件夹需要你自己备份。"),
         ("我没打算提前退休，也能用吗？", "能。不设目标，它就是你花了多少、每月存下多少、没了工资存款能撑多久。"
          "想看还要几年财务自由的时候，它一直在。"),
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
/* On a phone (2026-11-21): nothing here can be installed and the demo wants a wide screen, so the
   buttons give way to one line saying to open the site on a computer, a button that sends the link
   on (the phone's share sheet, else the clipboard), and the picture moves up under the question. */
.phone { display:none; }
.phone p { margin:0 0 12px; font-size:16px; color:var(--ink); }
.phone button { font:inherit; border:0; cursor:pointer; }
.phone .anyway { display:block; margin:14px 0 0; font-size:14px; color:var(--ink-2); }
.phone .copied { margin:10px 0 0; font-size:14px; color:var(--ink-2); }
.end .phone .copied { color:rgba(255,255,255,.85); }
.end .phone .anyway { color:rgba(255,255,255,.75); }
@media (max-width:799px) {
  .phone { display:block; margin:22px 0 0; }
  .actions, .mac { display:none; }
  .hero { display:flex; flex-direction:column; gap:0; padding:28px 0 36px; }
  .hero > div { display:contents; }
  .hero > div > * { order:3; }
  .hero > div > h1 { order:1; }
  .hero .shot { order:2; margin:0 0 22px; }
  .hero .lede { margin:0; }
}
.shot { margin:0; background:var(--page); border:1px solid var(--border); border-radius:14px; overflow:hidden;
        box-shadow:0 1px 2px rgba(46,44,41,.05), 0 12px 32px rgba(46,44,41,.09); }
.shot img { display:block; width:100%; height:auto; }
.points { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:0; padding:0; list-style:none; }
@media (max-width:980px) { .points { grid-template-columns:1fr; } }
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
/* FIRE questions (2026-11-17, user 001): the published pages in the road's order, four at most,
   each its question and its one-line answer, read from path.py so a page not yet written is never linked */
.road-lede { color:var(--ink-2); font-size:17px; margin:-14px 0 24px; max-width:40em; }
.roads { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:0; padding:0; list-style:none; }
@media (max-width:760px) { .roads { grid-template-columns:1fr; } }
.roads a { display:block; height:100%; background:var(--surface); border:1px solid var(--border); border-radius:12px;
           padding:18px 20px; text-decoration:none; }
.roads a:hover { border-color:rgba(46,44,41,.28); }
.roads b { display:block; font-size:17px; margin-bottom:6px; }
.roads span { color:var(--ink-2); font-size:15px; }
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
.end .phone { margin:0; }
.end .phone p { color:#fff; }
footer { padding:36px 0 48px; color:var(--muted); font-size:14px; display:flex; flex-wrap:wrap; gap:20px; }
footer a { color:var(--ink-2); }
"""


def page(t, base):
    def code(text, k):
        """The words that say the code is open link to it, once, where they are said."""
        w = html.escape(t["code_links"][k])
        return text.replace(w, f'<a href="{GH}">{w}</a>', 1)
    e = html.escape
    up = "../" if t["path"] else ""
    # The demo opens in the page's own language (2026-11-25, the dashboard in two languages).
    demo = f"{up}dashboard.html?lang={'zh' if t['lang'].startswith('zh') else 'en'}"
    url = f"{base}/{t['path']}"
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "FIRE Toad",
          "operatingSystem": "macOS", "applicationCategory": "FinanceApplication",
          "description": t["desc"], "url": url, "downloadUrl": DOWNLOAD, "inLanguage": t["lang"],
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CAD"}}
    panel = lambda i: f"{t['panel']}-{i}.png"   # the app's monthly panel at step i, taken by tools/demo.py
    img = lambda f, alt, lazy=True: (f'<img src="{up}screens/{f}" alt="{e(alt)}"'
                                     + (' loading="lazy"' if lazy else "") + ">")
    btns = (f'<a class="btn primary" href="{DOWNLOAD}">{e(t["download"])}</a>'
            f'<a class="btn secondary" href="{demo}">{e(t["demo"])}</a>')
    onphone = (f'<div class="phone"><p><b>{e(t["phone"][0])}</b>{"" if t["lang"].startswith("zh") else " "}'
               f'{e(t["phone"][1])}</p>'
               f'<button class="btn primary" type="button" data-url="{url}" data-done="{e(t["phone"][3])}">'
               f'{e(t["phone"][2])}</button><p class="copied" hidden>{e(t["phone"][5])}</p>'
               f'<a class="anyway" href="{demo}">{e(t["phone"][4])}</a></div>')
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
      !/^#(setup|how|ai|banks|faq)$/.test(location.hash)) location.replace('{demo}' + location.hash);
</script>
<style>{CSS}</style>
<script>
  // "Send yourself the link": the phone's share sheet where there is one, else copy it.
  document.addEventListener('click', ev => {{
    const b = ev.target.closest('.phone button'); if (!b) return;
    const url = b.dataset.url, hint = b.nextElementSibling;
    const done = () => {{ b.textContent = b.dataset.done; hint.hidden = false; }};
    const ask = () => prompt(hint.textContent, url);
    if (navigator.share) navigator.share({{url}}).catch(() => {{}});
    else if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, ask);
    else ask();
  }});
</script>
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
      {onphone}
      <p class="fine mac">{e(t['mac'][0])}<a href="{DOWNLOAD_INTEL}">{e(t['mac'][1])}</a>{e(t['mac'][2])}</p>
      <p class="fine">{code(e(t['fine']), 0)}</p>
    </div>
    <figure class="shot">{img('crop-fire.png', t['hero_alt'], lazy=False)}</figure>
  </div>
  <ul class="points">{''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in t['points'])}</ul>

  <!-- In the order a visitor decides (2026-11-25, the owner): what it tells you, then the work it
       asks (setting up, a month), the banks it reads, the optional AI, the FIRE questions, the rest. -->
  <section>
    <p class="lab">{e(t['q_lab'])}</p>
    <div class="qs">{''.join(f'<div class="q"><div class="qt"><h3>{e(h)}</h3><p>{e(p)}</p></div><figure class="shot">{img(f, alt)}</figure></div>' for h, p, f, alt in t['qs'])}</div>
  </section>

  <section id="setup">
    <p class="lab">{e(t['setup_lab'])}</p>
    <h2>{e(t['setup_h'])}</h2>
    <ol class="walk">{''.join(f'<li class="wk"><div class="txt"><h3><i>{i}</i>{e(a)}</h3><dl class="who"><dt>{e(t["you"])}</dt>'
                              f'<dd class="you">{e(y)}</dd><dt>{e(t["app"])}</dt><dd>{e(d)}</dd></dl></div>'
                              f'<figure class="pic">{img(t["setup_img"] + f"-{i}.png", alt)}</figure></li>'
                              for i, (a, y, d, alt) in enumerate(t['setup'], 1))}</ol>
    <a class="more" href="{GH}/blob/main/{t['install_doc']}">{e(t['install_more'])}</a>
  </section>

  <section id="how">
    <p class="lab">{e(t['how_lab'])}</p>
    <h2>{e(t['how_h'])}</h2>
    <ol class="walk">{''.join(f'<li class="wk"><div class="txt"><h3><i>{i}</i>{e(a)}</h3><dl class="who"><dt>{e(t["you"])}</dt>'
                              f'<dd class="you">{e(y)}</dd><dt>{e(t["app"])}</dt><dd>{e(d)}</dd></dl></div>'
                              f'<figure class="pic">{img(panel(i), alt)}</figure></li>'
                              for i, (a, y, d, alt) in enumerate(t['steps'], 1))}<li class="wk then"><div class="txt"><h3><i>✓</i>{e(t['then_h'])}</h3>
      <p>{e(t['then_p'])}</p></div><figure class="pic">{img(panel(4), t['then_alt'])}</figure></li></ol>
  </section>

  <section id="banks">
    <p class="lab">{e(t['banks_lab'])}</p>
    <h2>{e(t['banks_h'])}</h2>
    <div class="banks">{''.join(f'<div class="bank"><b>{e(h)}</b>' + (f'<p>{e(xs)}</p>' if isinstance(xs, str) else '<ul class="chips">' + ''.join(f'<li>{e(x)}</li>' for x in xs) + '</ul>') + '</div>' for h, xs in t['banks'])}</div>
    <a class="more" href="{GH}/blob/main/{t['banks_doc']}">{e(t['banks_more'])}</a>
  </section>

  <section id="ai">
    <p class="lab">{e(t['ai_lab'])}</p>
    <h2>{e(t['ai_h'])}</h2>
    <div class="qs">{''.join(f'<div class="q"><div class="qt"><h3>{e(h)}</h3><p>{e(p)}</p></div><figure class="shot">{img(f, alt)}</figure></div>' for h, p, f, alt in t['ai'])}</div>
  </section>

  <section id="road">
    <p class="lab">{e(t['road_lab'])}</p>
    <h2>{e(t['road_h'])}</h2>
    <p class="road-lede">{e(t['road_lede'])}</p>
    <ul class="roads">{''.join(f'<li><a href="path/{s["slug"]}/"><b>{e(s[t["lang"][:2]]["title"])}</b><span>{e(s[t["lang"][:2]]["line"])}</span></a></li>' for s in road_stops()[:4])}</ul>
    <a class="more" href="path/">{e(t['road_more'])}</a>
  </section>

  <section id="faq">
    <p class="lab">{e(t['faq_lab'])}</p>
    <h2>{e(t['faq_h'])}</h2>
    <dl class="faq">{''.join(f'<div><dt>{e(q)}</dt><dd>{code(e(a), 1)}</dd></div>' for q, a in t['faq'])}</dl>
  </section>

  <div class="end"><h2>{e(t['end_h'])}</h2><div class="actions">{btns}</div>{onphone}</div>
  <footer>{''.join(f'<a href="{h}">{e(n)}</a>' for h, n in t['foot'])}<a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_name']}</a></footer>
</main>
</body>
</html>
"""]
    return "".join(out)


def road_stops():
    """The published FIRE questions in the road's order, the same order path.py writes them in."""
    return sorted(road.stops(REPO), key=lambda s: [int(x) for x in s["id"].split(".")])


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
