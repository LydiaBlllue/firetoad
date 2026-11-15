"""drawdown.py — living on the portfolio and late-life care (FINANCE.md §1, §8d). One test per rule."""
import unittest
import _paths
import drawdown as dd

HOME = {"v": 4000, "esc": 0.0}
LTC = {"v": 2000, "esc": 0.0}


def run(p0=0, r=0.0, contrib=0, draw=0, stop=30, start=40, care=None, ltc_a=None, pensions=None, now=30, life=50):
    return dd.run(p0, r, contrib, draw, stop, start, care, ltc_a, LTC, HOME, pensions, now, life)


class TheAges(unittest.TestCase):

    def test_each_age_is_no_earlier_than_the_one_before(self):
        self.assertEqual(dd.ages(60, 95), {"stop": 60, "draw": 61, "care": 80, "ltc": 88, "tier": 0})
        self.assertEqual(dd.ages(85, 95)["care"], 86)
        self.assertEqual(dd.ages(85, 95)["ltc"], 88)

    def test_stopping_now_is_the_start(self):
        self.assertEqual(dd.ages(30, 95)["stop"], 30)


class WhatLeavesThePortfolio(unittest.TestCase):

    def test_a_pension_pays_part_of_the_spending_from_its_age(self):
        p = [{"v": 700, "from": 65}]
        self.assertEqual(dd.take_out(64, 3000, p), 3000)
        self.assertEqual(dd.take_out(65, 3000, p), 2300)

    def test_a_pension_bigger_than_the_spending_adds_nothing_to_the_pot(self):
        self.assertEqual(dd.take_out(70, 500, [{"v": 700, "from": 65}]), 0)

    def test_care_at_home_then_a_home_each_from_its_age(self):
        c = lambda age: dd.care_at(age, 80, 88, LTC, HOME, 30)
        self.assertEqual([c(79), c(80), c(88)], [0, 4000, 2000])

    def test_care_rises_with_its_own_rate_from_today(self):
        self.assertAlmostEqual(dd.care_at(32, 31, None, LTC, {"v": 1000, "esc": 0.1}, 30), 1210)

    def test_never_moving_to_a_home_stays_at_home(self):
        self.assertEqual(dd.care_at(90, 80, None, LTC, HOME, 30), 4000)


class TheRun(unittest.TestCase):

    def test_it_adds_until_the_stop_age_then_only_grows(self):
        s = run(p0=0, contrib=100, stop=31)["series"]
        self.assertEqual((s[12], s[13], s[-1]), (1200, 1200, 1200))

    def test_it_draws_from_the_start_age_and_says_when_it_runs_out(self):
        r = run(p0=1200, draw=100, start=31)
        self.assertEqual(r["series"][12], 1200)
        self.assertEqual(r["dead"], 32)
        self.assertEqual(set(r["series"][24:]), {0})     # nothing left, in that month and every one after

    def test_money_that_ran_out_before_care_is_not_a_hole_care_has_to_fill(self):
        # nothing at 31; care from 40 for ten years with no growth costs the same lump as starting from nothing
        s = run(p0=1200, draw=100, start=30)["series"]
        x = dd.extra_needed(s, 0.0, 100, 40, None, LTC, HOME, None, 30, 50)
        self.assertAlmostEqual(x, 4100 * 120, delta=4200)

    def test_money_that_lasts_has_no_last_age(self):
        self.assertIsNone(run(p0=10 ** 9, draw=100, start=31)["dead"])

    def test_a_month_compounds_before_anything_moves(self):
        self.assertAlmostEqual(run(p0=1000, r=0.12, life=31)["series"][1], 1010)


class WhatCareWouldNeed(unittest.TestCase):

    def test_nothing_more_when_the_money_already_lasts(self):
        s = run(p0=10 ** 9, draw=100, start=31, care=40, life=50)["series"]
        self.assertEqual(dd.extra_needed(s, 0.0, 100, 40, None, LTC, HOME, None, 30, 50), 0)

    def test_the_lump_that_just_reaches_the_last_year(self):
        # nothing held at 40, ten years of 4,100 a month to pay with no growth: about 492,000
        s = run(p0=0, life=50)["series"]
        x = dd.extra_needed(s, 0.0, 100, 40, None, LTC, HOME, None, 30, 50)
        self.assertAlmostEqual(x, 4100 * 120, delta=4200)

    def test_care_that_starts_after_the_plan_ends_has_no_answer(self):
        self.assertIsNone(dd.extra_needed([0, 0], 0.0, 100, 99, None, LTC, HOME, None, 30, 50))


class TheYearsOnRecord(unittest.TestCase):

    YEARS = [[2000, 0.0], [2001, 0.0], [2002, -0.5], [2003, 0.0]]

    def bt(self, pot, life=42):
        return dd.backtest(pot, 100, 40, None, None, LTC, HOME, None, self.YEARS, 30, life)

    def test_every_start_with_enough_years_after_it_is_replayed(self):
        b = self.bt(10 ** 6)
        self.assertEqual((b["n"], b["N"], b["from"], b["to"], b["ok"]), (3, 2, 2000, 2003, 3))

    def test_a_bad_year_can_end_a_start_that_a_flat_one_survives(self):
        b = self.bt(2400)                     # two flat years of 1,200 just last; a halving does not
        self.assertEqual([r["dead"] is None for r in b["runs"]], [False, False, False])
        b = self.bt(2401)
        self.assertEqual([r["dead"] is None for r in b["runs"]], [True, False, False])

    def test_a_retirement_longer_than_the_record_is_not_replayed(self):
        self.assertIsNone(self.bt(10 ** 6, life=60))

    def test_no_pot_is_nothing_to_replay(self):
        self.assertIsNone(self.bt(0))


class TheConstant(unittest.TestCase):

    def test_it_is_empty_without_a_year_of_birth_or_a_tier(self):
        self.assertEqual(dd.figures(1, 1, 1, 0.05, [LTC], HOME, [], [], None, 95, "2026-01-01"), {})
        self.assertEqual(dd.figures(1, 1, 1, 0.05, [], HOME, [], [], 1990, 95, "2026-01-01"), {})

    def test_it_carries_the_ages_and_the_plan_at_them(self):
        f = dd.figures(500000, 3000, 1000, 0.05, [LTC], HOME, [], [], 1990, 95, "2026-01-01")
        self.assertEqual(f["at"], {"stop": 36, "draw": 55, "care": 80, "ltc": 88, "tier": 0})
        self.assertEqual(sorted(f["now"]), ["atDraw", "atStop", "bt", "dead", "extra", "noCareDead", "stayHomeDead"])
        self.assertEqual(f["now"]["atStop"], 500000)
        self.assertIsNone(f["now"]["bt"])


if __name__ == "__main__":
    unittest.main()
