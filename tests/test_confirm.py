"""confirm.py — "not sure" is an answer, and what an open question carries for the owner's memory."""
import csv
import json
import os
import tempfile
import unittest

import _paths  # noqa: F401
import confirm
import layout


class NotSure(unittest.TestCase):

    def setUp(self):
        self.ws = tempfile.mkdtemp(prefix="jt_confirm_")
        layout.ensure(self.ws)
        w = lambda n, o: json.dump(o, open(layout.path(self.ws, n), "w", encoding="utf-8"))
        w("accounts.json", {"accounts": [{"key": "chq", "inst": "Bank", "name": "Chequing", "ledger": "chq.csv"}]})
        w("merchants.json", {"merchants": []})
        w("decisions.json", {"decisions": [
            {"kind": "merchant", "match": "SHOP", "what": "SHOP, seen for the first time.", "default": "Other", "status": "open"},
            {"kind": "merchant", "match": "CAFE", "what": "CAFE, seen for the first time.", "default": "Other", "status": "open"},
            {"kind": "transfer", "what": "sent", "default": "Transfer", "status": "open", "facts": {"kind": "sent", "amount": 650, "date": "2026-02-02"},
             "row": {"date": "2026-02-02", "amount": 650.0, "cur": "CAD", "note": "e-Transfer sent [B1/20260213]", "ledger": "chq.csv"}},
            {"kind": "transfer", "what": "sent", "default": "Transfer", "status": "open", "facts": {"kind": "sent", "amount": 650, "date": "2026-03-02"},
             "row": {"date": "2026-03-02", "amount": 650.0, "cur": "CAD", "note": "e-Transfer sent [B1/20260313]", "ledger": "chq.csv"}}]})
        with open(layout.path(self.ws, "spending.csv"), "w", encoding="utf-8", newline="") as fh:
            cw = csv.writer(fh); cw.writerow(["date", "amount", "currency", "category", "note"])
            cw.writerows([["2026-03-07", "40.00", "CAD", "Other", "SHOP [V1/20260319]"], ["2026-03-07", "9.00", "CAD", "Dining", "BAKERY [V1/20260319]"],
                          ["2026-03-21", "60.00", "CAD", "Other", "SHOP [V1/20260419]"], ["2026-03-22", "5.00", "CAD", "Other", "CAFE [V1/20260419]"]])
        with open(layout.path(self.ws, "chq.csv"), "w", encoding="utf-8", newline="") as fh:
            cw = csv.writer(fh); cw.writerow(layout.LEDGER_COLS)
            cw.writerows([["2026-02-02", "e-Transfer sent", "-650.00", "100.00", "B1/20260213", "Transfer", ""],
                          ["2026-02-02", "Plan fee", "-16.95", "83.05", "B1/20260213", "Fee", ""],
                          ["2026-03-02", "e-Transfer sent", "-650.00", "10.00", "B1/20260313", "Transfer", ""]])
        self._after = confirm._after_write
        confirm._after_write = lambda root: None            # no page to rebuild in a five-file workspace

    def tearDown(self):
        confirm._after_write = self._after

    def load(self, n):
        return json.load(open(layout.path(self.ws, n), encoding="utf-8"))

    def test_a_merchant_not_sure_is_filed_other_marked_and_closed(self):
        r = confirm.run(self.ws, write=True, sets=["SHOP=not sure"])
        self.assertEqual(r["rc"], 0, r["lines"])
        m = {e["match"]: e for e in self.load("merchants.json")["merchants"]}
        self.assertEqual(m["SHOP"]["category"], "Other")
        self.assertTrue(m["SHOP"]["unsure"])
        d = {x.get("match"): x for x in self.load("decisions.json")["decisions"]}
        self.assertEqual((d["SHOP"]["status"], d["SHOP"]["answer"]), ("confirmed", "Not sure"))
        self.assertEqual(d["CAFE"]["status"], "open")           # only what was answered is closed

    def test_who_a_bill_was_paid_to_is_remembered_as_its_brand(self):
        # feedback 104: a bank prints "TELEPHONE PMT"; the payee named once groups it with the card's charges
        r = confirm.run(self.ws, write=True, sets=["CAFE=Bills|Fido"])
        self.assertEqual(r["rc"], 0, r["lines"])
        m = {e["match"]: e for e in self.load("merchants.json")["merchants"]}
        self.assertEqual((m["CAFE"]["category"], m["CAFE"]["brand"]), ("Bills", "Fido"))

    def test_it_is_counted_and_not_asked_again(self):
        confirm.run(self.ws, write=True, sets=["SHOP=Not sure"])
        r = confirm.run(self.ws)
        self.assertEqual(r["unsure"], {"n": 1, "total": 100.0})
        self.assertNotIn("SHOP", [i["what"] for i in r["items"]])

    def test_a_transfer_not_sure_stays_a_transfer_and_is_closed(self):
        r0 = confirm.run(self.ws)
        n = next(i["n"] for i in r0["items"] if i["kind"] == "transfer")
        confirm.run(self.ws, write=True, sets=[f"{n}=不确定"])
        rows = list(csv.DictReader(open(layout.path(self.ws, "spending.csv"), encoding="utf-8")))
        self.assertEqual(len(rows), 4)                          # nothing became spending
        self.assertEqual(sum(1 for x in self.load("decisions.json")["decisions"] if x.get("answer") == "Not sure"), 1)

    def test_an_open_merchant_carries_its_days_and_their_company(self):
        it = next(i for i in confirm.run(self.ws)["items"] if i["what"] == "SHOP")
        self.assertEqual([x["d"] for x in it["recall"]["rows"]], ["2026-03-07", "2026-03-21"])
        self.assertEqual(it["recall"]["sameDays"][0]["with"], [{"what": "BAKERY", "a": 9.0}])

    def test_the_same_amount_moved_twice_is_one_question(self):
        tr = [i for i in confirm.run(self.ws)["items"] if i["kind"] == "transfer"]
        self.assertEqual(len({i["group"] for i in tr}), 1)
        self.assertIsNotNone(tr[0]["group"])
        first = next(i for i in tr if i["recall"]["rows"][0]["d"] == "2026-02-02")
        self.assertEqual(first["recall"]["sameDay"], [{"what": "Plan fee", "a": -16.95}])

    def test_money_moved_that_is_big_or_repeats_is_asked_first(self):
        tr = [i for i in confirm.run(self.ws)["items"] if i["kind"] == "transfer"]
        self.assertTrue(all(i["first"] for i in tr))                 # 650, twice
        self.assertFalse(any(i["first"] for i in confirm.run(self.ws)["items"] if i["kind"] == "merchant"))

    def test_money_in_with_no_name_waits_however_big(self):
        d = self.load("decisions.json")
        d["decisions"].append({"kind": "transfer", "what": "in", "default": "Other income", "status": "open",
                               "facts": {"kind": "credit", "amount": 3000, "date": "2026-02-05"},
                               "credit": {"date": "2026-02-05", "amount": 3000.0, "ledger": "chq.csv", "statement": "B1/20260213", "description": "e-Transfer received"}})
        json.dump(d, open(layout.path(self.ws, "decisions.json"), "w", encoding="utf-8"))
        it = next(i for i in confirm.run(self.ws)["items"] if i["credit"])
        self.assertFalse(it["first"])

    def test_a_small_amount_moved_once_waits(self):
        d = self.load("decisions.json")
        d["decisions"] = [x for x in d["decisions"] if x.get("kind") != "transfer"] + [
            {"kind": "transfer", "what": "sent", "default": "Transfer", "status": "open", "facts": {"kind": "sent", "amount": 40, "date": "2026-02-02"},
             "row": {"date": "2026-02-02", "amount": 40.0, "cur": "CAD", "note": "e-Transfer sent [B1/20260213]", "ledger": "chq.csv"}}]
        json.dump(d, open(layout.path(self.ws, "decisions.json"), "w", encoding="utf-8"))
        tr = [i for i in confirm.run(self.ws)["items"] if i["kind"] == "transfer"]
        self.assertEqual([i["first"] for i in tr], [False])

    def test_what_is_still_to_sort_and_the_owners_own_habit(self):
        r = confirm.run(self.ws)
        self.assertEqual(r["openOther"], 105.0)
        self.assertEqual(r["catUse"], {"Dining": 1})


if __name__ == "__main__":
    unittest.main()
