"""strings.py — the panel's words: every key in both languages, every placeholder a name t()
can take, and a missing translation falling back to English instead of raising.
"""
import re
import unittest

import _paths  # noqa: F401
import os, sys
sys.path.insert(0, os.path.join(_paths.SKILLS, "local-app", "scripts"))
import strings


class Table(unittest.TestCase):
    def test_every_key_has_both_languages(self):
        for table in (strings.S, strings.W):
            for k, row in table.items():
                self.assertEqual(set(row), {"en", "zh"}, k)
                self.assertTrue(row["en"].strip() and row["zh"].strip(), k)

    def test_no_placeholder_shadows_the_helpers_parameters(self):
        # t(lang, key, **kw): a placeholder called key or lang crashed the panel (2026-11-07)
        for table in (strings.S, strings.W):
            for k, row in table.items():
                for text in row.values():
                    for ph in re.findall(r"\{(\w+)\}", text):
                        self.assertNotIn(ph, ("lang", "key"), f"{k}: {{{ph}}}")

    def test_both_languages_use_the_same_placeholders(self):
        for table in (strings.S, strings.W):
            for k, row in table.items():
                self.assertEqual(set(re.findall(r"\{(\w+)\}", row["en"])), set(re.findall(r"\{(\w+)\}", row["zh"])), k)


class Lookup(unittest.TestCase):
    def test_formats_and_falls_back(self):
        self.assertEqual(strings.t("zh", "s1"), "拿到这个月的文件")
        self.assertIn("2", strings.t("en", "missing", doc="Chequing", n=2, months="Oct, Nov"))
        self.assertEqual(strings.t("fr", "s1"), strings.t("en", "s1"))
        self.assertEqual(strings.t("en", "no-such-key"), "no-such-key")

    def test_month_names(self):
        self.assertEqual(strings.months("en", ["2026-10", "2026-11"]), "Oct, Nov")
        self.assertEqual(strings.months("zh", ["2026-01"]), "1 月")


if __name__ == "__main__":
    unittest.main()
