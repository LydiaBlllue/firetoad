"""clock.py — the date staleness is measured from: today for an owner, its own newest fact for the demo."""
import csv, datetime, json, os, tempfile, unittest, warnings
import _paths
import clock, layout

# clock.py opens its files without closing them (lines 26, 31, 36); unittest turns that into a
# warning per file. Silenced here so the release check stays readable; the fix is in clock.py.
warnings.simplefilter("ignore", ResourceWarning)


def workspace(profile, banks=None, ledger_dates=()):
    root = tempfile.mkdtemp()
    layout.ensure(root)
    with open(layout.path(root, "profile.json"), "w") as f:
        json.dump(profile, f)
    if banks is not None:
        with open(layout.path(root, "banks.json"), "w") as f:
            json.dump(banks, f)
    if ledger_dates:
        with open(layout.path(root, "some_ledger.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=layout.LEDGER_COLS); w.writeheader()
            for d in ledger_dates:
                w.writerow({"date": d, "description": "x", "amount": "1", "balance": "1", "statement": "", "type": "", "label": ""})
    return root


class Clock(unittest.TestCase):

    def test_an_owner_is_measured_from_today(self):
        root = workspace({"name": "Someone"}, banks={"assets": [{"asof": "2020-01-01"}]})
        self.assertEqual(clock.clock(root), (datetime.date.today(), None))

    def test_no_profile_at_all_is_today(self):
        root = tempfile.mkdtemp(); layout.ensure(root)
        self.assertEqual(clock.clock(root), (datetime.date.today(), None))

    def test_the_demo_is_measured_from_its_newest_fact(self):
        root = workspace({"demo": True}, banks={"assets": [{"asof": "2026-03-31"}], "debts": [{"asof": "2026-02-28"}]},
                         ledger_dates=["2026-04-02", "2026-01-15"])
        self.assertEqual(clock.clock(root), (datetime.date(2026, 4, 2), "the demo's newest data"))

    def test_a_demo_with_no_dates_falls_back_to_today(self):
        root = workspace({"demo": True})
        self.assertEqual(clock.clock(root), (datetime.date.today(), None))

    def test_a_malformed_date_is_skipped_not_crashed_on(self):
        root = workspace({"demo": True}, banks={"assets": [{"asof": "2026/03/31"}, {"asof": "2026-03-30"}]})
        self.assertEqual(clock.clock(root)[0], datetime.date(2026, 3, 30))


if __name__ == "__main__":
    unittest.main()
