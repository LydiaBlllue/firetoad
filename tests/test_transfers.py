"""A transfer to or from an account outside the register is known by the number the statement
prints for the other side; once the owner says that account is their own, it is not asked again.
"""
import unittest

import _paths  # noqa: F401
import update


class OtherAccount(unittest.TestCase):
    def test_the_last_number_that_is_not_this_accounts_own(self):
        acc = {"id": "…471"}
        self.assertEqual(update.other_account("OnlineTransfer,TF0006#4471-9032", acc), "9032")
        self.assertEqual(update.other_account("Online Banking transfer - 7082", {"id": "2306"}), "7082")

    def test_no_number_no_account(self):
        self.assertIsNone(update.other_account("Transfer", {"id": "…471"}))
        self.assertIsNone(update.other_account("Transfer 4471", {"id": "…471"}))   # only its own


if __name__ == "__main__":
    unittest.main()
