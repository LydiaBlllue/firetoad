"""fire.py — the FIRE figures at the plan's own values (FINANCE.md §1).

The target, how far along the portfolio is, and how many months each return takes to reach it
were the page's own arithmetic, and FINANCE.md's figures table worked the first three out a
second time. They are computed here, once: rebuild.py hands the page the result (the FIRE
constant) and writes the figures table from the same numbers.

The page keeps the same formulas, because it redraws while a number is being changed, before
the change is saved and the page rebuilt. Two copies of one sum drift unless something holds
them together: check_render's R8 asks the built page for its own figures and fails when they
are not these.

Pure: numbers in, numbers out.
"""
import math

YEARS = 25              # the 4% rule: a year of spending, twenty-five times


def js_round(x):
    """Math.round: a half goes up, where Python's round() goes to the even neighbour."""
    return math.floor(x + 0.5)


def target(plan_base):
    return (plan_base or 0) * 12 * YEARS


def progress(portfolio, tgt):
    """The portfolio as a share of the target, in percent to one decimal; 0 with no target."""
    return js_round(portfolio / tgt * 1000) / 10 if tgt else 0


def gap(portfolio, tgt):
    return js_round(tgt - portfolio)


def coast_age(p0, tgt, r, age_now, life_to):
    """The age at which the portfolio, with nothing more added, grows to the target by itself;
    today's age when it is already there, None when that is beyond the plan's last year."""
    if tgt <= 0 or p0 >= tgt:
        return age_now
    if p0 <= 0 or r <= 0:
        return None
    yrs = math.log(tgt / p0) / math.log(1 + r)
    return None if yrs > life_to - age_now else age_now + yrs


def figures(portfolio, plan_base, today, coast_r, born, life_to):
    """The FIRE constant: the target, how far along the portfolio is, what is still to go, and
    `coastAge`, the age the portfolio coasts to the target from. (Months to go at each return,
    for the three-line trajectory, went with it in 1.0.6: the years are savings.py's.)"""
    tgt = target(plan_base)
    age_now = int(today[:4]) - born if born else None
    return {"target": tgt, "pct": progress(portfolio, tgt), "gap": gap(portfolio, tgt),
            "coastAge": coast_age(portfolio, tgt, coast_r, age_now, life_to) if age_now is not None and tgt > 0 else None}
