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
        a = dict(portfolio=100000, plan_base=3000, today="2027-03-10", coast_r=0.05, born=1995, life_to=95)
        a.update(kw)
        return fire.figures(**a)

    def test_it_carries_every_figure_the_page_shows(self):
        f = self.figures()
        self.assertEqual((f["target"], f["pct"], f["gap"]), (900000, 11.1, 800000))
        self.assertEqual(sorted(f), ["coastAge", "gap", "pct", "target"])

    def test_no_year_of_birth_is_no_coast_age(self):
        self.assertIsNone(self.figures(born=None)["coastAge"])

    def test_no_planning_figure_leaves_the_numbers_empty_not_broken(self):
        f = self.figures(plan_base=None)
        self.assertEqual((f["target"], f["pct"], f["coastAge"]), (0, 0, None))


if __name__ == "__main__":
    unittest.main()
