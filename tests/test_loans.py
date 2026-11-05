"""loans.py — money lent, and what is still owed (FINANCE.md §8a). One test per rule."""
import unittest
import _paths
import loans

LOAN = {"key": "loan-x", "role": "owed", "reach": "lent", "name": "Borrower Co",
        "names": ["BORROWER CO", "BCO"], "agreed": {"amount": 1000, "asof": "2026-01-10"}}


def row(date, desc, amount, type_, label=""):
    return {"date": date, "description": desc, "amount": amount, "type": type_, "label": label}


class Outstanding(unittest.TestCase):

    def test_a_repayment_after_the_agreed_date_comes_off(self):
        r = loans.outstanding(LOAN, [row("2026-02-01", "e-Transfer BCO", 200, "Repayment")])
        self.assertEqual((r["owed"], r["back"], r["last"]), (800, 200, "2026-02-01"))

    def test_money_lent_after_the_agreed_date_goes_on(self):
        r = loans.outstanding(LOAN, [row("2026-02-01", "Bank draft", -500, "Lent", label="lent to Borrower Co")])
        self.assertEqual((r["owed"], r["out"]), (1500, 500))

    def test_a_repayment_from_someone_else_changes_nothing(self):
        r = loans.outstanding(LOAN, [row("2026-02-01", "e-Transfer A FRIEND", 50, "Repayment")])
        self.assertEqual(r["owed"], 1000)

    def test_the_name_may_sit_in_the_label_instead_of_the_description(self):
        r = loans.outstanding(LOAN, [row("2026-02-01", "INTERAC E-TRF", 100, "Repayment", label="Repayment — Borrower Co")])
        self.assertEqual(r["owed"], 900)


class Edges(unittest.TestCase):

    def test_a_repayment_on_the_agreed_day_itself_is_already_settled(self):
        # The agreed figure settles everything up to AND INCLUDING that day.
        r = loans.outstanding(LOAN, [row("2026-01-10", "e-Transfer BCO", 200, "Repayment")])
        self.assertEqual(r["owed"], 1000)

    def test_no_agreed_block_starts_from_zero(self):
        loan = {"role": "owed", "name": "New Co"}
        r = loans.outstanding(loan, [row("2026-02-01", "Draft NEW CO", -500, "Lent")])
        self.assertEqual(r["owed"], 500)

    def test_a_negative_repayment_is_ignored(self):
        r = loans.outstanding(LOAN, [row("2026-02-01", "e-Transfer BCO", -200, "Repayment")])
        self.assertEqual(r["owed"], 1000)

    def test_a_loan_with_no_names_matches_nobody(self):
        loan = {"role": "owed", "name": "", "names": [], "agreed": {"amount": 1, "asof": "2026-01-01"}}
        r = loans.outstanding(loan, [row("2026-02-01", "ANYONE", 1, "Repayment")])
        self.assertEqual(r["owed"], 1)

    @unittest.expectedFailure
    def test_a_short_name_does_not_match_inside_a_longer_one(self):
        # Known gap (2026-11-05): matching is by substring, so a two-letter borrower name is found
        # inside an unrelated payer's name. Every real loan today has a long name; this pins the
        # gap until matching is by word boundary.
        loan = {"role": "owed", "name": "Li", "agreed": {"amount": 100, "asof": "2026-01-01"}}
        r = loans.outstanding(loan, [row("2026-02-01", "e-Transfer LINDA HOLM", 50, "Repayment")])
        self.assertEqual(r["owed"], 100)


if __name__ == "__main__":
    unittest.main()
