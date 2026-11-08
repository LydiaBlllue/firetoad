"""senders.json — who sends money and what it is, answered once (2026-11-07). The rule the owner
used to keep in prose for Claude, as data both doors read: the name read off the statement, the
rule applied before the question, the answer written back as the rule.
"""
import json
import os
import shutil
import tempfile
import types
import unittest

import _paths  # noqa: F401
import confirm
import layout
import update


class Naming(unittest.TestCase):
    def test_the_banks_words_come_off(self):
        self.assertEqual(update.sender_of("e-Transfer received MEI CHEN"), "MEI CHEN")
        self.assertEqual(update.sender_of("INTERAC E-TRANSFER FROM ALEX NG"), "ALEX NG")
        self.assertEqual(update.sender_of("Interac e-Transfer received SAM LEE REF 20XY"), "SAM LEE")

    def test_a_statement_with_no_name_leaves_nothing(self):
        self.assertEqual(update.sender_of("INTERACe-TransferReceived"), "")


def ws_with(senders):
    return types.SimpleNamespace(owner="EMMA ROY", broker="", cp=None, cp_rows=[], loans=[], rent=[], cards=[],
                                 bank_accts=[], senders=senders)


class Typing(unittest.TestCase):
    def test_a_named_sender_is_asked_once(self):
        ws = ws_with([])
        t, label, ask = update.type_row(ws, {}, "e-Transfer received ALEX NG", 880.0, "2026-02-03")
        self.assertEqual(t, "Other")
        self.assertIsNotNone(ask)
        self.assertEqual(ask.get("sender"), "ALEX NG")
        self.assertIn("Alex Ng", ask["what"])

    def test_the_rule_types_the_next_one_without_asking(self):
        ws = ws_with([{"match": "ALEX NG", "type": "Gift"}])
        t, label, ask = update.type_row(ws, {}, "e-Transfer received ALEX NG", 880.0, "2026-03-03")
        self.assertEqual((t, ask), ("Gift", None))
        self.assertIn("family or gift", label)

    def test_a_repayment_rule(self):
        ws = ws_with([{"match": "SAM LEE", "type": "Repayment"}])
        t, label, ask = update.type_row(ws, {}, "INTERAC E-TRANSFER FROM SAM LEE 1234", 45.5, "2026-03-03")
        self.assertEqual((t, ask), ("Repayment", None))

    def test_the_owners_own_name_still_wins(self):
        ws = ws_with([{"match": "EMMA ROY", "type": "Gift"}])
        t, label, ask = update.type_row(ws, {}, "e-Transfer received EMMA ROY", 500.0, "2026-03-03")
        self.assertEqual(t, "Transfer")

    def test_an_unknown_type_in_the_file_is_ignored(self):
        ws = ws_with([{"match": "X", "type": "Income"}])
        self.assertTrue(all(s["type"] in update.SENDER_LABEL for s in ws.senders) is False)
        t, label, ask = update.type_row(ws_with([s for s in ws.senders if s["type"] in update.SENDER_LABEL]), {},
                                        "e-Transfer received X", 5.0, "2026-03-03")
        self.assertIsNotNone(ask)


class Remembering(unittest.TestCase):
    def setUp(self):
        self.ws = tempfile.mkdtemp(prefix="jt_senders_")
        os.makedirs(os.path.join(self.ws, "findata", "register"))

    def tearDown(self):
        shutil.rmtree(self.ws, ignore_errors=True)

    def test_an_answer_becomes_the_rule_and_a_second_answer_replaces_it(self):
        self.assertTrue(confirm.remember_sender(self.ws, "Alex Ng", "Gift", "2026-11-07"))
        self.assertTrue(confirm.remember_sender(self.ws, "ALEX NG", "Repayment", "2026-11-08"))
        sj = json.load(open(layout.path(self.ws, "senders.json"), encoding="utf-8"))
        self.assertEqual(sj["senders"], [{"match": "ALEX NG", "type": "Repayment", "asof": "2026-11-08"}])

    def test_no_name_means_no_rule(self):
        self.assertFalse(confirm.remember_sender(self.ws, "", "Gift", "2026-11-07"))
        self.assertFalse(os.path.exists(layout.path(self.ws, "senders.json")))


if __name__ == "__main__":
    unittest.main()
