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



class SystemLanguage(unittest.TestCase):
    """The first launch speaks the system's first language, Chinese or English, never both."""
    def lang_for(self, out):
        from unittest import mock
        import subprocess
        with mock.patch.object(sys, "platform", "darwin"), \
             mock.patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, out, "")):
            return strings.system_lang()

    def test_chinese_first_is_chinese(self):
        self.assertEqual(self.lang_for('(\n    "zh-Hans-CA",\n    "en-CA"\n)'), "zh")

    def test_english_first_is_english_even_with_chinese_after(self):
        self.assertEqual(self.lang_for('(\n    "en-CA",\n    "zh-Hans-CA"\n)'), "en")

    def test_another_language_first_is_english(self):
        self.assertEqual(self.lang_for('(\n    "fr-CA",\n    "zh-Hant"\n)'), "en")

    def test_the_launcher_has_one_language_per_string(self):
        for k in ("welcome", "create_folder", "open_folder", "choose_again", "quit", "choose_prompt",
                  "not_a_folder", "your_folder"):
            self.assertNotIn("·", strings.t("en", k), k)
            self.assertFalse(re.search(r"[\u4e00-\u9fff]", strings.t("en", k)), k)
            self.assertTrue(re.search(r"[\u4e00-\u9fff]", strings.t("zh", k)), k)


if __name__ == "__main__":
    unittest.main()
