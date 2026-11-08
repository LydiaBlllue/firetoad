"""A TD chequing download (CSV): read by the `td` map, and its currency said by the owner.

The CSV names no currency, the way an OFX does, so setup asks: the wizard's answer lands on the
account only when its file is a CSV. Values here are invented.
"""
import os, sys, tempfile, unittest
import _paths
import wizard

sys.path.insert(0, os.path.join(_paths.SKILLS, "update-dashboard"))
from parsers import csv_bank

TD = ('"2026-03-30","MONTHLY ACCOUNT FEE","4.00",,"96.00"\n'
      '"2026-03-30","FEE REBATE",,"4.00","100.00"\n'
      '"2026-04-02","TRANSFER IN",,"50.00","150.00"\n')


class TdMap(unittest.TestCase):

    def test_a_chequing_download_is_read_and_follows(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "accountactivity.csv")
            with open(p, "w") as f:
                f.write(TD)
            self.assertEqual(csv_bank.detect(p), "td")
            r = csv_bank.parse(p, csv_bank.spec_of("td"))
        self.assertTrue(r["reconcile"]["ok"])
        self.assertEqual((r["opening"], r["closing"]), (100.0, 150.0))
        self.assertEqual([x["amount"] for x in r["rows"]], [-4.0, 4.0, 50.0])


class Currency(unittest.TestCase):

    def draft(self):
        return {"accounts": [{"inst": "TD", "name": "Chequing", "kind": "Chequing", "cur": "CAD", "balance": 150.0,
                              "doc": {"parser": "csv", "file": "accountactivity.csv"}},
                             {"inst": "OFX", "name": "Chequing 1111", "kind": "Chequing", "cur": "CAD", "balance": 10.0,
                              "doc": {"parser": "ofx", "file": "a.ofx"}}]}

    def test_the_wizard_asks_only_for_a_csv(self):
        rows = wizard.screens(self.draft(), "2026-04-03")["accounts"]["rows"]
        self.assertEqual([r["askCur"] for r in rows], [True, False])

    def test_the_answer_lands_on_a_csv_account_only(self):
        out = wizard.merge(self.draft(), {"accounts": [{"i": 0, "cur": "USD"}, {"i": 1, "cur": "USD"}]}, "2026-04-03")
        self.assertEqual([a["cur"] for a in out["accounts"]], ["USD", "CAD"])

    def test_anything_but_cad_or_usd_is_ignored(self):
        out = wizard.merge(self.draft(), {"accounts": [{"i": 0, "cur": "EUR"}]}, "2026-04-03")
        self.assertEqual(out["accounts"][0]["cur"], "CAD")


if __name__ == "__main__":
    unittest.main()
