"""flows.py — the monthly plan as flows (FINANCE.md §8b). One test per rule."""
import unittest
import _paths
import flows


def plan(*rows):
    return {"flows": list(rows)}


class Totals(unittest.TestCase):

    def test_each_kind_sums_on_its_own(self):
        t = flows.totals(plan({"kind": "income", "amount": 5000},
                              {"kind": "committed", "amount": 1500},
                              {"kind": "saving", "amount": 2000},
                              {"kind": "everyday", "amount": 1200}))
        self.assertEqual((t["income"], t["committed"], t["saving"], t["everyday"]),
                         (5000, 1500, 2000, 1200))

    def test_rent_that_starts_at_fire_is_planning_not_cash(self):
        t = flows.totals(plan({"kind": "committed", "amount": 1500, "starts": "fire"}))
        self.assertEqual(t["committed"], 0)          # not in this month's split
        self.assertEqual(t["committedKeep"], 1500)   # but in the planning figure

    def test_a_repayment_is_kept_after_fire_but_rent_paid_today_is_not(self):
        # Rent paid today is already in spending.csv; adding it to committedKeep would count it
        # twice. A repayment's principal is saving, so it is not in spending and is added.
        t = flows.totals(plan({"kind": "committed", "amount": 1800},                   # rent today
                              {"kind": "committed", "amount": 600, "pays": "mortgage"}))
        self.assertEqual(t["committedKeep"], 600)
        self.assertEqual(t["repayNow"], 600)

    def test_a_mortgage_marked_drop_leaves_the_planning_figure(self):
        t = flows.totals(plan({"kind": "committed", "amount": 600, "pays": "mortgage", "afterFire": "drop"}))
        self.assertEqual(t["committedKeep"], 0)

    def test_saving_to_somewhere_other_than_the_broker_is_not_invest(self):
        t = flows.totals(plan({"kind": "saving", "amount": 2000},
                              {"kind": "saving", "amount": 200, "to": "resp"}))
        self.assertEqual((t["saving"], t["invest"]), (2200, 2000))


class Edges(unittest.TestCase):

    def test_an_empty_plan_is_all_zero(self):
        t = flows.totals({})
        self.assertEqual(t["income"], 0)
        self.assertEqual(t["committedNow"], [])

    def test_null_amount_is_unset_and_counts_as_nothing(self):
        # 2026-10-28, first user: a skipped question used to land as $0 and read as a fact.
        p = plan({"kind": "income", "amount": None})
        self.assertEqual(flows.unset(p), {"takeHome"})
        self.assertEqual(flows.totals(p)["income"], 0)

    def test_zero_amount_is_a_fact_not_unset(self):
        self.assertEqual(flows.unset(plan({"kind": "everyday", "amount": 0})), set())

    def test_whole_amounts_come_back_as_int_cents_as_float(self):
        self.assertEqual(flows.totals(plan({"kind": "income", "amount": 5000.0}))["income"], 5000)
        self.assertEqual(flows.totals(plan({"kind": "income", "amount": 12.345}))["income"], 12.35)


if __name__ == "__main__":
    unittest.main()
