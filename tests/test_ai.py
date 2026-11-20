"""ai.py — AI assist's rules, with the network stood in for: an answer has to be one of the fifteen
or it is nothing; what is sent is the merchants and the category names and no more; off means no
call at all, and the key goes with it; a model that thinks first gets room to answer; a cloud
service is asked once an import, and never about more than fifty merchants; a key never lives in
the workspace's data, and a test never touches the Keychain; an answer cut off at the ceiling
still gives what it got to; a request that failed says why and leaves the merchants to be asked
again; a key goes over plain http to this computer and nowhere else.
"""
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.error

import _paths  # noqa: F401
import ai


class Picking(unittest.TestCase):
    def test_exact_and_cased(self):
        self.assertEqual(ai.pick_category("Grocery"), "Grocery")
        self.assertEqual(ai.pick_category(" dining. "), "Dining")

    def test_a_sentence_that_names_one(self):
        self.assertEqual(ai.pick_category("This looks like Transport (a taxi)."), "Transport")

    def test_a_sentence_that_names_two_is_nothing(self):
        self.assertIsNone(ai.pick_category("Not Dining, it is Grocery"))

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
        os.environ["FIRETOAD_AI_NO_KEYCHAIN"] = "1"

        def fake(url, headers, body):
            self.calls.append((url, headers, body))
            return {"choices": [{"message": {"content": self.reply}}]}
        ai._post = fake
        self.reply = "Dining"

    def tearDown(self):
        ai._post = self._post
        os.environ.pop("JADE_AI_KEY", None)
        os.environ.pop("FIRETOAD_AI_NO_KEYCHAIN", None)
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

    def other(self):
        ai.save_settings(self.ws, {"provider": "openai", "baseUrl": "https://example.test/v1", "model": "m"})

    def test_an_invalid_answer_is_dropped_and_logged(self):
        self.other()
        self.reply = "probably food of some kind"
        self.assertEqual(ai.categorise(self.ws, "X"), (None, "invalid"))
        log = open(os.path.join(self.ws, ".firetoad", "log", "ai.jsonl"), encoding="utf-8").read()
        self.assertIn('"got": "probably food of some kind"', log)
        self.assertIn('"merchants": ["X"]', log)

    def test_one_merchant_costs_one_call(self):
        self.other()
        ai.categorise(self.ws, "SAME SHOP")
        self.assertEqual(ai.categorise(self.ws, "SAME SHOP"), ("Dining", "cached"))
        self.assertEqual(len(self.calls), 1)

    def test_ollama_needs_no_key_and_anthropic_speaks_its_own_shape(self):
        os.environ.pop("JADE_AI_KEY", None)
        ai.save_settings(self.ws, {"provider": "ollama", "model": "qwen2.5:7b"})
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

    def test_a_model_that_thinks_first_gets_room_to_answer(self):
        # 40 tokens came back empty from the models that think before answering (2026-11-20)
        self.other()
        ai.categorise(self.ws, "ROOMY")
        self.assertGreaterEqual(self.calls[-1][2]["max_tokens"], 1000)

    def test_an_answer_cut_off_still_gives_what_it_got_to(self):
        whole = json.dumps({str(i): "Dining" for i in range(1, 11)})
        self.assertEqual(len(ai.parse_many(whole[:len(whole) // 2], 10)), 5)
        self.assertEqual(len(ai.parse_many('{\n  "1": "Dining",\n  "2": "Groc', 10)), 1)

    def test_a_cut_answer_is_said_and_the_rest_can_be_asked_again(self):
        self.other()
        ai._post = lambda url, headers, body: {"choices": [{"finish_reason": "length", "message": {"content": '{"1": "Dining", "2": "Gro'}}]}
        found, info = ai.suggest_many(self.ws, ["A CAFE", "B MARKET", "C THING"])
        self.assertEqual((found, info["cut"], info["answered"]), ({"A CAFE": "Dining"}, True, ["A CAFE"]))
        with open(os.path.join(ai.layout.state_dir(self.ws), "log", "ai.jsonl"), encoding="utf-8") as fh:
            self.assertTrue(json.loads(fh.readlines()[-1])["cut"])

    def test_claude_says_cut_its_own_way(self):
        ai.save_settings(self.ws, {"provider": "claude"})
        ai._post = lambda url, headers, body: {"stop_reason": "max_tokens", "content": [{"type": "thinking", "thinking": "…"}]}
        self.assertEqual(ai.exchange(self.ws, "s", "u"), ("", True))

    def refuse(self, code, body):
        def refused(url, headers, text):
            self.calls.append(url)
            raise urllib.error.HTTPError(url, code, "no", {}, io.BytesIO(json.dumps(body).encode()))
        ai._post = refused

    def test_a_failure_says_why(self):
        self.other()
        for code, body, why in ((401, {"error": {"type": "authentication_error", "message": "bad key sk-…abcd"}}, "key"),
                                (402, {"error": {"message": "Insufficient Balance"}}, "credit"),
                                (400, {"error": {"type": "invalid_request_error", "message": "Your credit balance is too low"}}, "credit"),
                                (429, {"error": {"code": "insufficient_quota", "message": "You exceeded your current quota"}}, "credit"),
                                (429, {"error": {"type": "rate_limit_error"}}, "busy"),
                                (529, {"error": {"type": "overloaded_error"}}, "busy"),
                                (404, {"error": {"type": "not_found_error"}}, "error")):
            self.refuse(code, body)
            self.assertEqual(ai.suggest_many(self.ws, [f"SHOP {code} {why}"])[1]["error"], why, (code, body))
        with open(os.path.join(ai.layout.state_dir(self.ws), "log", "ai.jsonl"), encoding="utf-8") as fh:
            log = fh.read()
        self.assertIn("HTTP 401 authentication_error", log)
        self.assertNotIn("abcd", log)                 # the service's own message can quote the key: never kept

    def decisions(self, names):
        p = ai.layout.path(self.ws, "decisions.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"decisions": [{"kind": "merchant", "status": "open", "match": m, "default": "Other"} for m in names]}, fh)
        return p

    def test_after_a_refused_key_the_same_merchants_are_asked_again(self):
        self.other()
        p = self.decisions(["A CAFE", "B MARKET"])
        self.refuse(401, {"error": {"type": "authentication_error"}})
        out = ai.suggest_open(self.ws)
        self.assertEqual((out["error"], out["suggested"]), ("key", 0))
        with open(p, encoding="utf-8") as fh:
            self.assertFalse(any(d.get("aiAsked") for d in json.load(fh)["decisions"]))
        ai._post = lambda url, headers, body: {"choices": [{"message": {"content": '{"1": "Dining", "2": "Spaceships"}'}}]}
        out = ai.suggest_open(self.ws)                # the key put right
        self.assertEqual((out["error"], out["suggested"]), (None, 1))
        with open(p, encoding="utf-8") as fh:
            got = json.load(fh)["decisions"]
        self.assertEqual([d.get("suggest") for d in got], ["Dining", None])
        self.assertTrue(all(d.get("aiAsked") for d in got))   # answered, even with nothing usable: not asked again

    def test_plain_http_only_to_this_computer(self):
        for url, ok in (("https://api.example.test/v1", True), ("http://localhost:11434/v1", True), ("http://127.0.0.1:8080/v1", True),
                        ("http://localhost.example.test/v1", False), ("http://127.0.0.1.example.test/v1", False),
                        ("http://example.test/v1", False), ("ftp://localhost/v1", False), ("localhost:11434", False), ("", False)):
            self.assertEqual(ai.address_ok(url), ok, url)
        with self.assertRaises(ValueError):
            ai.turn_on(self.ws, "openai", key="k", model="m", base_url="http://localhost.example.test/v1")

    def test_gpt5_takes_its_own_budget_and_no_temperature(self):
        body = ai.openai_body("gpt-5.4-mini", "s", "u", 1000)
        self.assertEqual(body["max_completion_tokens"], 1000)
        self.assertNotIn("temperature", body)
        self.assertNotIn("max_tokens", body)
        other = ai.openai_body("deepseek-flash", "s", "u", 1000)
        self.assertEqual((other["max_tokens"], other["temperature"]), (1000, 0))

    def test_a_cloud_service_is_asked_once_for_the_whole_import(self):
        self.other()
        self.reply = '```json\n{"1": "Dining", "2": "Grocery", "3": "Spaceships"}\n```'
        found, info = ai.suggest_many(self.ws, ["A CAFE", "B MARKET", "C THING", "A CAFE"])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(found, {"A CAFE": "Dining", "B MARKET": "Grocery"})   # not one of the fifteen: dropped
        self.assertEqual(self.calls[0][2]["messages"][-1]["content"].splitlines(), ["1. A CAFE", "2. B MARKET", "3. C THING"])
        ai.suggest_many(self.ws, ["A CAFE", "B MARKET"])                       # answered once: not sent again
        self.assertEqual(len(self.calls), 1)

    def test_never_more_than_fifty_merchants_an_import(self):
        self.other()
        self.reply = "{}"
        found, info = ai.suggest_many(self.ws, [f"SHOP {i}" for i in range(70)])
        self.assertEqual(len(self.calls[0][2]["messages"][-1]["content"].splitlines()), ai.MAX_PER_IMPORT)
        self.assertEqual(info["left"], 70 - ai.MAX_PER_IMPORT)

    def test_a_failure_is_not_retried(self):
        self.other()

        def broken(url, headers, body):
            self.calls.append(url)
            raise OSError("down")
        ai._post = broken
        found, info = ai.suggest_many(self.ws, ["A", "B"])
        self.assertEqual((found, info["error"], info["answered"], len(self.calls)), ({}, "network", [], 1))

    def test_ollamas_cloud_models_are_not_on_this_computer(self):
        self.assertTrue(ai.is_cloud_model("gpt-oss:120b-cloud"))
        self.assertTrue(ai.is_cloud_model("deepseek-v3.1:671b-cloud"))
        self.assertFalse(ai.is_cloud_model("qwen2.5:7b"))

    def test_off_deletes_the_key(self):
        ai.turn_on(self.ws, "deepseek", key="sk-1")
        self.assertTrue(os.path.exists(os.path.join(self.ws, ".firetoad", "ai-deepseek.key")))
        ai.turn_off(self.ws)
        self.assertFalse(any(f.endswith(".key") for f in os.listdir(os.path.join(self.ws, ".firetoad"))))
        self.assertEqual(ai.settings(self.ws)["provider"], "none")

    def test_choosing_another_service_deletes_the_first_ones_key(self):
        ai.turn_on(self.ws, "claude", key="sk-a")
        ai.turn_on(self.ws, "chatgpt", key="sk-b")
        keys = sorted(f for f in os.listdir(os.path.join(self.ws, ".firetoad")) if f.endswith(".key"))
        self.assertEqual(keys, ["ai-chatgpt.key"])

    def test_the_owner_chooses_a_name_and_the_tool_the_address_and_model(self):
        ai.turn_on(self.ws, "chatgpt", key="sk-b")
        self.assertEqual(set(ai.settings(self.ws)) - {"since", "declined"}, {"provider"})
        self.reply = "Dining"
        ai.categorise(self.ws, "NOODLES")
        self.assertTrue(self.calls[-1][0].startswith("https://api.openai.com/"))
        self.assertTrue(self.calls[-1][2]["model"].startswith("gpt-5"))

    def test_kept_counts_the_answers_that_agreed(self):
        os.makedirs(os.path.join(self.ws, "findata", "history"))
        with open(os.path.join(self.ws, "findata", "history", "decisions.json"), "w", encoding="utf-8") as fh:
            json.dump({"decisions": [
                {"kind": "merchant", "suggest": "Dining", "suggestBy": "model", "status": "confirmed", "answer": "Dining"},
                {"kind": "merchant", "suggest": "Dining", "suggestBy": "model", "status": "confirmed", "answer": "Grocery"},
                {"kind": "merchant", "suggest": "Travel", "suggestBy": "model", "status": "open"},
                {"kind": "merchant", "suggest": "Grocery", "status": "confirmed", "answer": "Grocery"}]}, fh)
        self.assertEqual(ai.kept(self.ws), (3, 1))

    def test_the_settings_file_never_holds_the_key(self):
        ai.save_settings(self.ws, {"provider": "openai", "model": "m"})
        text = open(os.path.join(self.ws, ".firetoad", "settings.json"), encoding="utf-8").read()
        self.assertNotIn("test-key", text)
        self.assertNotIn("key", json.loads(text)["ai"])


if __name__ == "__main__":
    unittest.main()
