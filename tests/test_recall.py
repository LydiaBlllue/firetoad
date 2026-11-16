"""recall.py — what helps a person remember a charge. One test per rule."""
import unittest
import _paths  # noqa: F401
import recall


def row(date, amount, note="SHOP"):
    return {"date": date, "amount": str(amount), "note": note}


SHOP = lambda r: r["note"] == "SHOP"


class TheCharges(unittest.TestCase):

    def test_each_charge_has_its_day_amount_and_weekday(self):
        ch = recall.charges([row("2026-03-07", 12.5), row("2026-03-09", 4, "OTHER")], SHOP)
        self.assertEqual(ch, [{"d": "2026-03-07", "a": 12.5, "w": 5}])      # a Saturday

    def test_oldest_first_and_refunds_left_out(self):
        ch = recall.charges([row("2026-03-21", 9), row("2026-03-07", 8), row("2026-03-10", -8)], SHOP)
        self.assertEqual([x["d"] for x in ch], ["2026-03-07", "2026-03-21"])


class TheRhythm(unittest.TestCase):

    def ch(self, *days_amounts):
        return recall.charges([row(d, a) for d, a in days_amounts], SHOP)

    def test_two_charges_are_not_a_rhythm(self):
        self.assertIsNone(recall.rhythm(self.ch(("2026-01-03", 10), ("2026-02-03", 10))))

    def test_the_same_amount_at_the_start_of_every_month(self):
        r = recall.rhythm(self.ch(("2026-01-02", 650), ("2026-02-02", 650), ("2026-03-02", 650), ("2026-04-01", 650)))
        self.assertEqual((r["every"], r["same"], r["when"], r["about"]), ("month", True, "start", 650))

    def test_every_other_saturday_at_about_an_amount(self):
        r = recall.rhythm(self.ch(("2026-03-07", 148.2), ("2026-03-21", 131.75), ("2026-04-04", 152.1), ("2026-04-18", 140)))
        self.assertEqual((r["every"], r["weekday"], r["same"]), ("2weeks", 5, False))
        self.assertAlmostEqual(r["about"], 144.1)

    def test_every_week(self):
        r = recall.rhythm(self.ch(("2026-03-02", 5), ("2026-03-09", 6), ("2026-03-16", 7), ("2026-03-23", 5)))
        self.assertEqual((r["every"], r["weekday"]), ("week", 0))

    def test_scattered_days_and_amounts_say_nothing(self):
        self.assertIsNone(recall.rhythm(self.ch(("2026-01-03", 10), ("2026-01-29", 44), ("2026-04-14", 7))))

    def test_the_same_amount_with_no_rhythm_is_still_worth_saying(self):
        r = recall.rhythm(self.ch(("2026-01-03", 20), ("2026-01-29", 20), ("2026-04-14", 20)))
        self.assertEqual((r["every"], r["same"]), (None, True))

    def test_a_month_end_charge(self):
        r = recall.rhythm(self.ch(("2026-01-30", 80), ("2026-02-27", 81), ("2026-03-30", 79)))
        self.assertEqual((r["every"], r["when"]), ("month", "end"))


class TheSameDays(unittest.TestCase):

    ROWS = [row("2026-03-07", 148), row("2026-03-07", 62, "FUEL"), row("2026-03-07", 11, "BAKERY"), row("2026-03-07", 3, "PARKING"),
            row("2026-03-21", 131), row("2026-04-04", 152), row("2026-04-04", 58, "FUEL"), row("2026-04-04", -5, "REFUND")]

    def test_the_newest_days_that_have_company_with_the_biggest_other_charges(self):
        got = recall.same_days(self.ROWS, recall.charges(self.ROWS, SHOP), SHOP, lambda r: r["note"])
        self.assertEqual([x["d"] for x in got], ["2026-04-04", "2026-03-07"])
        self.assertEqual(got[0]["with"], [{"what": "FUEL", "a": 58.0}])
        self.assertEqual([o["what"] for o in got[1]["with"]], ["FUEL", "BAKERY"])

    def test_a_day_with_nothing_else_is_not_listed(self):
        rows = [row("2026-03-21", 131)]
        self.assertEqual(recall.same_days(rows, recall.charges(rows, SHOP), SHOP, lambda r: r["note"]), [])


class MoneyMoved(unittest.TestCase):

    LEDGER = [{"date": "2026-02-02", "amount": "-650.00", "description": "e-Transfer sent"},
              {"date": "2026-02-02", "amount": "-16.95", "description": "Plan fee"},
              {"date": "2026-02-03", "amount": "2150.00", "description": "Payroll"}]

    def test_what_else_moved_that_day_without_the_row_asked_about(self):
        self.assertEqual(recall.ledger_day(self.LEDGER, "2026-02-02", skip=650), [{"what": "Plan fee", "a": -16.95}])

    def test_the_other_end_in_another_account_within_a_few_days(self):
        other = {"savings.csv": [{"date": "2026-02-04", "amount": "650.00"}], "chequing.csv": self.LEDGER}
        self.assertEqual(recall.counterpart(other, "2026-02-02", -650, "chequing.csv"), {"ledger": "savings.csv", "d": "2026-02-04"})

    def test_the_same_amount_a_week_later_is_not_the_other_end(self):
        other = {"savings.csv": [{"date": "2026-02-12", "amount": "650.00"}]}
        self.assertIsNone(recall.counterpart(other, "2026-02-02", -650, "chequing.csv"))

    def test_the_account_itself_is_not_its_own_other_end(self):
        self.assertIsNone(recall.counterpart({"chequing.csv": [{"date": "2026-02-02", "amount": "650.00"}]}, "2026-02-02", -650, "chequing.csv"))


class OneQuestion(unittest.TestCase):

    def test_two_or_more_that_share_a_key_are_one_group(self):
        items = [{"k": "a"}, {"k": "b"}, {"k": "a"}, {"k": None}]
        g = recall.groups(items, lambda i: i["k"])
        self.assertEqual({k: len(v) for k, v in g.items()}, {"a": 2})


if __name__ == "__main__":
    unittest.main()
