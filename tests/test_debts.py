"""debts.py — when a debt has to be paid (FINANCE.md §8d). One test per rule."""
import unittest
import _paths
import debts

CARD = {"key": "card", "kind": "Credit card", "side": "liability"}
LOAN = {"key": "loan", "kind": "Loan", "side": "liability"}
LINE = {"key": "line", "kind": "Line of credit", "side": "liability"}
MORTGAGE = {"key": "mort", "kind": "Mortgage", "side": "liability", "against": "home"}
HOME = {"key": "home", "kind": "Property", "side": "asset"}
BY_KEY = {a["key"]: a for a in (CARD, LOAN, LINE, MORTGAGE, HOME)}


class WhenItIsDue(unittest.TestCase):

    def test_a_card_is_due_now_and_everything_else_later(self):
        self.assertEqual([debts.due(a) for a in (CARD, LOAN, LINE, MORTGAGE)], ["now", "later", "later", "later"])

    def test_the_owners_word_on_the_row_wins(self):
        self.assertEqual(debts.due(dict(LOAN, due="now")), "now")
        self.assertEqual(debts.due(dict(CARD, due="later")), "later")

    def test_a_word_that_is_not_one_of_the_two_falls_back_to_the_kind(self):
        self.assertEqual(debts.due(dict(CARD, due="soon")), "now")


class WhatSitsOnNoAsset(unittest.TestCase):

    def test_only_what_is_due_now_is_in_the_first_list(self):
        now, later = debts.unsecured([(CARD, 900), (LOAN, 20000), (LINE, 5000), (MORTGAGE, 300000)], BY_KEY)
        self.assertEqual([a["key"] for a, _ in now], ["card"])
        self.assertEqual([a["key"] for a, _ in later], ["loan", "line"])

    def test_a_debt_secured_on_an_asset_is_in_neither(self):
        now, later = debts.unsecured([(MORTGAGE, 300000)], BY_KEY)
        self.assertEqual((now, later), ([], []))

    def test_a_debt_against_something_that_is_not_in_the_register_counts_as_unsecured(self):
        now, later = debts.unsecured([(dict(LOAN, against="gone"), 100)], BY_KEY)
        self.assertEqual(len(later), 1)


class WhatThePlanPays(unittest.TestCase):

    def test_a_committed_flow_names_the_debt_it_repays(self):
        flows = [{"kind": "committed", "pays": "loan", "amount": 350}, {"kind": "committed", "amount": 1500},
                 {"kind": "saving", "pays": "line", "amount": 1}, {"kind": "committed", "pays": "mort", "starts": "fire"}]
        self.assertEqual(debts.paid_by(flows), {"loan"})


if __name__ == "__main__":
    unittest.main()
