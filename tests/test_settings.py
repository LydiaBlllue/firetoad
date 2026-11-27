"""settings.py — the numbers that are the owner's to choose (FINANCE.md §8e). One test per rule."""
import unittest
import _paths
import settings


def files(plan=None, flows=None, profile=None):
    return {"plan.json": dict(plan or {}), "funds.json": {"plan": {"flows": list(flows or [])}},
            "profile.json": dict(profile or {})}


class Reading(unittest.TestCase):

    def test_a_value_never_given_is_the_default(self):
        self.assertEqual(settings.value("importDay", files()), 1)
        self.assertIsNone(settings.stored("importDay", files()))

    def test_a_stored_value_wins_over_the_default(self):
        self.assertEqual(settings.value("importDay", files(profile={"importDay": 26})), 26)

    def test_a_plan_figure_is_read_from_its_flow(self):
        f = files(flows=[{"kind": "income", "amount": 4300}, {"kind": "saving", "amount": 700, "to": "broker"},
                         {"kind": "saving", "amount": 300, "to": "savings"}, {"kind": "everyday", "amount": 1500}])
        self.assertEqual([settings.value(k, f) for k in ("takeHome", "invest", "everyday")], [4300, 700, 1500])

    def test_a_flow_with_no_amount_is_not_set_not_zero(self):
        self.assertIsNone(settings.value("everyday", files(flows=[{"kind": "everyday", "amount": None}])))

    def test_a_flow_that_starts_at_fire_is_not_this_months_figure(self):
        f = files(flows=[{"kind": "income", "amount": 900, "starts": "fire"}])
        self.assertIsNone(settings.stored("takeHome", f))

    def test_a_figure_made_of_several_flows_is_locked(self):
        f = files(flows=[{"kind": "income", "amount": 2000}, {"kind": "income", "amount": 500}])
        self.assertEqual(settings.locked("takeHome", f), "several")
        self.assertEqual(settings.value("takeHome", f), 2500)
        with self.assertRaises(ValueError):
            settings.write("takeHome", 3000, f, "2026-01-02")


class Checking(unittest.TestCase):

    def test_money_reads_the_way_it_is_typed(self):
        self.assertEqual(settings.check("planBase", "$3,600")[0], 3600)
        self.assertEqual(settings.check("everyday", 1250.5)[0], 1250.5)

    def test_money_is_never_negative_and_never_a_word(self):
        self.assertIsNone(settings.check("invest", -5)[0])
        self.assertIsNone(settings.check("invest", "a lot")[0])
        self.assertIsNone(settings.check("invest", None)[0])
        self.assertIsNone(settings.check("invest", True)[0])

    def test_the_import_day_is_a_whole_day_every_month_has(self):
        self.assertEqual(settings.check("importDay", "26")[0], 26)
        self.assertIsNone(settings.check("importDay", 29)[0])
        self.assertIsNone(settings.check("importDay", 0)[0])
        self.assertIsNone(settings.check("importDay", 5.5)[0])

    def test_an_unknown_key_is_refused(self):
        self.assertIsNone(settings.check("colour", 3)[0])


class Writing(unittest.TestCase):

    def test_a_change_lands_where_the_value_lives_and_is_dated(self):
        f = files({"planBase": 3000}, [{"kind": "everyday", "amount": 1500}], {"importDay": 1})
        self.assertEqual(settings.write("planBase", 3600, f, "2026-01-02"), ["plan.json"])
        self.assertEqual(settings.write("everyday", 1800, f, "2026-01-03"), ["funds.json", "plan.json"])
        self.assertEqual(settings.write("importDay", 26, f, "2026-01-04"), ["plan.json", "profile.json"])
        self.assertEqual(f["plan.json"]["planBase"], 3600)
        self.assertEqual(f["funds.json"]["plan"]["flows"][0]["amount"], 1800)
        self.assertEqual(f["profile.json"]["importDay"], 26)
        self.assertEqual(f["plan.json"]["changed"], {"planBase": "2026-01-02", "everyday": "2026-01-03", "importDay": "2026-01-04"})

    def test_a_first_value_makes_the_flow(self):
        f = files()
        settings.write("invest", 500, f, "2026-01-02")
        self.assertEqual(f["funds.json"]["plan"]["flows"], [{"key": "invest", "kind": "saving", "name": "Invest", "to": "broker", "amount": 500}])
        self.assertEqual(settings.value("invest", f), 500)

    def test_going_back_to_the_default_writes_the_default(self):
        f = files()
        settings.write("importDay", 26, f, "2026-01-02")
        self.assertEqual(settings.value("importDay", f), 26)
        settings.reset("importDay", f, "2026-01-03")
        self.assertEqual(settings.value("importDay", f), 1)

    def test_a_figure_with_no_default_cannot_go_back(self):
        with self.assertRaises(ValueError):
            settings.reset("planBase", files({"planBase": 3000}), "2026-01-02")


class ThePagesRows(unittest.TestCase):

    def test_every_row_of_the_table_reaches_the_page_with_its_value(self):
        f = files({"planBase": 3000, "changed": {"importDay": "2026-01-02"}}, profile={"importDay": 26})
        rows = {r["key"]: r for r in settings.rows(f)}
        self.assertEqual(set(rows), {r["key"] for r in settings.TABLE})
        self.assertEqual((rows["importDay"]["v"], rows["importDay"]["isDef"], rows["importDay"]["changed"]), (26, False, "2026-01-02"))
        self.assertEqual((rows["planBase"]["v"], rows["planBase"]["isDef"]), (3000, False))
        self.assertTrue(settings.rows(files())[0]["isDef"])

    def test_every_row_has_both_languages_and_a_stage(self):
        for r in settings.TABLE:
            self.assertTrue(all(r.get(k) for k in ("en", "zh", "whyEn", "whyZh")), r["key"])
            self.assertIn(r["stage"], settings.STAGES)


class TheReturn(unittest.TestCase):

    def test_it_is_five_percent_until_the_owner_says_otherwise(self):
        self.assertEqual(settings.value("growth", {"plan.json": {}}), 5)

    def test_a_half_point_is_a_legal_value_and_twelve_is_not(self):
        self.assertEqual(settings.check("growth", "6.5"), (6.5, None))
        self.assertIsNone(settings.check("growth", "12")[0])

    def test_it_lives_in_the_plan_with_its_day(self):
        f = {"plan.json": {}}
        self.assertEqual(settings.write("growth", 7, f, "2026-11-15"), ["plan.json"])
        self.assertEqual(f["plan.json"], {"growth": 7, "changed": {"growth": "2026-11-15"}})


if __name__ == "__main__":
    unittest.main()
