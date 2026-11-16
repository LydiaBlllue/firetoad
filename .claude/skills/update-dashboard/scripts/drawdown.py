"""drawdown.py — living on the portfolio, year by year, and late-life care (FINANCE.md §1, §8d).

The Drawdown page lets the owner move four ages and a care tier and redraws as they move, so
the page keeps these sums. But what the plan comes to at the ages it starts from was known only
inside the browser. It is computed here, once, at those ages (the DRAWDOWN constant): how long
the money lasts, what is short once it has run out, what is there the day the drawing starts, how much more care would need, and
how many starting years on record the plan would have survived.

check_render's R8 asks the built page for the same figures at the same ages and fails when they
differ, so the page's sums and these cannot drift apart.

Pure: numbers in, numbers out. Every amount is in today's money a month; every return is real.
"""
# The ages the page starts from, until the owner moves them. They were literals in the page.
DRAW_AGE, CARE_AGE, LTC_AGE, LTC_TIER = 55, 80, 88, 0


def js_round(x):
    import math
    return math.floor(x + 0.5)


def ages(age_now, life_to, draw=DRAW_AGE, care=CARE_AGE, ltc=LTC_AGE, stop=None, tier=LTC_TIER):
    """The four ages, each no earlier than the one before it: stop adding, start drawing, care
    at home, a care home."""
    stop = max(age_now, age_now if stop is None else stop)
    draw = max(stop + 1, draw)
    care = max(draw, care)
    ltc = max(care, ltc)
    return {"stop": stop, "draw": draw, "care": care, "ltc": ltc, "tier": tier}


def pension_at(age, pensions):
    return sum(p["v"] for p in pensions or [] if age >= p["from"])


def take_out(age, spend, pensions):
    """What leaves the portfolio: the spending less the pensions already being paid."""
    return max(0, spend - pension_at(age, pensions)) if spend > 0 else 0


def care_at(age, care_a, ltc_a, ltc, home, age_now):
    """What care costs a month at this age: nothing before it starts, care at home from
    `care_a`, a care home from `ltc_a` — each rising at its own rate above inflation."""
    if care_a is None:
        return 0
    if ltc_a is not None and age >= ltc_a:
        return ltc["v"] * (1 + ltc["esc"]) ** (age - age_now)
    if age >= care_a:
        return home["v"] * (1 + home["esc"]) ** (age - age_now)
    return 0


def run(p0, r, contrib, draw_m, stop_a, start_a, care_a, ltc_a, ltc, home, pensions, age_now, life_to):
    """{series, dead, short}: the portfolio month by month to the plan's last year, the age it
    runs out (None when it does not), and the shortfall — what was still to pay in the months
    it could not pay, added up. Once it runs out it is nothing in every month after: a
    portfolio is not a loan. The shortfall is a plain sum in today's money; it assumes nothing
    about where that money would come from or what borrowing it would cost."""
    m, v, out, dead, short = r / 12, p0, [p0], None, 0
    for i in range(1, (life_to - age_now) * 12 + 1):
        age = age_now + (i - 1) / 12
        v = v * (1 + m) + (contrib if age < stop_a else 0) \
            - take_out(age, (draw_m if age >= start_a else 0) + care_at(age, care_a, ltc_a, ltc, home, age_now), pensions)
        if v <= 0:
            short += -v
            dead, v = (age_now + i / 12 if dead is None else dead), 0
        out.append(v)
    return {"series": out, "dead": dead, "short": short}


def extra_needed(series, r, draw_m, care_a, ltc_a, ltc, home, pensions, age_now, life_to):
    """How much more would have to be held the day care starts for the money to reach the
    plan's last year. Solved, not subtracted: the day care begins the runs with and without
    it are still the same."""
    at = js_round((care_a - age_now) * 12)
    if at >= len(series) or at < 0:
        return None
    base, m = series[at], r / 12

    def survives(lump):
        v = base + lump
        for i in range(at + 1, (life_to - age_now) * 12 + 1):
            age = age_now + (i - 1) / 12
            v = v * (1 + m) - take_out(age, draw_m + care_at(age, care_a, ltc_a, ltc, home, age_now), pensions)
            if v <= 0:
                return False
        return True
    if survives(0):
        return 0
    lo, hi = 0, 1e7
    for _ in range(40):
        mid = (lo + hi) / 2
        if survives(mid):
            hi = mid
        else:
            lo = mid
    return hi


def backtest(pot0, draw_m, draw_a, care_a, ltc_a, ltc, home, pensions, years, age_now, life_to):
    """Every starting year on record, replayed: the pot the drawing starts with, taken through
    that year's real returns and the ones after it. {runs, ok, n, N, from, to}, or None when
    there is nothing to replay (no record, no pot, or a retirement longer than the record)."""
    n_years = life_to - draw_a
    if not years or pot0 <= 0 or n_years < 1 or n_years > len(years):
        return None
    runs = []
    for s in range(0, len(years) - n_years + 1):
        v, dead = pot0, None
        for j in range(n_years):
            m = (1 + years[s + j][1]) ** (1 / 12) - 1
            for k in range(12):
                age = draw_a + j + k / 12
                v = v * (1 + m) - take_out(age, draw_m + care_at(age, care_a, ltc_a, ltc, home, age_now), pensions)
                if v <= 0:
                    dead, v = age, 0
                    break
            if dead is not None:
                break
        runs.append({"y": years[s][0], "end": v, "dead": dead})
    return {"runs": runs, "ok": sum(1 for x in runs if x["dead"] is None), "n": len(runs), "N": n_years,
            "from": years[0][0], "to": years[-1][0]}


def now(at, portfolio, r, contrib, draw_m, tiers, home, pensions, years, age_now, life_to):
    """The plan at the given ages: what the Drawdown page says before anything is moved."""
    ltc = tiers[at["tier"]]
    ltc_a = None if at["ltc"] >= life_to else at["ltc"]
    go = lambda care_a, l_a: run(portfolio, r, contrib, draw_m, at["stop"], at["draw"], care_a, l_a, ltc, home, pensions, age_now, life_to)
    main = go(at["care"], ltc_a)
    pick = lambda a: main["series"][js_round((a - age_now) * 12)] if 0 <= js_round((a - age_now) * 12) < len(main["series"]) else None
    at_draw = pick(at["draw"]) or 0
    bt = backtest(at_draw, draw_m, at["draw"], at["care"], ltc_a, ltc, home, pensions, years, age_now, life_to)
    # Money that runs out before care begins has no "extra for care": everything after it is
    # the shortfall, and a lump for care alone would be a number about nothing.
    broke_first = main["dead"] is not None and main["dead"] <= at["care"]
    return {"dead": main["dead"], "short": main["short"], "atDraw": at_draw, "atStop": pick(at["stop"]) or portfolio,
            "noCareDead": go(None, None)["dead"], "stayHomeDead": go(at["care"], None)["dead"],
            "extra": None if broke_first else extra_needed(main["series"], r, draw_m, at["care"], ltc_a, ltc, home, pensions, age_now, life_to),
            "bt": {k: bt[k] for k in ("ok", "n", "N", "from", "to")} if bt else None}


def figures(portfolio, plan_base, contrib, r, tiers, home, pensions, years, born, life_to, today, fi_years=None):
    """The DRAWDOWN constant: `at` (the ages the page starts from) and `now` (the plan at them).
    Empty when there is no year of birth, no planning figure or no care tier to price."""
    if not born or not tiers or not home or not life_to:
        return {}
    age_now = int(today[:4]) - born
    if life_to <= age_now:
        return {}
    # The page starts where the FIRE page ends (2026-11-15, user 001): adding until the year the
    # money reaches the target, and taking from the year after. Without that year, the old ages.
    if fi_years is not None:
        import math
        stop = age_now + math.ceil(fi_years)
        at = ages(age_now, life_to, draw=stop + 1, stop=stop)
    else:
        at = ages(age_now, life_to)
    return {"at": at, "now": now(at, portfolio, r, contrib or 0, plan_base or 0, tiers, home, pensions, years, age_now, life_to)}
