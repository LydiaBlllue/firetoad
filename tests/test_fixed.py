"""fixed.py — fixed costs are only what the owner declared (FINANCE.md §3a). One test per rule."""
import unittest
import _paths
import fixed


def row(d, a, cat="Housing", note="X"):
    return {"date": d, "amount": a, "currency": "CAD", "category": cat, "note": note}


RENT = {"kind": "committed", "name": "Rent", "amount": 1450}
GROUPS = {"Housing": "bills", "Bills": "bills", "Grocery": "everyday"}


class TheDeclaredPayment(unittest.TestCase):

    def test_the_row_of_the_flows_amount_is_fixed_each_month(self):
        rows = [row("2026-01-01", 1450), row("2026-02-01", 1450), row("2026-02-03", 80, "Bills", "FIDO")]
        self.assertEqual(fixed.mark(rows, [RENT], GROUPS), {0, 1})

    def test_a_bill_nobody_declared_is_everyday(self):
        rows = [row("2026-01-05", 65, "Bills", "FIDO MOBILE")]
        self.assertEqual(fixed.mark(rows, [RENT], GROUPS), set())

    def test_within_a_dollar_or_one_per_cent(self):
        self.assertEqual(fixed.mark([row("2026-01-01", 1460)], [RENT], GROUPS), {0})
        self.assertEqual(fixed.mark([row("2026-01-01", 1480)], [RENT], GROUPS), set())

    def test_a_bill_taken_in_two_debits_by_one_payee(self):
        rows = [row("2026-01-02", 700, note="LANDLORD CO"), row("2026-01-15", 750, note="LANDLORD CO"),
                row("2026-01-15", 750, "Grocery", "SHOP")]
        self.assertEqual(fixed.mark(rows, [RENT], GROUPS), {0, 1})

    def test_one_payment_a_month_only(self):
        rows = [row("2026-01-01", 1450), row("2026-01-20", 1450)]
        self.assertEqual(len(fixed.mark(rows, [RENT], GROUPS)), 1)

    def test_after_its_end_a_flow_is_not_looked_for(self):
        loan = {"kind": "committed", "name": "Loan", "amount": 300, "until": "2026-01"}
        rows = [row("2026-01-10", 300, "Bills"), row("2026-02-10", 300, "Bills")]
        self.assertEqual(fixed.mark(rows, [loan], GROUPS), {0})


class AnEstimate(unittest.TestCase):

    def test_the_bills_group_stands_for_a_figure_across_several_bills(self):
        est = {"kind": "committed", "name": "Utilities", "amount": 500, "estimate": True}
        rows = [row("2026-01-05", 65, "Bills"), row("2026-01-06", 40, "Grocery")]
        self.assertEqual(fixed.mark(rows, [est], GROUPS), {0})


if __name__ == "__main__":
    unittest.main()
