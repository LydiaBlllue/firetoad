"""ocr.py — the pure half: amounts out of a line of text, and which amount on a screenshot is
the balance. The Vision call itself is not tested here (it needs macOS and ocrmac); the
ranking is, because it is the rule the model used to apply by eye: the headline number, near
the balance word, never the yield.
"""
import datetime
import unittest

import _paths  # noqa: F401
import ocr


class Amounts(unittest.TestCase):
    def test_currency_signs_and_thousands(self):
        self.assertEqual(ocr.amounts("余额 ¥203,134.64"), [203134.64])
        self.assertEqual(ocr.amounts("US$17.56 available"), [17.56])
        self.assertEqual(ocr.amounts("C$1,065.33"), [1065.33])

    def test_plain_integers_are_not_amounts(self):
        # an account number, a date fragment, a count: no decimals and no thousands separator
        self.assertEqual(ocr.amounts("卡号 4016 2026"), [])

    def test_several_on_one_line(self):
        self.assertEqual(ocr.amounts("市值 29,000.64 收益 -63.57"), [29000.64, 63.57])


class Dates(unittest.TestCase):
    def test_full_and_chinese(self):
        today = datetime.date(2026, 11, 6)
        self.assertIn("2026-10-23", ocr.dates("2026-10-23 10:41", today))
        self.assertIn("2026-10-26", ocr.dates("2026年10月26日", today))

    def test_month_day_rolls_back_a_year_when_in_the_future(self):
        today = datetime.date(2026, 1, 5)
        self.assertEqual(ocr.dates("12-30 转入", today), ["2025-12-30"])


class Candidates(unittest.TestCase):
    """A screenshot as Vision returns it: boxes with y from the top, sizes as fractions."""

    def shot(self):
        return [
            {"text": "我的账户", "x": 0.4, "y": 0.05, "w": 0.2, "h": 0.03},
            {"text": "可用余额(元)", "x": 0.1, "y": 0.20, "w": 0.3, "h": 0.025},
            {"text": "3,412.77", "x": 0.1, "y": 0.24, "w": 0.4, "h": 0.06},       # the headline number, under the label
            {"text": "昨日收益 0.00", "x": 0.1, "y": 0.32, "w": 0.3, "h": 0.025},
            {"text": "七日年化 1.35%", "x": 0.5, "y": 0.32, "w": 0.3, "h": 0.025},
            {"text": "转账 -1,200.00", "x": 0.1, "y": 0.60, "w": 0.4, "h": 0.03},
            {"text": "2026-10-19 09:12", "x": 0.1, "y": 0.64, "w": 0.4, "h": 0.02},
        ]

    def test_the_headline_under_the_balance_word_wins(self):
        cands, ds = ocr.candidates(self.shot(), "一家银行 App · 我的账户 — 可用余额(元)", datetime.date(2026, 11, 6))
        self.assertEqual(cands[0]["amount"], 3412.77)
        self.assertEqual(cands[0]["near"], "可用余额(元)")
        self.assertEqual(ds, ["2026-10-19"])

    def test_a_yield_line_ranks_below_a_transaction(self):
        cands, _ = ocr.candidates(self.shot(), None, datetime.date(2026, 11, 6))
        order = [c["amount"] for c in cands]
        self.assertLess(order.index(1200.0), order.index(1.35))

    def test_each_amount_once_and_at_most_top(self):
        boxes = [{"text": f"{i}.00", "x": 0, "y": i / 100, "w": .1, "h": .01} for i in range(1, 20)]
        boxes.append({"text": "5.00", "x": 0, "y": .9, "w": .1, "h": .01})
        cands, _ = ocr.candidates(boxes, None, datetime.date(2026, 11, 6), top=5)
        self.assertEqual(len(cands), 5)
        self.assertEqual(len({c["amount"] for c in cands}), 5)

    def test_the_english_balance_word_counts_too(self):
        boxes = [{"text": "Available balance", "x": 0.1, "y": 0.1, "w": 0.3, "h": 0.02},
                 {"text": "$1,065.33", "x": 0.1, "y": 0.13, "w": 0.3, "h": 0.04},
                 {"text": "$9,999.99", "x": 0.1, "y": 0.50, "w": 0.3, "h": 0.04}]
        cands, _ = ocr.candidates(boxes, "Wealthsimple app · Chequing", datetime.date(2026, 11, 6))
        self.assertEqual(cands[0]["amount"], 1065.33)


if __name__ == "__main__":
    unittest.main()
