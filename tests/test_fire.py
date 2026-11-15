"""fire.py — the FIRE figures at the plan's own values (FINANCE.md §1). One test per rule."""
import unittest
import _paths
import fire


class TheTarget(unittest.TestCase):

    def test_it_is_twenty_five_years_of_the_planning_figure(self):
        self.assertEqual(fire.target(3000), 900000)

    def test_no_planning_figure_is_no_target(self):
        self.assertEqual(fire.target(None), 0)
        self.assertEqual(fire.progress(50000, 0), 0)

    def test_progress_is_a_share_to_one_decimal(self):
        self.assertEqual(fire.progress(123456, 900000), 13.7)

    def test_a_half_rounds_up_as_the_page_rounds_it(self):
        self.assertEqual(fire.js_round(0.5), 1)
        self.assertEqual(fire.js_round(2.5), 3)
        self.assertEqual(fire.gap(99999.5, 200000), 100001)


class TheProjection(unittest.TestCase):

    def test_a_month_compounds_then_adds_the_contribution(self):
        self.assertEqual(fire.project(1000, 0.12, 2, 100), [1000, 1110.0, 1221.1])

    def test_no_months_is_just_today(self):
        self.assertEqual(fire.project(1000, 0.05, 0, 100), [1000])

    def test_the_target_is_crossed_at_the_first_month_at_or_over_it(self):
        self.assertEqual(fire.cross_month([1, 2, 3, 4], 3), 2)
        self.assertEqual(fire.cross_month([5, 6], 3), 0)

    def test_a_target_never_reached_has_no_month(self):
        self.assertIsNone(fire.cross_month([1, 2, 3], 10))


class Coasting(unittest.TestCase):

    def test_already_there_is_todays_age(self):
        self.assertEqual(fire.coast_age(900000, 900000, 0.05, 32, 95), 32)

    def test_doubling_at_five_percent_takes_about_fourteen_years(self):
        self.assertAlmostEqual(fire.coast_age(450000, 900000, 0.05, 32, 95), 46.2067, places=3)

    def test_beyond_the_plans_last_year_is_never(self):
        self.assertIsNone(fire.coast_age(1000, 900000, 0.05, 32, 95))

    def test_nothing_invested_never_coasts(self):
        self.assertIsNone(fire.coast_age(0, 900000, 0.05, 32, 95))


class TheConstant(unittest.TestCase):

    def figures(self, **kw):
        a = dict(portfolio=100000, plan_base=3000, contrib=2000, scenarios=[{"r": 0.05}, {"r": 0.09}], horizon=25,
                 anchor_year=2026, today="2027-03-10", coast_r=0.05, born=1995, life_to=95)
        a.update(kw)
        return fire.figures(**a)

    def test_it_carries_every_figure_the_page_shows(self):
        f = self.figures()
        self.assertEqual((f["target"], f["pct"], f["gap"]), (900000, 11.1, 800000))
        self.assertEqual(len(f["cross"]), 2)
        self.assertLess(f["cross"][1], f["cross"][0])            # a higher return gets there sooner

    def test_the_months_looked_at_stop_at_the_horizon_from_the_anchor_year(self):
        # 25 years from January 2026, seen from March 2027: 300 - 14 months are left to look at
        f = self.figures(contrib=0, scenarios=[{"r": 0.0}], portfolio=1)
        self.assertEqual(f["cross"], [None])
        self.assertEqual(self.figures(horizon=1)["cross"], [None, None])

    def test_no_year_of_birth_is_no_coast_age(self):
        self.assertIsNone(self.figures(born=None)["coastAge"])

    def test_no_planning_figure_leaves_the_numbers_empty_not_broken(self):
        f = self.figures(plan_base=None)
        self.assertEqual((f["target"], f["pct"], f["coastAge"]), (0, 0, None))


if __name__ == "__main__":
    unittest.main()
