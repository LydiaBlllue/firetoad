"""wizard.py — what the setup's answers become. One rule here: an early-retirement question the
owner skips is "no for now" (PRODUCT.md), written down, so the page does not read "never asked"
and show FIRE to anyone with money invested, and the first import does not ask again.
"""
import unittest

import _paths  # noqa: F401
import wizard


class Goal(unittest.TestCase):
    def fire(self, goal):
        return wizard.merge({"accounts": []}, {"goal": goal}, "2026-11-12")["plan"]["fire"]

    def test_yes_is_yes(self):
        self.assertEqual(self.fire("yes"), {"goal": True, "asked": "2026-11-12"})

    def test_no_is_no(self):
        self.assertEqual(self.fire("no"), {"goal": False, "asked": "2026-11-12"})

    def test_skipped_is_no_and_says_it_was_skipped(self):
        for g in ("", "skip", None):
            self.assertEqual(self.fire(g), {"goal": False, "asked": "2026-11-12", "skipped": True})


class NotMine(unittest.TestCase):
    """An account on a broker's export can be said to be someone else's money: it goes to
    notOwned and stays in the draft, so the export's document survives (scaffold.py drops it)."""
    def draft(self):
        return {"accounts": [
            {"inst": "BMO", "name": "Chequing", "kind": "Chequing", "id": "…471", "doc": {"into": "chq.csv"}},
            {"inst": "WS", "name": "TFSA", "kind": "TFSA", "id": "HQ1", "doc": {"key": "Holdings", "into": "holdings_latest.csv"}},
            {"inst": "WS", "name": "RRSP", "kind": "RRSP", "id": "HQ2", "doc": {"key": "Activities", "into": "ws_activities.csv"}}]}

    def test_only_an_account_on_a_shared_export_can_be_disowned(self):
        chq, tfsa, rrsp = self.draft()["accounts"]
        self.assertFalse(wizard.can_disown(chq))       # its own statement would arrive every month
        self.assertTrue(wizard.can_disown(tfsa))
        self.assertTrue(wizard.can_disown(rrsp))
        self.assertFalse(wizard.can_disown({"kind": "TFSA", "id": "—"}))   # no number to know it by

    def test_not_mine_is_named_in_notowned_and_keeps_its_row(self):
        a = wizard.merge(self.draft(), {"goal": "no", "accounts": [{"i": 2, "role": "not-mine"}]}, "2026-11-12")
        self.assertEqual([x["id"] for x in a["notOwned"]], ["HQ2"])
        self.assertEqual(len(a["accounts"]), 3)        # the row carries the Activities document

    def test_a_bank_account_asked_to_be_not_mine_stays_mine(self):
        a = wizard.merge(self.draft(), {"goal": "no", "accounts": [{"i": 0, "role": "not-mine"}]}, "2026-11-12")
        self.assertNotIn("notOwned", a)


if __name__ == "__main__":
    unittest.main()
