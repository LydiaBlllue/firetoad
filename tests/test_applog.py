"""applog.py — the code and the report an owner copies when a run stops: the code names the verb
and what stopped it, the report carries the run's own ✗ lines and nothing else of what it printed.
"""
import datetime
import unittest

import _paths  # noqa: F401
import os, sys
sys.path.insert(0, os.path.join(_paths.SKILLS, "local-app", "scripts"))
import applog


class Report(unittest.TestCase):
    def rep(self, **kw):
        lines = ["  reading 3 statements", "  Spending in May: $0 → $503", "  ✗ KeyError: 'series'"]
        return applog.report("setup", "3fa9c1d2", "KeyError", "KeyError: 'series'", lines, "1.0.4",
                             now=datetime.datetime(2026, 11, 12, 21, 40), **kw)

    def test_the_code_is_the_verb_and_what_stopped_it(self):
        self.assertEqual(self.rep()["code"], "FT-SETUP-KeyError")
        self.assertEqual(applog.code("import", "STOPPED"), "FT-IMPORT-STOPPED")

    def test_the_text_to_copy_has_version_time_code_id_and_the_log(self):
        text = self.rep()["text"].splitlines()
        self.assertEqual(text[0], "App: FIRE Toad 1.0.4")
        self.assertTrue(text[1].startswith("System: "))
        self.assertEqual(text[2], "Time: 2026-11-12 21:40")
        self.assertEqual(text[3], "Error code: FT-SETUP-KeyError")
        self.assertEqual(text[4], "Run: 3fa9c1d2")
        self.assertEqual(text[5], "What happened: KeyError: 'series'")
        self.assertTrue(text[-1].startswith("Log: "))

    def test_one_fact_a_line_never_strung_on_a_dot(self):
        self.assertNotIn("·", self.rep()["text"])

    def test_only_the_marked_lines_go_in_never_the_amounts(self):
        text = self.rep()["text"]
        self.assertIn("✗ KeyError: 'series'", text)
        self.assertNotIn("$503", text)
        self.assertNotIn("reading 3 statements", text)

    def test_the_log_is_the_systems_own_place_on_a_mac(self):
        if sys.platform == "darwin":
            self.assertTrue(applog.log_path().endswith(os.path.join("Library", "Logs", "FIRE Toad", "firetoad.log")))


if __name__ == "__main__":
    unittest.main()
