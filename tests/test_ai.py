"""ai.py — the rules around a model's answer, with the network stood in for: an answer has to be
one of the fifteen or it is nothing; what is sent is the merchant and the category names and
no more; off means no call at all; a key never lives in the workspace's data.
"""
import json
import os
import shutil
import tempfile
import unittest

import _paths  # noqa: F401
import ai


class Picking(unittest.TestCase):
    def test_exact_and_cased(self):
        self.assertEqual(ai.pick_category("Grocery"), "Grocery")
        self.assertEqual(ai.pick_category(" dining. "), "Dining")

    def test_a_sentence_that_names_one(self):
        self.assertEqual(ai.pick_category("This looks like Transport (a taxi)."), "Transport")

    def test_anything_else_is_nothing(self):
        self.assertIsNone(ai.pick_category("Groceries and snacks"))   # not a category name, whole
        self.assertIsNone(ai.pick_category("I cannot tell"))
        self.assertIsNone(ai.pick_category(""))


class Calls(unittest.TestCase):
    def setUp(self):
        self.ws = tempfile.mkdtemp(prefix="jt_ai_")
        self.calls = []
        self._post = ai._post
        os.environ["JADE_AI_KEY"] = "test-key"

        def fake(url, headers, body):
            self.calls.append((url, headers, body))
            return {"choices": [{"message": {"content": self.reply}}]}
        ai._post = fake
        self.reply = "Dining"

    def tearDown(self):
        ai._post = self._post
        os.environ.pop("JADE_AI_KEY", None)
        shutil.rmtree(self.ws, ignore_errors=True)

    def test_off_means_no_call(self):
        self.assertEqual(ai.categorise(self.ws, "SOME SHOP"), (None, "off"))
        self.assertEqual(self.calls, [])

    def test_the_request_carries_the_merchant_and_the_names_only(self):
        ai.save_settings(self.ws, {"provider": "openai", "baseUrl": "https://example.test/v1", "model": "m"})
        cat, how = ai.categorise(self.ws, "SHINY NOODLE BAR 12")
        self.assertEqual((cat, how), ("Dining", "model"))
        url, headers, body = self.calls[0]
        self.assertEqual(url, "https://example.test/v1/chat/completions")
        self.assertEqual(headers["Authorization"], "Bearer test-key")
        text = json.dumps(body)
        self.assertIn("SHINY NOODLE BAR 12", text)
        for c in ai.CATEGORIES:
            self.assertIn(c, text)
        for forbidden in ("amount", "balance", "account", "$"):
            self.assertNotIn(forbidden, text.lower().replace("account_", ""))

    def test_an_invalid_answer_is_dropped_and_logged(self):
        ai.save_settings(self.ws, {"provider": "openai"})
        self.reply = "probably food of some kind"
        self.assertEqual(ai.categorise(self.ws, "X"), (None, "invalid"))
        log = open(os.path.join(self.ws, ".jade", "log", "ai.jsonl"), encoding="utf-8").read()
        self.assertIn('"got": "probably food of some kind"', log)
        self.assertIn('"merchant": "X"', log)

    def test_one_merchant_costs_one_call(self):
        ai.save_settings(self.ws, {"provider": "openai"})
        ai.categorise(self.ws, "SAME SHOP")
        self.assertEqual(ai.categorise(self.ws, "SAME SHOP"), ("Dining", "cached"))
        self.assertEqual(len(self.calls), 1)

    def test_ollama_needs_no_key_and_anthropic_speaks_its_own_shape(self):
        os.environ.pop("JADE_AI_KEY", None)
        ai.save_settings(self.ws, {"provider": "ollama"})
        self.assertTrue(ai.enabled(self.ws))
        self.assertEqual(ai.categorise(self.ws, "A")[1], "model")
        self.assertNotIn("Authorization", self.calls[-1][1])
        os.environ["JADE_AI_KEY"] = "k"
        ai.save_settings(self.ws, {"provider": "anthropic"})

        def fake(url, headers, body):
            self.calls.append((url, headers, body))
            return {"content": [{"type": "text", "text": "Travel"}]}
        ai._post = fake
        self.assertEqual(ai.categorise(self.ws, "B"), ("Travel", "model"))
        url, headers, body = self.calls[-1]
        self.assertTrue(url.endswith("/v1/messages"))
        self.assertEqual(headers["x-api-key"], "k")
        self.assertIn("system", body)

    def test_the_settings_file_never_holds_the_key(self):
        ai.save_settings(self.ws, {"provider": "openai", "model": "m"})
        text = open(os.path.join(self.ws, ".jade", "settings.json"), encoding="utf-8").read()
        self.assertNotIn("test-key", text)
        self.assertNotIn("key", json.loads(text)["ai"])


if __name__ == "__main__":
    unittest.main()
