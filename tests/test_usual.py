"""usual.py — a usual month and the emergency fund's months (FINANCE.md §3a, §8d). One test per rule."""
import unittest
import _paths
import usual


def row(date, amount, **kw):
    return dict({"date": date, "amount": amount, "currency": "CAD"}, **kw)


def year(amounts, start="2025-01"):
    """One row on the 10th of each month from `start`."""
    out, m = [], start
    for a in amounts:
        out.append(row(m + "-10", a)); m = usual.ym_shift(m, 1)
    return out


END = {"card": "2025-12-31"}


class Coverage(unittest.TestCase):

    def test_a_month_counts_only_when_every_card_has_closed_it(self):
        self.assertEqual(usual.cov_end({"a": "2025-08-31", "b": "2025-08-20"}), "2025-07")

    def test_a_statement_closing_on_the_last_day_covers_its_month(self):
        self.assertEqual(usual.cov_end({"a": "2025-02-28"}), "2025-02")
        self.assertEqual(usual.cov_end({"a": "2024-02-28"}), "2024-01")     # a leap year has a 29th

    def test_a_source_that_has_reported_nothing_constrains_nothing(self):
        self.assertEqual(usual.cov_end({"a": "2025-08-31", "b": None}), "2025-08")

    def test_nothing_reported_covers_no_month(self):
        self.assertEqual(usual.cov_end({}), "")
        self.assertIsNone(usual.at(year([100, 100, 100, 100]), {}, {}, "2025-06"))


class AUsualMonth(unittest.TestCase):

    def test_it_is_the_average_of_the_full_months_before(self):
        u = usual.at(year([100, 200, 300, 999]), END, {}, "2025-04")
        self.assertEqual(u, {"v": 200, "n": 3})

    def test_fewer_than_three_months_is_not_enough(self):
        self.assertIsNone(usual.at(year([100, 200, 300]), END, {}, "2025-03"))

    def test_at_most_twelve_months_the_newest_ones(self):
        u = usual.at(year([1200] * 3 + [100] * 12), {"card": "2026-03-31"}, {}, "2026-04")
        self.assertEqual(u, {"v": 100, "n": 12})

    def test_a_month_set_aside_is_left_out(self):
        u = usual.at(year([100, 5000, 100, 100]), END, {"2025-02": "moved house"}, "2025-05")
        self.assertEqual(u, {"v": 100, "n": 3})

    def test_a_yearly_charge_is_a_twelfth_in_each_of_its_twelve_months(self):
        rows = year([100, 100, 100]) + [row("2025-01-15", 1200, yr=1)]
        self.assertEqual(usual.compared(rows, "2025-01"), 200)
        self.assertEqual(usual.compared(rows, "2025-12"), 100)
        self.assertEqual(usual.compared(rows, "2026-01"), 0)
        self.assertEqual(usual.at(rows, END, {}, "2025-04"), {"v": 200, "n": 3})

    def test_money_in_another_currency_is_not_in_it(self):
        rows = year([100, 100, 100]) + [row("2025-02-11", 900, currency="USD")]
        self.assertEqual(usual.at(rows, END, {}, "2025-04")["v"], 100)

    def test_a_month_of_refunds_only_is_not_a_month(self):
        u = usual.at(year([100, -50, 100, 100]), END, {}, "2025-05")
        self.assertEqual(u, {"v": 100, "n": 3})

    def test_every_month_the_page_can_turn_to_has_its_answer(self):
        by = usual.by_month(year([100, 100, 100, 100]), END, {}, "2025-04-20")
        self.assertEqual(sorted(by), ["2025-04", "2025-05"])


class TheEmergencyFund(unittest.TestCase):

    def test_months_covered_is_the_money_over_what_a_month_costs(self):
        r = usual.runway(12000, 2000, 1000, 0, 500, {"v": 2500, "n": 6})
        self.assertEqual((r["money"], r["cost"], r["months"], r["abroadMonths"]), (9000, 3000, 3, None))

    def test_more_owed_than_held_is_zero_months_not_negative(self):
        self.assertEqual(usual.runway(1000, 0, 4000, 0, 0, {"v": 1000, "n": 3})["months"], 0)

    def test_money_abroad_is_a_second_answer(self):
        r = usual.runway(3000, 0, 0, 3000, 0, {"v": 1000, "n": 3})
        self.assertEqual((r["months"], r["abroadMonths"]), (3, 6))

    def test_without_a_usual_month_there_are_no_months(self):
        r = usual.runway(3000, 0, 0, 0, 0, None)
        self.assertEqual((r["money"], r["cost"], r["months"]), (3000, None, None))


if __name__ == "__main__":
    unittest.main()
