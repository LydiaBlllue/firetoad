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


if __name__ == "__main__":
    unittest.main()
