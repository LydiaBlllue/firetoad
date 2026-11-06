"""categories.py — the fifteen categories, their groups, and a charge that repeats (FINANCE.md §3a)."""
import unittest
import _paths
import categories as C


class Groups(unittest.TestCase):

    def test_fifteen_categories_other_last(self):
        self.assertEqual(len(C.CATEGORIES), 15)
        self.assertEqual(C.CATEGORIES[-1], "Other")
        self.assertEqual(len(set(C.CATEGORIES)), 15)

    def test_default_groups_housing_and_bills_are_bills(self):
        g = C.groups({})
        self.assertEqual({k for k, v in g.items() if v == "bills"}, {"Housing", "Bills"})

    def test_owner_may_move_a_category(self):
        g = C.groups({"categoryGroups": {"Transport": "bills"}})
        self.assertEqual(g["Transport"], "bills")

    def test_an_unknown_group_name_falls_back_to_the_default(self):
        g = C.groups({"categoryGroups": {"Transport": "monthly"}})
        self.assertEqual(g["Transport"], "everyday")

    def test_not_in_fire_defaults_to_education_and_an_empty_list_means_none(self):
        self.assertEqual(C.not_in_fire({}), ["Education"])
        self.assertEqual(C.not_in_fire({"notInFire": []}), [])

    def test_page_table_marks_no_fire_only_where_told(self):
        t = C.page_table({})
        self.assertEqual([e["k"] for e in t if e.get("noFire")], ["Education"])
        self.assertEqual(t[0]["c"], "var(--c-grocery)")


class Brand(unittest.TestCase):
    """The merchant of a row, read off a truncated statement string — never for meaning."""

    def test_statement_tag_and_store_number_come_off(self):
        self.assertEqual(C.brand_of("TIM HORTONS #1234 TORONTO ON [RBC1111/2026-09]"), "TIM HORTONS")

    def test_web_suffix_and_place_are_not_a_name(self):
        self.assertEqual(C.brand_of("APPLE.COM/BILL TORONTO ON"), "APPLE")

    def test_a_repeat_of_itself_is_said_once(self):
        self.assertEqual(C.brand_of("NETFLIX.COM NETFLIX.COM"), "NETFLIX")

    def test_a_payment_processor_prefix_comes_off(self):
        self.assertEqual(C.brand_of("SQ *BLUE BOTTLE COFFEE"), "BLUE BOTTLE")

    def test_amazon_prime_stays_apart_from_amazon(self):
        self.assertNotEqual(C.brand_of("AMAZON PRIME MEMBER"), C.brand_of("AMAZON.CA"))

    def test_empty_and_none(self):
        self.assertEqual(C.brand_of(""), "")
        self.assertEqual(C.brand_of(None), "")


def rows(brand, *month_amounts, category="Entertainment", day="05"):
    """[('2026-01', 9.99), ...] -> spending rows for one merchant."""
    return [{"date": f"{m}-{day}", "note": f"{brand} [X/{m}]", "amount": a, "category": category}
            for m, a in month_amounts]


class Recurring(unittest.TestCase):
    """A subscription is a charge that repeats -- measured, never read off a name."""

    def test_one_price_three_months_running_is_recurring(self):
        r = C.recurring(rows("NETFLIX.COM", ("2026-01", 16.49), ("2026-02", 16.49), ("2026-03", 16.49)))
        self.assertIn("NETFLIX", r)
        self.assertEqual((r["NETFLIX"]["amount"], r["NETFLIX"]["months"]), (16.49, 3))

    def test_two_months_are_not_enough(self):
        r = C.recurring(rows("NETFLIX.COM", ("2026-01", 16.49), ("2026-02", 16.49)))
        self.assertEqual(r, {})

    def test_a_brand_seen_once_is_never_one_whatever_the_name(self):
        # 2026-09-06: LIGHTHOUSE PUBLICATION was a notebook.
        r = C.recurring(rows("LIGHTHOUSE PUBLICATION", ("2026-01", 24.00)))
        self.assertEqual(r, {})

    def test_a_coffee_once_a_month_is_not_one_because_the_amount_moves(self):
        r = C.recurring(rows("CAFE", ("2026-01", 4.10), ("2026-02", 6.75), ("2026-03", 5.20), ("2026-04", 3.90)))
        self.assertEqual(r, {})

    def test_a_plan_whose_price_went_up_once_still_repeats(self):
        r = C.recurring(rows("SPOTIFY", ("2026-01", 10.99), ("2026-02", 10.99), ("2026-03", 10.99),
                             ("2026-04", 11.99), ("2026-05", 11.99)))
        self.assertIn("SPOTIFY", r)

    @unittest.expectedFailure
    def test_after_a_price_rise_the_amount_shown_is_the_new_price(self):
        # Known gap (2026-11-06): when the old price alone already repeats three months, the
        # one-price rule wins and reports it, so the page shows the plan at the price it no
        # longer costs. The docstring promises "the latest".
        r = C.recurring(rows("SPOTIFY", ("2026-01", 10.99), ("2026-02", 10.99), ("2026-03", 10.99),
                             ("2026-04", 11.99), ("2026-05", 11.99)))
        self.assertEqual(r["SPOTIFY"]["amount"], 11.99)

    def test_housing_cash_and_fees_never_recur(self):
        for cat in ("Housing", "Cash", "Fees"):
            r = C.recurring(rows("LANDLORD", ("2026-01", 1800), ("2026-02", 1800), ("2026-03", 1800), category=cat))
            self.assertEqual(r, {}, cat)

    def test_refunds_do_not_count(self):
        r = C.recurring(rows("NETFLIX.COM", ("2026-01", -16.49), ("2026-02", -16.49), ("2026-03", -16.49)))
        self.assertEqual(r, {})

    def test_owner_brand_map_joins_two_spellings(self):
        # "NETFLIX.COM" and "NETFLIX INC" already read as one brand (web suffix, INC dropped);
        # a spelling the rules cannot join needs the owner's map.
        xs = rows("NETFLIX.COM", ("2026-01", 16.49), ("2026-02", 16.49)) + rows("NFLX DIGITAL", ("2026-03", 16.49))
        self.assertEqual(C.recurring(xs), {})                                  # two names, neither three months
        r = C.recurring(xs, brands={"NFLX DIGITAL": "NETFLIX"})
        self.assertEqual(r["NETFLIX"]["months"], 3)

    def test_a_gap_of_one_month_in_six_is_tolerated(self):
        r = C.recurring(rows("GYM", ("2026-01", 40), ("2026-02", 40), ("2026-04", 40), ("2026-05", 40), ("2026-06", 40)))
        self.assertIn("GYM", r)


class Yearly(unittest.TestCase):

    def test_a_charge_a_year_apart_within_a_tenth_is_yearly(self):
        self.assertEqual(C.yearly(rows("INSURER", ("2025-03", 1200), ("2026-03", 1260))), {"INSURER"})

    def test_two_months_apart_is_not(self):
        self.assertEqual(C.yearly(rows("INSURER", ("2026-01", 1200), ("2026-03", 1200))), set())

    def test_declared_counts_only_if_seen(self):
        self.assertEqual(C.yearly(rows("CLUB", ("2026-01", 99)), declared=("CLUB", "GHOST")), {"CLUB"})

    def test_housing_is_never_yearly(self):
        self.assertEqual(C.yearly(rows("TAX", ("2025-07", 3000), ("2026-07", 3000), category="Housing")), set())


class Monthly(unittest.TestCase):
    """_monthly: at least n months, hardly one missed between first and last."""

    def test_boundaries(self):
        self.assertFalse(C._monthly(["2026-01", "2026-02"], 3))
        self.assertTrue(C._monthly(["2026-01", "2026-02", "2026-03"], 3))
        self.assertTrue(C._monthly(["2025-11", "2025-12", "2026-01"], 3))        # across a year end
        self.assertTrue(C._monthly(["2026-01", "2026-02", "2026-04"], 3))        # one gap allowed
        self.assertFalse(C._monthly(["2026-01", "2026-02", "2026-06"], 3))       # three missed in six


if __name__ == "__main__":
    unittest.main()
