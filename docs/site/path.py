"""path.py — "FIRE questions" on the site (FIRE 问答; the knowledge map's "My way to FIRE"): one page a stop, in English and Chinese, and an index.

A stop is one question someone would search for, answered in a sentence, with why it matters, a
way to work it out, its sources and what to know before relying on it. The content is data
(STOPS below); the pages are drawn from it by one layout per language, the way make.py draws
the front page. Only the stops in STOPS are published: a stop goes up once its sources are
checked, so nothing links to a page that does not exist — the index, the previous and next stop
and the list beside each page name published stops only, and build() refuses a site with a
relative link that points nowhere.

Every figure on a page is worked out here, never typed: the CPP lines from the government's
0.6% / 0.7% a month, the history from the yearly returns in findata/ledgers/returns.json
(Damodaran, NYU Stern; US inflation from the BLS), the raise example from the same formula the
app uses for years to financial independence. The reader's own numbers never reach the site: the
calculators run in the page and send nothing.

Each address is a fixed English name (/path/when-to-take-cpp/), never the stop's number, which
moves when a stop is added; Chinese is the same name under /zh/.
"""
import html
import json
import math
import os

e = html.escape
YEARS = 25                       # the 4% rule: a year of spending, twenty-five times
REAL = 0.05                      # the return the worked examples use, after inflation
CHECKED = {"en": "Checked against these sources in November 2026.", "zh": "2026 年 11 月按以上出处核对过。"}

# ---------------------------------------------------------------- what the site says around a stop
WORDS = {
    "en": dict(road="FIRE questions", prev="Before this", next="Next stop", why="Why it matters",
               src="Sources", limits="Before you rely on it", download="Download for Mac — free",
               demo="See it on sample data", other="中文", how="About the app",
               cta=("FIRE Toad works these out with your own numbers: your target, the age your pensions "
                    "start paying part of the bill, your savings rate. It runs on your Mac; your statements "
                    "never leave it."),
               index_lede=("What to know on the way to financial independence, one question a page, each with "
                           "its sources. The first pages are up; more follow as each one’s sources are checked."),
               index_cta=("FIRE Toad works out your own number, your years to financial independence and your savings "
                          "rate from your statements. It runs on your Mac; your statements never leave it."),
               stages=["Get started", "Set a goal", "Stay on track", "After FIRE"],
               anchors=["get-started", "set-a-goal", "stay-on-track", "after-fire"],
               stage_q=["Where does my money go, and will I be all right?", "How much do I need, and how long will it take?",
                        "How do I keep going each month?", "How do I live on it?"]),
    "zh": dict(road="FIRE 问答", prev="上一站", next="下一站", why="为什么要紧", src="出处",
               limits="用之前要知道", download="下载 Mac 版，免费", demo="先看演示数据", other="English", how="关于这个 app",
               cta="FIRE Toad 用你自己的数算这些：你的目标、你的养老金几岁开始替组合付一部分开销、你的储蓄率。它在你的 Mac 上运行，对账单不会离开你的电脑。",
               index_lede="走向财务自由要懂的事，一页一个问题，每页带出处。先上线了几页，其余的核对完出处一页一页加。",
               index_cta="FIRE Toad 用你的对账单算出你自己的目标、离财务自由几年和储蓄率。它在你的 Mac 上运行，对账单不会离开你的电脑。",
               stages=["开始理财", "定目标", "执行", "自由以后"],
               anchors=["get-started", "set-a-goal", "stay-on-track", "after-fire"],
               stage_q=["钱花到哪去了？会不会翻车？", "我要多少？还差几年？", "每个月怎么走？", "不上班了，钱怎么取？"]),
}


# ---------------------------------------------------------------- the figures, worked out
def cpp():
    """CPP and OAS by the age they start (Canada.ca, both pages dated 2026-10-02): 0.6% a month
    less before 65, 0.7% a month more after it, for CPP; 0.6% a month more after 65 for OAS."""
    early, late, oas_late = 0.006, 0.007, 0.006
    f60, f70 = 1 - early * 60, 1 + late * 60
    cross = lambda s1, f1, s2, f2: (f2 * s2 - f1 * s1) / (f2 - f1)       # f1(a − s1) = f2(a − s2)
    return {"f60": f60, "f70": f70, "oas70": 1 + oas_late * 60,
            "c6065": cross(60, f60, 65, 1), "c6570": cross(65, 1, 70, f70), "c6070": cross(60, f60, 70, f70)}


def history(repo):
    """The share of starting years whose money lasted 30, 40 and 50 years at each withdrawal rate:
    US data from returns.json, 60% stocks and 40% 10-year Treasuries, the first year's amount
    raised with inflation every year after, taken out at the start of each year."""
    ret = json.load(open(os.path.join(repo, "findata", "ledgers", "returns.json"), encoding="utf-8"))
    cols = ret["columns"]
    yr = {r[0]: dict(zip(cols, r)) for r in ret["years"]}
    first, last = min(yr), max(yr)
    real = lambda y: (1 + 0.6 * yr[y]["stocks"] + 0.4 * yr[y]["bonds"]) / (1 + yr[y]["inflation"]) - 1
    rates = [r / 1000 for r in range(30, 51, 5)]

    def lasted(w, n):
        starts = [s for s in yr if s + n - 1 <= last]
        ok = 0
        for s in starts:
            b = 1.0
            for y in range(s, s + n):
                b -= w
                if b <= 0:
                    break
                b *= 1 + real(y)
            ok += b > 0
        return ok / len(starts) * 100, len(starts)

    tab = {n: [lasted(w, n)[0] for w in rates] for n in (30, 40, 50)}
    return {"first": first, "last": last, "rates": rates, "tab": tab, "n30": lasted(0.04, 30)[1]}


def years_to(income, spend):
    """Years from nothing until 25 years of spending is invested, saving the rest each year."""
    c, t = income - spend, spend * YEARS
    return math.log((t + c / REAL) / (c / REAL)) / math.log(1 + REAL)


def svg_lines(series, xs, x0, x1, y0, y1, xlab, ytick, yfmt, xfmt, marks=(), w=680, h=300):
    """A line chart: series = [(name, ys, colour)]; a dashed line the page's script moves."""
    L, R, T, B = 52, 96, 14, 34
    X = lambda x: L + (x - x0) / (x1 - x0) * (w - L - R)
    Y = lambda y: T + (1 - (y - y0) / (y1 - y0)) * (h - T - B)
    g = [f'<line x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#dcd8d1"/>'
         f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{e(yfmt(v))}</text>' for v in ytick]
    g += [f'<text x="{X(x):.1f}" y="{h - 10}" text-anchor="middle">{e(xfmt(x))}</text>' for x in xlab]
    for name, ys, col in series:
        g.append(f'<polyline points="{" ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in zip(xs, ys))}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        g.append(f'<text x="{X(xs[-1]) + 8:.1f}" y="{Y(ys[-1]) + 4:.1f}" style="fill:{col};font-weight:600">{e(name)}</text>')
    for x, y, t in marks:
        g.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4.5" fill="#2e2c29"/>'
                 f'<text x="{X(x):.1f}" y="{Y(y) - 10:.1f}" text-anchor="middle" style="fill:#2e2c29;font-weight:600">{e(t)}</text>')
    g.append(f'<line class="vl" x1="{X(x0)}" x2="{X(x0)}" y1="{T}" y2="{h - B}" stroke="#2e2c29" stroke-dasharray="3 3"/>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" data-l="{L}" data-r="{w - R}" data-x0="{x0}" data-x1="{x1}">'
            + "".join(g) + "</svg>")


SLIDE_JS = """function vline(svg, x){ var L = +svg.dataset.l, R = +svg.dataset.r, x0 = +svg.dataset.x0, x1 = +svg.dataset.x1,
  p = L + (Math.min(Math.max(x, x0), x1) - x0) / (x1 - x0) * (R - L), v = svg.querySelector('.vl'); v.setAttribute('x1', p); v.setAttribute('x2', p); }
function money(v){ return '$' + Math.round(v).toLocaleString('en-US'); }"""


# ---------------------------------------------------------------- the stops published so far
def stops(repo):
    """The published stops, in the road's order. `id` is the knowledge map's (KNOWLEDGE 2.2 …),
    `slug` the address, `stage` 0–3. Each language carries its own words; the figures are shared."""
    c, h = cpp(), history(repo)
    base = years_to(100, 80)
    raise_rows = [(100 + 10, 90), (110, 85), (110, 80)]
    years_cpp = list(range(60, 96))
    cum = lambda start, f: [max(0, a - start) * 12 * f * 1000 for a in years_cpp]
    lang_age = {"en": lambda a: f"{a}", "zh": lambda a: f"{a} 岁"}
    cpp_chart = lambda lang, names: svg_lines(
        [(names[0], cum(60, c["f60"]), "#b5651d"), (names[1], cum(65, 1), "#2a78d6"), (names[2], cum(70, c["f70"]), "#1e7a46")],
        years_cpp, 60, 95, 0, 450000, [60, 65, 70, 75, 80, 85, 90, 95], [0, 100000, 200000, 300000, 400000],
        lambda v: f"${v / 1000:.0f}k", lang_age[lang],
        marks=[(c["c6065"], (c["c6065"] - 65) * 12 * 1000, lang_age[lang](round(c["c6065"]))),
               (c["c6570"], (c["c6570"] - 65) * 12 * 1000, lang_age[lang](round(c["c6570"])))])
    hist_chart = lambda names: svg_lines(
        [(names[0], h["tab"][30], "#2a78d6"), (names[1], h["tab"][40], "#b5651d"), (names[2], h["tab"][50], "#7a3fb0")],
        [w * 100 for w in h["rates"]], 3.0, 5.0, 0, 100, [3.0, 3.5, 4.0, 4.5, 5.0], [0, 25, 50, 75, 100],
        lambda v: f"{v:.0f}%", lambda x: f"{x:.1f}%")
    t30, t50 = h["tab"][30][2], h["tab"][50][2]
    pct = lambda v: f"{v:.0f}%"
    cpp_js = f"""(function(){{ var s = document.getElementById('age'), o = document.getElementById('ageo'), svg = document.querySelector('#chart svg'), unit = o.dataset.unit;
  function go(){{ var a = +s.value; o.textContent = a + unit;
    [[60, {c['f60']}], [65, 1], [70, {c['f70']}]].forEach(function(p, i){{ document.getElementById('r' + i).textContent = money(Math.max(0, a - p[0]) * 12 * p[1] * 1000); }});
    vline(svg, a); }}
  s.addEventListener('input', go); go(); }})();"""
    hist_js = f"""(function(){{ var T = {json.dumps({str(n): [round(v, 1) for v in h['tab'][n]] for n in h['tab']})}, W = {json.dumps([round(w * 100, 1) for w in h['rates']])};
  var s = document.getElementById('wr'), o = document.getElementById('wro'), svg = document.querySelector('#chart svg'), times = document.getElementById('mult').dataset.unit;
  function go(){{ var i = +s.value, w = W[i]; o.textContent = w.toFixed(1) + '%';
    document.getElementById('mult').textContent = (100 / w).toFixed(1) + times;
    ['30','40','50'].forEach(function(n){{ document.getElementById('h' + n).textContent = Math.round(T[n][i]) + '%'; }});
    vline(svg, w); }}
  s.addEventListener('input', go); go(); }})();"""
    rule_js = f"""(function(){{ var i = document.getElementById('m');
  function go(){{ var m = parseFloat(String(i.value).replace(/[^0-9.]/g, '')) || 0; document.getElementById('y').textContent = money(m * 12); document.getElementById('t').textContent = money(m * 12 * {YEARS}); }}
  i.addEventListener('input', go); go(); }})();"""
    life_js = f"""(function(){{ var s = document.getElementById('keep'), o = document.getElementById('keepo'), r = {REAL}, W = JSON.parse(o.dataset.words);
  function yrs(inc, sp){{ var c = inc - sp, t = sp * {YEARS}; return Math.log((t + c / r) / (c / r)) / Math.log(1 + r); }}
  function go(){{ var k = +s.value / 100, sp = 80 + 10 * (1 - k), y = yrs(110, sp), d = Math.round({base:.4f} - y);
    o.textContent = Math.round(k * 100) + '%';
    document.getElementById('lr').textContent = Math.round((110 - sp) / 110 * 100) + '%';
    document.getElementById('ly').textContent = Math.round(y) + W.yrs;
    document.getElementById('ld').textContent = d > 0 ? W.sooner.replace('N', d) : (d < 0 ? W.later.replace('N', -d) : W.same); }}
  s.addEventListener('input', go); go(); }})();"""
    rows = lambda names, unit: "".join(
        f'<tr><td>{e(n)}</td><td class="n">{(i - s) / i * 100:.0f}%</td><td class="n">{years_to(i, s):.0f}{unit}</td></tr>'
        for n, (i, s) in zip(names, raise_rows))
    return [
        {"id": "1.6", "slug": "lifestyle-inflation", "stage": 0, "js": life_js,
         "en": dict(name="Lifestyle inflation", line="When income rises and spending follows, the savings rate stands still.",
                    title="Got a raise but not saving more? Lifestyle inflation",
                    desc="Why a raise often doesn't raise your savings, and how many years it can cost or save on the way to financial independence.",
                    lede="When income rises and spending rises with it, the savings rate stands still, or falls. A raise is the easiest moment to save more, because nothing you already spend has to be cut.",
                    why="Once spending rises, the number you need rises with it, since it is 25 times a year’s spending. You lose twice.",
                    body=f"""<h2>A worked example</h2>
<p>Take-home 100, spending 80: a savings rate of 20%, and {base:.0f} years from nothing at 5% a year after inflation. After a raise of 10:</p>
<div class="tblw"><table class="tbl"><tr><th>What happens to the raise</th><th>Savings rate</th><th>Years of work</th></tr>{rows(["Spend it all", "Spend half", "Save it all"], " years")}</table></div>
<p>Spending all of it takes {years_to(110, 90) - base:.0f} years longer than before the raise: income rose, and so did what it has to pay for.</p>
<div class="chart"><div class="slide">Of the raise, save <input type="range" id="keep" min="0" max="100" step="10" value="50"> <output id="keepo" data-words='{e(json.dumps({"yrs": " years", "sooner": "N years sooner than before the raise", "later": "N years later than before the raise", "same": "The same as before the raise"}))}'></output></div>
<div class="read"><span>Savings rate <b id="lr"></b></span><span>Years of work <b id="ly"></b></span><span><b id="ld"></b></span></div></div>""",
                    limits=[("This is not saying you can’t live better.", "It only turns the raise into years; what you do with it is yours."),
                            ("A one-off big purchase is not a change of lifestyle.", "The month you move or buy a car says little; a year’s average does.")],
                    sources=[("Maths.", "The table and the slider use the formula FIRE Toad uses for years to financial independence: 5% a year after inflation, a target of 25 times a year’s spending. The idea itself is a common one in personal finance; no study is cited.")]),
         "zh": dict(name="生活方式通胀", line="收入涨了，开销跟着涨，储蓄率就原地不动。",
                    title="加薪了，为什么还是存不下钱？",
                    desc="为什么加薪常常不等于多存钱，以及加薪的钱怎么用，离财务自由会早几年或晚几年。",
                    lede="收入涨了，开销跟着涨，储蓄率就原地不动，甚至往下掉。加薪是提高储蓄率最不痛的机会，因为不用削减任何已经有的开销。",
                    why="开销一旦跟着涨上去，要攒的目标也跟着变大（目标是一年开销的 25 倍），等于两头吃亏。",
                    body=f"""<h2>算一个例子</h2>
<p>到手 100，花 80，储蓄率 20%，按每年 5% 的实际回报，从零开始要 {base:.0f} 年。加薪 10 之后：</p>
<div class="tblw"><table class="tbl"><tr><th>加薪的钱怎么用</th><th>储蓄率</th><th>要工作几年</th></tr>{rows(["全花掉", "花一半", "全存下"], " 年")}</table></div>
<p>全花掉反而比加薪前多 {years_to(110, 90) - base:.0f} 年：收入涨了，要养的开销也涨了。</p>
<div class="chart"><div class="slide">加薪的钱存下 <input type="range" id="keep" min="0" max="100" step="10" value="50"> <output id="keepo" data-words='{e(json.dumps({"yrs": " 年", "sooner": "比加薪前早 N 年", "later": "比加薪前晚 N 年", "same": "跟加薪前一样"}, ensure_ascii=False))}'></output></div>
<div class="read"><span>储蓄率 <b id="lr"></b></span><span>要工作 <b id="ly"></b></span><span><b id="ld"></b></span></div></div>""",
                    limits=[("这不是说不能提高生活水平。", "这里只把加薪换算成年数，怎么用是你的事。"),
                            ("一次性的大额开销不算。", "搬家、买车的那个月不代表生活方式变了，要看一年的平均。")],
                    sources=[("数学。", "表和滑杆用 FIRE Toad 算「离财务自由几年」的同一个公式：每年回报 5%，扣掉通胀，目标是一年开销的 25 倍。这个说法本身是理财里的通用说法，不引用研究。")])},
        {"id": "2.2", "slug": "how-much-to-retire-early", "stage": 1, "js": rule_js,
         "en": dict(name="The 4% rule", line="About 25 times a year’s spending.",
                    title="How much do you need to retire early?",
                    desc="The 4% rule in one page: why your number is about 25 times a year's spending, where it comes from, and a calculator.",
                    lede="About 25 times what you plan to spend in a year. That is the 4% rule: take out 4% in the first year, the same amount raised with inflation every year after, and in US history the money lasted at least 30 years.",
                    why="It turns a question nobody can answer, how much is enough, into one you can: how much do you spend in a year. Every target in FIRE Toad starts here.",
                    body=f"""<h2>Work it out</h2>
<div class="calc"><label>Spending a month <input id="m" inputmode="decimal" value="$2,950"></label>
<div class="rows"><div><span>A year</span><span id="y"></span></div><div><span>Times 25: your number</span><b id="t"></b></div></div>
<p class="formula">Your number = spending a month × 12 × 25. The amount filled in is FIRE Toad’s sample owner’s; change it to yours. Nothing you type leaves this page.</p></div>""",
                    limits=[("The 25 is measured on US history and 30 years.", f"Retiring at 40 can mean 50 years, and most countries did worse. In the same history, 4% lasted 50 years from {t50:.0f}% of the starting years. The next stop has more.")],
                    sources=[("Bengen, Journal of Financial Planning, October 1994.", "US data from 1926, half stocks and half intermediate Treasuries, withdrawals raised with inflation. At 4% the money never ran out in less than 33 years."),
                             ("Cooley, Hubbard and Walz (the Trinity study), AAII Journal, February 1998.", "US data from 1926 to 1995, the same kind of test over more mixes of stocks and bonds.")]),
         "zh": dict(name="4% 法则 / 25 倍", line="大约一年开销的 25 倍。",
                    title="提前退休要存多少钱？",
                    desc="一页讲清 4% 法则：为什么目标大约是一年开销的 25 倍，它从哪来，再自己算一算。",
                    lede="大约一年开销的 25 倍。这就是 4% 法则：第一年取出 4%，以后每年取同样多、跟着物价涨，在美国的历史上，这笔钱至少撑了 30 年。",
                    why="它把一个没人答得上来的问题「多少才够」，换成一个答得上来的问题「我一年花多少」。FIRE Toad 里的每个目标数都从这里来。",
                    body=f"""<h2>算一算</h2>
<div class="calc"><label>每月开销 <input id="m" inputmode="decimal" value="$2,950"></label>
<div class="rows"><div><span>一年</span><span id="y"></span></div><div><span>乘以 25：你的目标</span><b id="t"></b></div></div>
<p class="formula">目标 = 每月开销 × 12 × 25。填着的是 FIRE Toad 演示用户的数，改成你自己的就行。你输入的数不会离开这个页面。</p></div>""",
                    limits=[("25 倍是按美国的历史、撑 30 年算的。", f"40 岁退休可能要撑 50 年，而大多数国家的历史没这么好。按同样的历史，4% 撑 50 年时只有 {t50:.0f}% 的开始年份撑住了。下一站细说。")],
                    sources=[("Bengen，《Journal of Financial Planning》，1994 年 10 月。", "用 1926 年以来的美国数据，一半股票一半中期国债，每年取的钱跟着物价涨。按 4% 取，钱没有一次在 33 年内用完。"),
                             ("Cooley、Hubbard、Walz（三一研究），《AAII Journal》，1998 年 2 月。", "用 1926 到 1995 年的美国数据，对更多种股债比例做了同样的检验。")])},
        {"id": "2.3", "slug": "does-the-4-percent-rule-last", "stage": 1, "js": hist_js,
         "en": dict(name="The limits of 4%", line="Lasting 40 or 50 years asks for less than 4%.",
                    title="Does the 4% rule last 40 or 50 years?",
                    desc=f"Retiring early means the money has to last longer. In US history since {h['first']}, how often 3% to 5% lasted 30, 40 and 50 years.",
                    lede=f"The 4% rule comes from US history over 30 years, and retiring early means lasting longer. Taking 4% a year, the money lasted 30 years from {t30:.0f}% of the starting years, and 50 years from only {t50:.0f}%. Taking out less means a bigger number: 3.5% is 28.6 times a year’s spending, 3% is 33.3 times.",
                    why="The 25 under every FIRE target comes from it. Retiring at 40 can mean 50 years, and most countries’ history was worse than the US’s. Knowing this is what lets you decide whether to leave yourself room.",
                    body=f"""<h2>Work it out: how much, for how long</h2>
<div class="chart" id="chart"><div class="slide">Take out each year <input type="range" id="wr" min="0" max="{len(h['rates']) - 1}" value="2"> <output id="wro"></output></div>
{hist_chart(["30 years", "40 years", "50 years"])}
<div class="read"><span>Your number: <b id="mult" data-unit=" times a year’s spending"></b></span><span>Lasting 30 years <b id="h30"></b></span><span>40 years <b id="h40"></b></span><span>50 years <b id="h50"></b></span></div>
<p class="note">Worked out by FIRE Toad from US data, {h['first']} to {h['last']}: 60% stocks and 40% 10-year Treasuries, the first year’s withdrawal raised with inflation every year after. Each percentage is the share of starting years whose money lasted; lasting 30 years was tried from {h['n30']} starting years. History, not a forecast.</p></div>
<h2>What research found</h2>
<ul class="src"><li><b>Pfau, Journal of Financial Planning, December 2010.</b><br>17 countries over 30 years: 4% held in only four. Canada was the highest, at 4.42%.</li>
<li><b>Anarkulova, Cederburg, O’Doherty and Sias, Journal of Pension Economics and Finance, 2025.</b><br>38 developed countries: 2.31% for a couple aged 65 accepting a 5% chance of running out.</li>
<li><b>Early Retirement Now, “The Ultimate Guide to Safe Withdrawal Rates”, part 1, 2016 (a blog).</b><br>US data from 1871, half stocks and half bonds: 4% lasted 30 years 95% of the time, and 60 years 65%.</li></ul>""",
                    limits=[("The withdrawal rate and the number are one choice.", "Taking out less is steadier, but means working longer. Once CPP and OAS begin, the portfolio pays less, so for an early retiree the hard years are the ones before them.")],
                    sources=[]),
         "zh": dict(name="4% 的局限", line="要撑 40、50 年，4% 就偏高了。",
                    title="4% 法则撑得了 40 年、50 年吗？",
                    desc=f"提前退休，钱要撑得更久。按 {h['first']} 年以来的美国历史，每年取 3% 到 5%，撑 30、40、50 年的各有几成。",
                    lede=f"4% 是按美国历史、撑 30 年算出来的，提前退休要撑得更久。按同样的历史，每年取 4%，撑 30 年时 {t30:.0f}% 的开始年份撑住了，撑 50 年时只有 {t50:.0f}%。取得少一点，目标就要大一点：3.5% 是 28.6 倍，3% 是 33.3 倍。",
                    why="25 倍是整个目标的基础。40 岁退休可能要撑 50 年，而大多数国家的历史没有美国这么好。知道这一点，才会决定要不要给自己留余量。",
                    body=f"""<h2>算一算：取多少，撑多久</h2>
<div class="chart" id="chart"><div class="slide">每年取 <input type="range" id="wr" min="0" max="{len(h['rates']) - 1}" value="2"> <output id="wro"></output></div>
{hist_chart(["撑 30 年", "撑 40 年", "撑 50 年"])}
<div class="read"><span>目标是一年开销的 <b id="mult" data-unit=" 倍"></b></span><span>撑 30 年 <b id="h30"></b></span><span>撑 40 年 <b id="h40"></b></span><span>撑 50 年 <b id="h50"></b></span></div>
<p class="note">FIRE Toad 用 {h['first']} 到 {h['last']} 年的美国数据自己算的：六成股票、四成十年期国债，第一年取出这个比例，以后每年取同样多、跟着物价涨。百分比是钱撑住了的开始年份占几成，撑 30 年一共试了 {h['n30']} 个开始年份。这是历史，不是预测。</p></div>
<h2>研究怎么说</h2>
<ul class="src"><li><b>Pfau，《Journal of Financial Planning》，2010 年 12 月。</b><br>17 个国家看 30 年，4% 只在 4 个国家撑住了；加拿大最高，是 4.42%。</li>
<li><b>Anarkulova、Cederburg、O’Doherty、Sias，《Journal of Pension Economics and Finance》，2025 年。</b><br>38 个发达国家；65 岁的夫妇如果能接受 5% 的可能把钱用完，取款率是 2.31%。</li>
<li><b>Early Retirement Now，「The Ultimate Guide to Safe Withdrawal Rates」第 1 部分，2016 年（博客）。</b><br>美国 1871 年以来的数据，一半股票一半债券，4% 撑 30 年的成功率是 95%，撑 60 年是 65%。</li></ul>""",
                    limits=[("取款率和目标是同一个选择。", "取得少更稳，但要多工作几年。养老金（CPP、OAS）开始以后，组合要付的就少了，所以早退休的人真正难的是领养老金之前的那些年。")],
                    sources=[])},
        {"id": "2.11", "slug": "when-to-take-cpp", "stage": 1, "js": cpp_js,
         "en": dict(name="Take CPP early or late", line="Every month later, CPP pays more for life.",
                    title="When to take CPP: at 60, 65 or 70?",
                    desc="The rules for starting CPP and OAS early or late, and at what age the later start catches up, worked out in today's dollars.",
                    lede=f"CPP can start any time from 60 to 70, OAS from 65 to 70. Every month before 65, CPP pays 0.6% less; every month after, 0.7% more, for life. In today’s dollars, someone who starts at 60 is caught up by someone who starts at 65 at about {c['c6065']:.0f}.",
                    why="An early retiree lives on their investments until the pensions begin. Starting later raises the floor under every month of the later years, and it rises with prices: insurance against living a long time.",
                    body=f"""<h2>The rules</h2>
<div class="tblw"><table class="tbl"><tr><th></th><th>Earliest</th><th>Standard</th><th>Latest</th><th>Earlier</th><th>Later</th></tr>
<tr><td><b>CPP</b></td><td>60</td><td>65</td><td>70</td><td>0.6% less a month, 36% less at 60</td><td>0.7% more a month, 42% more at 70</td></tr>
<tr><td><b>OAS</b></td><td>65</td><td>65</td><td>70</td><td>Cannot start early</td><td>0.6% more a month, 36% more at 70</td></tr></table></div>
<p class="note">A full OAS needs 40 years in Canada after 18; fewer years pay a share, years ÷ 40. Quebec has the QPP, with similar but not identical rules.</p>
<h2>Work it out: live to which age, and which pays more</h2>
<div class="chart" id="chart"><div class="slide">Live to <input type="range" id="age" min="60" max="95" value="85"> <output id="ageo" data-unit=""></output></div>
{cpp_chart("en", ["Start at 60", "Start at 65", "Start at 70"])}
<div class="read"><span>Start at 60 <b id="r0"></b></span><span>Start at 65 <b id="r1"></b></span><span>Start at 70 <b id="r2"></b></span></div>
<p class="note">An example of $1,000 a month at 65: ${c['f60'] * 1000:,.0f} at 60, ${c['f70'] * 1000:,.0f} at 70. In today’s dollars, leaving out what the earlier payments could earn invested, and tax. Starting at 60 against 70 catches up at about {c['c6070']:.0f}.</p></div>""",
                    limits=[("The catch-up ages are simplified.", "They leave out what earlier payments could earn invested, and tax; CPP itself also depends on how many years you paid in."),
                            ("This page gives the rules, not the age you should choose.", "That depends on health, other income and a partner, and it is yours to decide."),
                            ("A newcomer’s OAS is often not full.", "The 40-year rule matters to many people.")],
                    sources=[("Government of Canada, CPP, “When to start your retirement pension”, page dated 2 October 2026.", "0.6% less a month before 65, up to 36%; 0.7% more a month after, up to 42%."),
                             ("Government of Canada, OAS, “When to start”, page dated 2 October 2026.", "0.6% more a month after 65, up to 36%; the 40-year residence rule.")]),
         "zh": dict(name="早领还是晚领", line="每晚一个月，CPP 一辈子都多领一点。",
                    title="CPP 几岁开始领？60、65 还是 70 岁",
                    desc="CPP 和 OAS 早领、晚领的规则，以及按今天的钱算，晚领在几岁追上早领。",
                    lede=f"CPP 可以在 60 到 70 岁之间开始领，OAS 在 65 到 70 岁之间。比 65 岁每早一个月，CPP 少 0.6%；每晚一个月，多 0.7%，一辈子都是。按今天的钱算，60 岁开始领的人，累计领到的钱在 {c['c6065']:.0f} 岁左右被 65 岁开始领的人追上。",
                    why="提前退休的人，在养老金开始之前全靠自己的投资。晚领让后半辈子每月的保底更高，而且跟着物价涨，等于给「活得很久」上了一份保险。",
                    body=f"""<h2>规则</h2>
<div class="tblw"><table class="tbl"><tr><th></th><th>最早</th><th>标准</th><th>最晚</th><th>早领</th><th>晚领</th></tr>
<tr><td><b>CPP</b></td><td>60 岁</td><td>65 岁</td><td>70 岁</td><td>每早一个月少 0.6%，60 岁领少 36%</td><td>每晚一个月多 0.7%，70 岁领多 42%</td></tr>
<tr><td><b>OAS</b></td><td>65 岁</td><td>65 岁</td><td>70 岁</td><td>不能早领</td><td>每晚一个月多 0.6%，70 岁领多 36%</td></tr></table></div>
<p class="note">OAS 全额要 18 岁以后在加拿大住满 40 年；不满的按住的年数 ÷ 40 领一部分。魁北克用的是 QPP，规则相近但不相同。</p>
<h2>算一算：活到几岁，哪种领得多</h2>
<div class="chart" id="chart"><div class="slide">活到 <input type="range" id="age" min="60" max="95" value="85"> <output id="ageo" data-unit=" 岁"></output></div>
{cpp_chart("zh", ["60 岁开始", "65 岁开始", "70 岁开始"])}
<div class="read"><span>60 岁开始 <b id="r0"></b></span><span>65 岁开始 <b id="r1"></b></span><span>70 岁开始 <b id="r2"></b></span></div>
<p class="note">按 65 岁开始领每月 $1,000 举例，60 岁是 ${c['f60'] * 1000:,.0f}，70 岁是 ${c['f70'] * 1000:,.0f}。按今天的钱算，没算早领的钱拿去投资的回报，也没算税。60 岁对 70 岁，在 {c['c6070']:.0f} 岁左右追上。</p></div>""",
                    limits=[("追上的年龄是简化算的。", "没算早领的钱拿去投资能赚多少，也没算税；CPP 的金额还取决于你缴了多少年。"),
                            ("这里只讲规则，不说你该几岁领。", "这取决于身体、其他收入、有没有配偶，是个人的决定。"),
                            ("新移民的 OAS 往往不是全额。", "住满 40 年的规则对很多人很要紧。")],
                    sources=[("加拿大政府，CPP「When to start your retirement pension」，页面日期 2026 年 10 月 2 日。", "早领每月少 0.6%，最多少 36%；晚领每月多 0.7%，最多多 42%。"),
                             ("加拿大政府，OAS「When to start」，页面日期 2026 年 10 月 2 日。", "晚领每月多 0.6%，最多多 36%；40 年居住的规则。")])},
    ]


# ---------------------------------------------------------------- the layout
CSS = """
.crumb, .art .crumb { font-size:14px; color:var(--muted); margin:36px 0 10px; }
.crumb a { text-decoration:none; color:var(--ink-2); } .crumb a:hover { text-decoration:underline; }
.pg { display:grid; grid-template-columns:minmax(0,760px) 240px; gap:56px; align-items:start; }
.pg > * { min-width:0; }
.side-n { display:none; margin:34px 0 0; font-size:15px; }
.side-n h3 { font-size:13px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:0 0 8px; }
.side-n a { display:block; text-decoration:none; color:var(--ink-2); padding:8px 0 8px 12px; border-left:2px solid var(--grid); }
.side-n a.on { color:var(--ink); font-weight:700; border-left-color:var(--btn); }
@media (max-width:1100px) { .pg { grid-template-columns:1fr; } .side { display:none; } .side-n { display:block; } }
.side { position:sticky; top:84px; margin-top:96px; font-size:15px; }
.side h3 { font-size:13px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:0 0 8px; }
.side a { display:block; text-decoration:none; color:var(--ink-2); padding:6px 0 6px 12px; border-left:2px solid var(--grid); }
.side a.on { color:var(--ink); font-weight:700; border-left-color:var(--btn); }
.art h1 { font-size:clamp(28px,3vw,40px); margin:0 0 14px; }
.art .lede { font-size:19px; margin:0 0 30px; color:var(--ink-2); }
.art h2 { font-size:20px; letter-spacing:-.01em; margin:34px 0 10px; }
.art p { margin:0 0 12px; color:var(--ink-2); }
.calc, .chart { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:18px 20px; margin:6px 0 8px; }
.calc label { display:flex; align-items:center; gap:12px; font-weight:600; flex-wrap:wrap; }
.calc input { font:inherit; font-size:20px; font-weight:700; width:150px; padding:6px 10px; border:1px solid var(--border); border-radius:8px; background:#fff; font-variant-numeric:tabular-nums; }
.rows { margin:14px 0 0; }
.rows div { display:flex; justify-content:space-between; border-top:1px solid var(--grid); padding:9px 0; font-variant-numeric:tabular-nums; }
.rows div b { font-size:22px; }
.formula, .note { font-size:14px; color:var(--muted); margin:10px 0 0; }
.chart svg { display:block; width:100%; height:auto; }
.chart svg text { font:12px system-ui,-apple-system,"PingFang SC",sans-serif; fill:var(--muted); }
.read { display:flex; flex-wrap:wrap; gap:6px 22px; font-size:15px; margin:10px 0 0; font-variant-numeric:tabular-nums; }
.read b { font-size:17px; }
.slide { display:flex; align-items:center; gap:14px; margin:4px 0 12px; font-weight:600; flex-wrap:wrap; }
.slide input { flex:1; min-width:180px; accent-color:var(--btn); }
.slide output { min-width:64px; text-align:right; font-variant-numeric:tabular-nums; }
.tblw { overflow-x:auto; margin:4px 0 8px; }
.tbl { width:100%; border-collapse:collapse; font-size:15px; }
.tbl th, .tbl td { text-align:left; padding:9px 10px 9px 0; border-top:1px solid var(--grid); vertical-align:top; }
.tbl th { font-size:13px; color:var(--muted); font-weight:600; }
.tbl td.n { font-variant-numeric:tabular-nums; }
@media (max-width:600px) { .tbl { font-size:13.5px; } }
.src { margin:0; padding:0; list-style:none; }
.src li { border-top:1px solid var(--grid); padding:12px 0; color:var(--ink-2); font-size:15.5px; }
.src li b { color:var(--ink); font-weight:600; }
.cta { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:22px; margin:34px 0 0; }
.cta p { margin:0 0 14px; }
.pn { display:flex; justify-content:space-between; gap:16px; margin:34px 0 0; padding:18px 0 0; border-top:1px solid var(--grid); font-size:15.5px; }
.pn a { text-decoration:none; color:var(--ink-2); } .pn a b { color:var(--ink); }
.checked { font-size:14px; color:var(--muted); margin:18px 0 56px; }
section.stage { padding:0; margin:40px 0 0; }
.stage h2 { font-size:22px; margin:0 0 2px; }
.stage .q { color:var(--muted); margin:0 0 10px; }
.stops { margin:0; padding:0; list-style:none; max-width:760px; }
.stops li { border-top:1px solid var(--grid); padding:12px 0; }
.stops a { font-weight:700; color:var(--ink); text-decoration:none; } .stops a:hover { text-decoration:underline; }
.stops span { display:block; color:var(--ink-2); font-size:15px; }
"""


def head(lang, title, desc, url, alt_en, alt_zh, up, css, ld=None):
    return f"""<!doctype html>
<!-- Built by docs/site/make.py and docs/site/path.py; edit those, not this. -->
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} — FIRE Toad</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="zh" href="{alt_zh}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
<link rel="icon" href="{up}logo.svg" type="image/svg+xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="FIRE Toad">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
{'<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' if ld else ''}
<style>{css}{CSS}</style>
</head>
<body>"""


def top(lang, up, other_href, w):
    return f"""<header class="top"><div class="wrap">
  <a class="brand" href="{up}{'zh/' if lang == 'zh' else ''}"><img src="{up}logo.svg" alt="">FIRE Toad</a>
  <nav><a class="road" href="{up}{'zh/' if lang == 'zh' else ''}path/">{e(w['road'])}</a><a class="sec" href="{up}{'zh/' if lang == 'zh' else ''}">{e(w['how'])}</a><a href="{other_href}" hreflang="{'en' if lang == 'zh' else 'zh'}" lang="{'en' if lang == 'zh' else 'zh'}">{w['other']}</a></nav>
</div></header>"""


def stop_page(st, lang, base, css, published, download):
    w, t = WORDS[lang], st[lang]
    up = "../../../" if lang == "zh" else "../../"
    pre = f"{base}/{'zh/' if lang == 'zh' else ''}"
    url, alt_en, alt_zh = f"{pre}path/{st['slug']}/", f"{base}/path/{st['slug']}/", f"{base}/zh/path/{st['slug']}/"
    i = published.index(st)
    prev, nxt = (published[i - 1] if i else None), (published[i + 1] if i + 1 < len(published) else None)
    same = [s for s in published if s["stage"] == st["stage"]]
    side = "".join(f'<a href="../{s["slug"]}/" class="{"on" if s is st else ""}">{e(s[lang]["name"])}</a>' for s in same)
    pn = ((f'<a href="../{prev["slug"]}/">← {e(w["prev"])}<br><b>{e(prev[lang]["name"])}</b></a>' if prev else "<span></span>")
          + (f'<a href="../{nxt["slug"]}/" style="text-align:right">{e(w["next"])} →<br><b>{e(nxt[lang]["name"])}</b></a>' if nxt else ""))
    lim = "".join(f"<li><b>{e(a)}</b><br>{e(b)}</li>" for a, b in t["limits"])
    src = "".join(f"<li><b>{e(a)}</b><br>{e(b)}</li>" for a, b in t["sources"])
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": t["title"], "description": t["desc"],
          "inLanguage": lang, "url": url, "dateModified": "2026-11", "publisher": {"@type": "Organization", "name": "FIRE Toad"}}
    other = f"../../{'../' if lang == 'zh' else 'zh/'}path/{st['slug']}/"
    return (head(lang, t["title"], t["desc"], url, alt_en, alt_zh, up, css, ld) + top(lang, up, other, w) + f"""
<main class="wrap"><div class="pg"><div class="art">
  <p class="crumb"><a href="../">{e(w['road'])}</a> › <a href="../#{w['anchors'][st['stage']]}">{e(w['stages'][st['stage']])}</a></p>
  <h1>{e(t['title'])}</h1>
  <p class="lede">{e(t['lede'])}</p>
  <h2>{e(w['why'])}</h2><p>{e(t['why'])}</p>
  {t['body']}
  {f'<h2>{e(w["src"])}</h2><ul class="src">{src}</ul>' if src else ''}
  <h2>{e(w['limits'])}</h2><ul class="src">{lim}</ul>
  <div class="cta"><p>{e(w['cta'])}</p><div class="actions"><a class="btn primary" href="{download}">{e(w['download'])}</a><a class="btn secondary" href="{up}dashboard.html?lang={lang}">{e(w['demo'])}</a></div></div>
  <nav class="side-n"><h3>{e(w['stages'][st['stage']])}</h3>{side}</nav>
  <div class="pn">{pn}</div>
  <p class="checked">{e(CHECKED[lang])}</p>
</div><aside class="side"><h3>{e(w['stages'][st['stage']])}</h3>{side}</aside></div></main>
<script>{SLIDE_JS}
{st['js']}</script>
</body>
</html>
""")


def index_page(lang, base, css, published, download):
    w = WORDS[lang]
    up = "../../" if lang == "zh" else "../"
    url = f"{base}/{'zh/' if lang == 'zh' else ''}path/"
    parts = []
    for k, name in enumerate(w["stages"]):
        rows = [s for s in published if s["stage"] == k]
        if rows:
            lis = "".join(f'<li><a href="{s["slug"]}/">{e(s[lang]["title"])}</a><span>{e(s[lang]["line"])}</span></li>' for s in rows)
            parts.append(f'<section class="stage" id="{w["anchors"][k]}"><h2>{e(name)}</h2><p class="q">{e(w["stage_q"][k])}</p><ul class="stops">{lis}</ul></section>')
    other = "../../path/" if lang == "zh" else "../zh/path/"
    return (head(lang, w["road"], w["index_lede"], url, f"{base}/path/", f"{base}/zh/path/", up, css) + top(lang, up, other, w) + f"""
<main class="wrap"><div class="art" style="max-width:760px">
  <p class="crumb">FIRE Toad</p>
  <h1>{e(w['road'])}</h1>
  <p class="lede">{e(w['index_lede'])}</p>
  {''.join(parts)}
  <div class="cta" style="margin-bottom:56px"><p>{e(w['index_cta'])}</p><div class="actions"><a class="btn primary" href="{download}">{e(w['download'])}</a><a class="btn secondary" href="{up}dashboard.html?lang={lang}">{e(w['demo'])}</a></div></div>
</div></main>
</body>
</html>
""")


def build(dst, base, css, repo, download):
    """Write every published stop and the index in both languages under dst; return the addresses
    for the sitemap, relative to the site's root."""
    published = sorted(stops(repo), key=lambda s: [int(x) for x in s["id"].split(".")])
    urls = []
    for lang in ("en", "zh"):
        root = os.path.join(dst, "zh" if lang == "zh" else "", "path")
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_page(lang, base, css, published, download))
        urls.append(f"{'zh/' if lang == 'zh' else ''}path/")
        for st in published:
            d = os.path.join(root, st["slug"])
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
                f.write(stop_page(st, lang, base, css, published, download))
            urls.append(f"{'zh/' if lang == 'zh' else ''}path/{st['slug']}/")
    return urls
