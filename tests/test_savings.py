"""savings.py — years to financial independence and the savings rate (FINANCE.md §1a). One test per rule."""
import unittest
import _paths
import savings


def month(ym, amount):
    return {"date": ym + "-10", "amount": amount, "currency": "CAD", "category": "Groceries"}


END = {"card": "2026-06-30"}
SPEND = [month("2026-0%d" % i, 2000) for i in (1, 2, 3, 4, 5)]
CASH = [{"ym": "2026-0%d" % i, "payroll": 4000, "other": 0} for i in (1, 2, 3, 4, 5)]
DEP = [{"ym": "2026-0%d" % i, "amt": a} for i, a in ((3, 900), (4, 600), (5, 700), (6, 800), (7, 100))]
TODAY = "2026-07-15"


def m(**kw):
    a = dict(cashflow=CASH, spending=SPEND, stmt_end=END, skip={}, today=TODAY, portfolio=0)
    a.update(kw)
    return savings.measured(**a)


class TheYears(unittest.TestCase):

    def test_saving_half_from_nothing_takes_about_seventeen_years_at_five_percent(self):
        # KNOWLEDGE 0.6: 50% at 5% is 17 years — target 25 years of $2,000, $2,000 a month added
        self.assertAlmostEqual(savings.years_to(0, 2000 * 300, 2000, 0.05), 17.0, delta=0.6)

    def test_what_is_already_invested_shortens_it(self):
        self.assertLess(savings.years_to(100000, 600000, 2000, 0.05), savings.years_to(0, 600000, 2000, 0.05))

    def test_a_portfolio_that_reaches_the_target_is_already_there(self):
        self.assertEqual(savings.years_to(600000, 600000, 0, 0.05), 0.0)

    def test_adding_nothing_has_no_years(self):
        self.assertIsNone(savings.years_to(1000, 600000, 0, 0.05))


class ThePace(unittest.TestCase):

    def test_it_is_what_reached_the_broker_over_the_last_three_full_months(self):
        self.assertEqual(savings.pace(DEP, TODAY, 500), (700.0, 3))

    def test_with_nothing_seen_arriving_it_is_the_plan(self):
        self.assertEqual(savings.pace([], TODAY, 500), (500.0, 0))

    def test_the_answer_is_at_the_pace(self):
        r = m(wsdep=DEP, plan_invest=500, plan_base=2000)
        self.assertEqual(r["invest"], 700.0)
        self.assertEqual(r["years"][1], round(savings.years_to(0, 600000, 700, 0.05), 1))


class TheReturn(unittest.TestCase):

    def test_it_is_the_setting_and_one_point_either_side(self):
        self.assertEqual(m(plan_base=2000, plan_invest=500)["returns"], [0.04, 0.05, 0.06])
        self.assertEqual(m(plan_base=2000, plan_invest=500, growth=7)["returns"], [0.06, 0.07, 0.08])

    def test_a_higher_return_is_never_slower(self):
        lo, hi = m(plan_base=2000, plan_invest=500, growth=4), m(plan_base=2000, plan_invest=500, growth=7)
        self.assertLess(hi["years"][1], lo["years"][1])


class TheTarget(unittest.TestCase):

    def test_it_is_the_planning_figure_when_there_is_one(self):
        self.assertEqual(m(plan_base=3000)["target"], 900000)

    def test_else_what_is_really_spent(self):
        self.assertEqual(m()["target"], 600000)

    def test_with_neither_there_is_nothing_to_say(self):
        self.assertEqual(m(cashflow=CASH[:2], spending=SPEND[:2]), {})


class TheRate(unittest.TestCase):

    def test_it_is_what_is_left_of_what_work_delivered(self):
        r = m()
        self.assertEqual(r["rate"], 0.5)
        self.assertEqual((r["income"], r["spend"], r["n"], r["keep"]), (4000, 2000, 5, 2000))

    def test_a_gift_is_not_income(self):
        self.assertEqual(m(cashflow=[dict(c, gift=5000) for c in CASH])["rate"], 0.5)

    def test_other_income_counts(self):
        self.assertEqual(m(cashflow=[dict(c, other=1000) for c in CASH])["rate"], 0.6)

    def test_fewer_than_three_months_has_no_rate(self):
        r = m(cashflow=CASH[:2], spending=SPEND[:2], plan_base=2000, plan_invest=500)
        self.assertNotIn("rate", r)
        self.assertIn("years", r)

    def test_a_month_set_aside_is_left_out(self):
        spend = SPEND + [month("2026-06", 9000)]
        cash = CASH + [{"ym": "2026-06", "payroll": 4000, "other": 0}]
        with_it = m(cashflow=cash, spending=spend, today="2026-08-01")["rate"]
        without = m(cashflow=cash, spending=spend, today="2026-08-01", skip={"2026-06": "moving"})["rate"]
        self.assertLess(with_it, without)
        self.assertEqual(without, 0.5)

    def test_a_month_with_no_income_does_not_count(self):
        cash = CASH[:4] + [{"ym": "2026-05", "payroll": 0, "other": 0}]
        self.assertEqual(m(cashflow=cash)["n"], 4)


class WhatIsKept(unittest.TestCase):

    def test_it_is_split_by_its_job_and_the_rest_has_none(self):
        r = m(wsdep=DEP, set_aside=[("Emergency fund", 300)])
        self.assertEqual(r["jobs"], [["Invested", 700.0], ["Emergency fund", 300.0]])
        self.assertEqual(r["free"], 1000.0)

    def test_more_set_aside_than_kept_is_said_as_it_is(self):
        self.assertEqual(m(wsdep=DEP, set_aside=[("Emergency fund", 1500)])["free"], -200.0)


class TheSlider(unittest.TestCase):

    def test_it_is_in_dollars_from_nothing_more(self):
        s = m(plan_invest=500)["more"]
        self.assertEqual((s[0]["more"], s[1]["more"], s[-1]["more"]), (0, 50, 1000))

    def test_nothing_more_is_today(self):
        r = m(plan_invest=500)
        self.assertEqual(r["more"][0]["years"], r["years"])

    def test_investing_more_is_never_slower(self):
        ys = [x["years"][1] for x in m(plan_invest=500)["more"]]
        self.assertEqual(ys, sorted(ys, reverse=True))


if __name__ == "__main__":
    unittest.main()
