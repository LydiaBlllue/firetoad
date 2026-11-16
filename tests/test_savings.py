"""savings.py — the savings rate and the years it takes (FINANCE.md §1a). One test per rule."""
import unittest
import _paths
import savings


def month(ym, amount):
    return {"date": ym + "-10", "amount": amount, "currency": "CAD", "category": "Groceries"}


END = {"card": "2026-06-30"}
SPEND = [month("2026-0%d" % i, 2000) for i in (1, 2, 3, 4, 5)]
CASH = [{"ym": "2026-0%d" % i, "payroll": 4000, "other": 0} for i in (1, 2, 3, 4, 5)]


class TheYears(unittest.TestCase):

    def test_saving_half_from_nothing_takes_about_seventeen_years_at_five_percent(self):
        # the table in KNOWLEDGE 0.6: 50% at 5% is 17 years
        self.assertAlmostEqual(savings.years(0, 4000, 2000, 0.05), 17.0, delta=0.6)

    def test_what_is_already_invested_shortens_it(self):
        self.assertLess(savings.years(100000, 4000, 2000, 0.05), savings.years(0, 4000, 2000, 0.05))

    def test_a_portfolio_that_reaches_the_target_is_already_there(self):
        self.assertEqual(savings.years(2000 * 12 * 25, 4000, 2000, 0.05), 0.0)

    def test_saving_nothing_has_no_years(self):
        self.assertIsNone(savings.years(0, 2000, 2000, 0.05))
        self.assertIsNone(savings.years(0, 2000, 2500, 0.05))


class TheRate(unittest.TestCase):

    def test_it_is_what_is_left_of_what_work_delivered(self):
        r = savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)
        self.assertEqual(r["rate"], 0.5)
        self.assertEqual((r["income"], r["spend"], r["n"]), (4000, 2000, 5))

    def test_a_gift_is_not_income(self):
        cash = [dict(c, gift=5000) for c in CASH]
        self.assertEqual(savings.measured(cash, SPEND, END, {}, "2026-07-15", 0)["rate"], 0.5)

    def test_other_income_counts(self):
        cash = [dict(c, other=1000) for c in CASH]
        self.assertEqual(savings.measured(cash, SPEND, END, {}, "2026-07-15", 0)["rate"], 0.6)

    def test_fewer_than_three_months_is_not_enough(self):
        self.assertEqual(savings.measured(CASH[:2], SPEND[:2], END, {}, "2026-07-15", 0), {})

    def test_a_month_set_aside_is_left_out(self):
        spend = SPEND + [month("2026-06", 9000)]
        cash = CASH + [{"ym": "2026-06", "payroll": 4000, "other": 0}]
        with_it = savings.measured(cash, spend, END, {}, "2026-08-01", 0)["rate"]
        without = savings.measured(cash, spend, END, {"2026-06": "moving"}, "2026-08-01", 0)["rate"]
        self.assertLess(with_it, without)
        self.assertEqual(without, 0.5)

    def test_a_month_with_no_income_does_not_count(self):
        cash = CASH[:4] + [{"ym": "2026-05", "payroll": 0, "other": 0}]
        self.assertEqual(savings.measured(cash, SPEND, END, {}, "2026-07-15", 0)["n"], 4)

    def test_a_negative_rate_is_said_as_it_is(self):
        spend = [month("2026-0%d" % i, 5000) for i in (1, 2, 3)]
        r = savings.measured(CASH[:3], spend, END, {}, "2026-07-15", 0)
        self.assertEqual(r["rate"], -0.25)
        self.assertEqual(r["years"], [None, None, None])


class TheCurve(unittest.TestCase):

    def test_it_runs_from_nothing_to_ninety_in_steps_of_five(self):
        c = savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)["curve"]
        self.assertEqual([p["pct"] for p in c], list(range(0, 95, 5)))

    def test_saving_more_is_never_slower(self):
        c = savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)["curve"]
        ys = [p["years"][2] for p in c if p["years"][2] is not None]
        self.assertEqual(ys, sorted(ys, reverse=True))

    def test_saving_nothing_has_no_years_on_the_curve(self):
        self.assertEqual(savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)["curve"][0]["years"], [None] * 3)


class TheSlider(unittest.TestCase):

    def test_it_is_in_dollars_from_nothing_more(self):
        m = savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)["more"]
        self.assertEqual((m[0]["more"], m[1]["more"], m[-1]["more"]), (0, 50, 1000))

    def test_nothing_more_is_today(self):
        r = savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)
        self.assertEqual(r["more"][0]["years"], r["years"])
        self.assertEqual(r["more"][0]["pct"], 50.0)

    def test_keeping_more_is_never_slower(self):
        m = savings.measured(CASH, SPEND, END, {}, "2026-07-15", 0)["more"]
        ys = [x["years"][1] for x in m]
        self.assertEqual(ys, sorted(ys, reverse=True))


if __name__ == "__main__":
    unittest.main()
