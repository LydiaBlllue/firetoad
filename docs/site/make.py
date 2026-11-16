#!/usr/bin/env python3
"""Build the live demo's site: the front page in English and Chinese, beside the demo itself.

    python3 docs/site/make.py OUT --base https://<owner>.github.io/<repo>

writes OUT/index.html, OUT/zh/index.html, OUT/sitemap.xml and copies the demo
(dashboards/finance_dashboard.html → OUT/dashboard.html), the logo and docs/screens/ beside them.
The Pages workflow runs it; run it locally to look at the site before a release.

The front page is the page a search finds, so everything on it is plain HTML, never written by a
script. One layout, two tables of words: the two languages say the same things in the same order.
The screenshots are the demo owner's, retaken at every release by tools/demo.py (the panel's are
taken from the app). Facts only: nothing here that the tool does not do today — no phone app, no
bank connection, no Windows download.
"""
import argparse
import html
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GH = "https://github.com/lydiablllue/firetoad"
DOWNLOAD = GH + "/releases/latest"

# The demo's person is the one tools/demo.py invents; the page names her from there.
sys.path.insert(0, os.path.join(REPO, "tools"))
from demo import P as DEMO  # noqa: E402
CITY_ZH = {"Ottawa": "渥太华", "Toronto": "多伦多", "Vancouver": "温哥华", "Montreal": "蒙特利尔", "Calgary": "卡尔加里"}

EN = dict(
    lang="en", path="", other="zh/", other_name="中文", other_lang="zh",
    title="FIRE Toad — Budget and FIRE tracker for Canada, no bank login",
    desc=("Free, open-source Mac app for Canadians. Drop in your RBC, BMO or any bank's statements "
          "and see your spending, net worth and years to FIRE. No bank login, no account."),
    name="FIRE Toad",
    nav=[("#how", "How it works"), ("#banks", "Banks"), ("#faq", "Questions")],
    h1="Your money on one page — for reaching financial independence in Canada.",
    lede=("Once a month you drop your bank statements into a folder. FIRE Toad reads them on your "
          "Mac, checks that every statement adds up, files every purchase and builds one page: what "
          "you spent, what you own, how many years until financial independence."),
    demo="Open the live demo", download="Download for Mac — free",
    fine=(f"The demo is {DEMO['first']}'s money — a made-up {DEMO['age']}-year-old in {DEMO['city']}. "
          "Nothing to install. The app is signed and notarised by Apple, in English and Chinese, free "
          "and open source (MIT)."),
    phone="The demo is built for a computer screen; on a phone, the pictures below show it.",
    hero_alt="The FIRE page: about 29 to 37 years to financial independence, and what investing more each month changes",
    points=[("No bank login.", "You download your statements; the app reads them on your computer. "
                               "Nothing is uploaded, and there is no account to make."),
            ("Every number adds up.", "A statement is let in only when it balances to the totals it prints."),
            ("Your FIRE plan, not just a budget.", "Years to financial independence, how long the money "
             "lasts, your TFSA, RRSP and FHSA, and money held abroad, in one net worth.")],
    how_lab="How it works", how_h="Once a month, four steps",
    steps=[("Get the files", "Download last month's statements from your bank's website. The app "
                             "says which ones are still missing and how to get each."),
           ("Import", "Drop them in. Each is read on your Mac and let in only if it adds up."),
           ("Categorize", "Answer what a program cannot decide: a shop seen for the first time, "
                          "a transfer with no name. One tap each, remembered next time."),
           ("Done", "Your page is rebuilt with the new month.")],
    panel_img="panel.png", panel_alt="The monthly import in the app, at step 3: what was a $200 e-Transfer with no sender?",
    q_lab="What it answers",
    qs=[("Where do I stand?", "Net worth across every account and currency: a row for what each part "
                              "is for, its bar coloured by how easily you could reach it.",
         "crop-home.png", "Home: net worth $65,655, years to financial independence, this month's investing and spending"),
        ("Where did the money go?", "The year by category and month by month, with what stands out: "
                                    "the biggest category, a subscription, the biggest month.",
         "crop-year.png", "The year: spending by category and what stands out"),
        ("What do I own?", "Your portfolio by currency, by kind of asset and by your own buckets.",
         "crop-port.png", "Portfolio: by currency, kind of asset and bucket"),
        ("Is everything in?", "Which statement arrived which month, and what is still to bring.",
         "crop-src.png", "Statements: a dot for each month each statement arrived")],
    banks_lab="What it reads", banks_h="Your bank's own files",
    banks=[("Read directly", ["RBC · PDF", "BMO · PDF", "Wealthsimple · exports"]),
           ("Through an OFX or QFX download", ["TD", "Scotiabank", "CIBC", "Tangerine", "most other banks"]),
           ("Anything else", "A balance you type once a month, read off the bank's app.")],
    banks_more="Every bank and broker →", banks_doc="docs/banks.md",
    faq_lab="Questions", faq_h="Before you try it",
    faq=[("Is it free?", "Yes. The app is free and open source (MIT). There is nothing to subscribe to."),
         ("Does it connect to my bank?", "No. You download your statements yourself from your bank's "
          "website. The app never sees your bank password."),
         ("Where does my data live?", "In a folder on your Mac: plain CSV and JSON files and one page. "
          "Nothing is sent anywhere unless you turn on the optional AI suggestions, which send only "
          "the names of shops. Backing the folder up is yours."),
         ("Do I need Claude?", "No. The app works on its own. Claude Code is a second way in, for a "
          "statement no parser reads, money held abroad, or a question in words."),
         ("Is there a Windows version?", "Not as a download yet. On Windows it runs from Python "
          "(python3 app.py)."),
         ("My bank is not on the list.", "Download your transactions as OFX or QFX (the Quicken or "
          "Money choice); most Canadian banks offer it. Failing that, a CSV, or the balance typed once a month.")],
    end_h="Try it on sample data first.",
    foot=[(GH, "FIRE Toad on GitHub"), (GH + "/blob/main/docs/install.md", "Installing it")],
)

ZH = dict(
    lang="zh-CN", path="zh/", other="../", other_name="English", other_lang="en",
    title="FIRE蛙 FIRE Toad — 加拿大的记账和 FIRE 工具，不用登录银行",
    desc=("给在加拿大的人的免费开源 Mac app。把 RBC、BMO 或任何银行的对账单放进来，看花了多少、净值多少、"
          "离财务自由还有几年。不用登录银行，不用注册。"),
    name="FIRE蛙 FIRE Toad",
    nav=[("#how", "怎么用"), ("#banks", "银行"), ("#faq", "常见问题")],
    h1="你的钱，一页看完。给在加拿大追求财务自由的人。",
    lede=("每个月把银行对账单放进一个文件夹。FIRE蛙在你的 Mac 上读取它们，核对每份对账单是否对平，"
          "给每笔消费归类，再生成一个页面：花了多少、有多少、离财务自由还有几年。"),
    demo="打开在线 demo", download="下载 Mac 版（免费）",
    fine=(f"demo 里是 {DEMO['first']} 的钱，一位虚构的、住在{CITY_ZH.get(DEMO['city'], DEMO['city'])}的 {DEMO['age']} 岁上班族。"
          "什么都不用装（页面是英文的）。app 经过 Apple 签名和公证，有中文和英文，免费开源（MIT）。"),
    phone="demo 是为电脑屏幕做的；在手机上，可以先看下面的图。",
    hero_alt="FIRE 页：离财务自由大约 29 到 37 年，每月多投一点会怎样",
    points=[("不登录银行。", "对账单你自己下载，app 在你的电脑上读，什么都不上传，也不用注册。"),
            ("每个数都对得上。", "一份对账单要和它自己印的合计对平，才会收进来。"),
            ("不只是记账，还有 FIRE 计划。", "离财务自由几年、钱能撑多久；TFSA、RRSP、FHSA 和国外的钱，都算进一个净值。")],
    how_lab="怎么用", how_h="每个月，四步",
    steps=[("拿文件", "从银行网站下载上个月的对账单。app 会告诉你还差哪几份、每份怎么拿。"),
           ("导入", "把文件放进来。每份都在你的 Mac 上读，对平了才收。"),
           ("归类", "程序定不了的才问你：第一次出现的商户、没有名字的转账。点一下就好，下次记得。"),
           ("完成", "你的页面带上新的一个月，重新生成。")],
    panel_img="panel-zh.png", panel_alt="app 里的月度导入，第 3 步：一笔没写是谁的 $200 e-Transfer 是什么？",
    q_lab="它回答什么",
    qs=[("我现在在哪？", "所有账户、所有币种算在一起的净值：每一行是这部分钱的用途，色条按多容易拿到上色。",
         "crop-home.png", "首页：净值 $65,655、离财务自由几年、这个月的投资和花销"),
        ("钱花到哪去了？", "这一年按分类、按月看，还有特别的地方：最大的分类、一笔订阅、花得最多的月。",
         "crop-year.png", "这一年：按分类的花销和特别的地方"),
        ("我有什么？", "投资组合按币种、资产类别和你自己的分组怎么分。",
         "crop-port.png", "投资组合：按币种、资产类别和分组"),
        ("都到齐了吗？", "哪份对账单哪个月到了，还差哪些。",
         "crop-src.png", "对账单：每份每个月到了就是一个点")],
    banks_lab="能读什么", banks_h="银行自己给的文件",
    banks=[("直接读", ["RBC · PDF", "BMO · PDF", "Wealthsimple · 导出"]),
           ("用 OFX 或 QFX 下载", ["TD", "Scotiabank", "CIBC", "Tangerine", "大多数其他银行"]),
           ("别的", "每月从银行 app 里看一眼余额，填一次。")],
    banks_more="每家银行和券商 →", banks_doc="docs/zh/banks.md",
    faq_lab="常见问题", faq_h="试之前想知道的",
    faq=[("免费吗？", "免费。app 免费开源（MIT），没有订阅。"),
         ("要连我的银行吗？", "不用。对账单你自己从银行网站下载，app 永远看不到你的银行密码。"),
         ("数据放在哪？", "你 Mac 上的一个文件夹里：普通的 CSV、JSON 文件和一个页面。除非你打开可选的 AI 建议"
          "（只发送商户名），什么都不会发出去。文件夹要你自己备份。"),
         ("要用 Claude 吗？", "不用。app 自己就能用。Claude Code 是另一种用法，适合解析器读不了的对账单、国外的钱，"
          "或者想用一句话问。"),
         ("有 Windows 版吗？", "还没有安装包。在 Windows 上可以用 Python 运行（python3 app.py）。"),
         ("我的银行不在上面。", "把交易下载成 OFX 或 QFX（选 Quicken 或 Money）；加拿大大多数银行都有。"
          "实在没有，就用 CSV，或者每月填一次余额。")],
    end_h="先用示例数据看看。",
    foot=[(GH, "GitHub 上的 FIRE蛙"), (GH + "/blob/main/docs/zh/install.md", "怎么安装")],
)

CSS = """
:root { --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e; --muted:#75736d;
        --grid:#e6e4de; --border:rgba(11,11,11,.10); --pill:#efeeea; --ok:#1e7a46; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--page); color:var(--ink);
       font:16px/1.55 system-ui,-apple-system,"Segoe UI","PingFang SC","Hiragino Sans GB",sans-serif; }
a { color:inherit; }
.wrap { max-width:1120px; margin:0 auto; padding:0 24px; }
@media (max-width:600px) { .wrap { padding:0 16px; } }
.top { position:sticky; top:0; z-index:5; background:rgba(249,249,247,.92); backdrop-filter:blur(8px);
       border-bottom:1px solid var(--border); }
.top .wrap { display:flex; align-items:center; gap:22px; height:60px; }
.brand { display:flex; align-items:center; gap:10px; font-weight:700; font-size:17px; text-decoration:none; }
.brand img { width:30px; height:30px; }
.top nav { display:flex; gap:20px; margin-left:auto; font-size:15px; color:var(--ink-2); }
.top nav a { text-decoration:none; }
.top nav a:hover { color:var(--ink); }
@media (max-width:760px) { .top nav .sec { display:none; } }
.lab { font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0 0 10px; }
.hero { display:grid; grid-template-columns:1fr 1.15fr; gap:48px; align-items:center; padding:64px 0 56px; }
@media (max-width:980px) { .hero { grid-template-columns:1fr; gap:36px; padding:40px 0; } }
h1 { font-size:clamp(30px,3.3vw,44px); line-height:1.1; letter-spacing:-.025em; margin:0 0 18px; }
:lang(zh) h1, :lang(zh-CN) h1 { letter-spacing:0; line-height:1.25; }
.lede { color:var(--ink-2); font-size:18px; margin:0 0 26px; max-width:34em; }
.actions { display:flex; flex-wrap:wrap; gap:10px; }
.btn { display:inline-block; border-radius:9px; padding:12px 18px; font-size:16px; font-weight:600; text-decoration:none; }
.primary { background:var(--ink); color:#fff; }
.primary:hover { background:#2b2b2a; }
.secondary { background:var(--pill); color:var(--ink); }
.secondary:hover { background:#e4e2dc; }
.fine { color:var(--muted); font-size:14px; margin:14px 0 0; max-width:36em; }
.phone { display:none; }
@media (max-width:799px) { .phone { display:block; } }
.shot { margin:0; background:var(--page); border:1px solid var(--border); border-radius:14px; overflow:hidden;
        box-shadow:0 1px 2px rgba(11,11,11,.04), 0 12px 32px rgba(11,11,11,.07); }
.shot img { display:block; width:100%; height:auto; }
.points { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:0; padding:0; list-style:none; }
@media (max-width:760px) { .points { grid-template-columns:1fr; } }
.points li { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px; }
.points b { display:block; font-size:17px; margin-bottom:6px; }
.points span { color:var(--ink-2); font-size:15px; }
section { padding:72px 0 0; scroll-margin-top:60px; }
h2 { font-size:clamp(24px,3vw,32px); letter-spacing:-.015em; line-height:1.2; margin:0 0 28px; }
.how { display:grid; grid-template-columns:4fr 7fr; gap:40px; align-items:start; }
@media (max-width:980px) { .how { grid-template-columns:1fr; } }
.steps { margin:0; padding:0; list-style:none; counter-reset:s; }
.steps li { counter-increment:s; position:relative; padding:0 0 22px 44px; }
.steps li::before { content:counter(s); position:absolute; left:0; top:0; width:28px; height:28px; border-radius:50%;
                    background:var(--ink); color:#fff; font-weight:700; font-size:14px; display:flex;
                    align-items:center; justify-content:center; }
.steps li:not(:last-child)::after { content:""; position:absolute; left:13.5px; top:32px; bottom:4px; width:1px; background:var(--grid); }
.steps b { display:block; font-size:17px; margin:2px 0 4px; }
.steps span { color:var(--ink-2); font-size:15px; }
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
.end { margin:88px 0 0; background:var(--ink); color:#fff; border-radius:18px; padding:44px 40px;
       display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:20px; }
.end h2 { margin:0; color:#fff; font-size:clamp(22px,2.6vw,28px); }
.end .primary { background:#fff; color:var(--ink); }
.end .primary:hover { background:#efeeea; }
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
    img = lambda f, alt, lazy=True: (f'<img src="{up}screens/{f}" alt="{e(alt)}"'
                                     + (' loading="lazy"' if lazy else "") + ">")
    btns = (f'<a class="btn primary" href="{up}dashboard.html">{e(t["demo"])}</a>'
            f'<a class="btn secondary" href="{DOWNLOAD}">{e(t["download"])}</a>')
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
  <nav>{''.join(f'<a class="sec" href="{h}">{e(n)}</a>' for h, n in t['nav'])}<a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_name']}</a></nav>
</div></header>
<main class="wrap">
  <div class="hero">
    <div>
      <h1>{e(t['h1'])}</h1>
      <p class="lede">{e(t['lede'])}</p>
      <div class="actions">{btns}</div>
      <p class="fine">{e(t['fine'])}</p>
      <p class="fine phone">{e(t['phone'])}</p>
    </div>
    <figure class="shot">{img('crop-fire.png', t['hero_alt'], lazy=False)}</figure>
  </div>
  <ul class="points">{''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in t['points'])}</ul>

  <section id="how">
    <p class="lab">{e(t['how_lab'])}</p>
    <h2>{e(t['how_h'])}</h2>
    <div class="how">
      <ol class="steps">{''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in t['steps'])}</ol>
      <figure class="shot">{img(t['panel_img'], t['panel_alt'])}</figure>
    </div>
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
    with open(os.path.join(dst, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"  <url><loc>{base}/{p}</loc></url>\n" for p in ("", "zh/", "dashboard.html"))
                + "</urlset>\n")
    shutil.copy(os.path.join(REPO, "docs", "logo.svg"), dst)
    shutil.copy(os.path.join(REPO, "dashboards", "finance_dashboard.html"), os.path.join(dst, "dashboard.html"))
    shutil.copytree(os.path.join(REPO, "docs", "screens"), os.path.join(dst, "screens"), dirs_exist_ok=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--base", required=True, help="the site's own address, no trailing slash")
    a = ap.parse_args()
    build(a.out, a.base)
    print(f"site written to {a.out}")
