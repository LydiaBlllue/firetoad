"""layout.py — which of the three findata folders a bare filename lives in (schema 6)."""
import os, tempfile, unittest
import _paths
import layout


class Layer(unittest.TestCase):

    def test_declarations_facts_history(self):
        self.assertEqual(layout.layer("accounts.json"), "register")
        self.assertEqual(layout.layer("imports.json"), "history")
        self.assertEqual(layout.layer("spending.csv"), "ledgers")

    def test_a_name_no_list_claims_is_a_ledger(self):
        # The ledger CSVs are named in accounts.json, not here.
        self.assertEqual(layout.layer("rbc_chequing.csv"), "ledgers")
        self.assertEqual(layout.layer("anything_at_all.json"), "ledgers")

    def test_a_path_is_judged_by_its_basename(self):
        self.assertEqual(layout.layer("findata/register/plan.json"), "register")


class Rel(unittest.TestCase):

    def test_bare_name_gets_its_folder(self):
        self.assertEqual(layout.rel("funds.json"), "findata/register/funds.json")
        self.assertEqual(layout.rel("filings.json"), "findata/history/filings.json")
        self.assertEqual(layout.rel("banks.json"), "findata/ledgers/banks.json")

    def test_a_name_with_a_folder_is_left_alone(self):
        self.assertEqual(layout.rel("findata/ledgers/x.csv"), "findata/ledgers/x.csv")
        self.assertEqual(layout.rel("ledgers/x.csv"), "findata/ledgers/x.csv")

    def test_every_register_and_history_name_is_in_exactly_one_list(self):
        self.assertEqual(set(layout.REGISTER) & set(layout.HISTORY), set())


class Path(unittest.TestCase):
    """A workspace not yet moved to schema 6 keeps its files flat; the flat file is what exists,
    so it is what is returned."""

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def test_split_workspace_returns_the_folder_path(self):
        layout.ensure(self.root)
        p = layout.path(self.root, "plan.json")
        self.assertEqual(os.path.relpath(p, self.root), os.path.join("findata", "register", "plan.json"))
        self.assertTrue(layout.is_split(self.root))

    def test_flat_workspace_returns_the_flat_file_while_it_exists(self):
        os.makedirs(os.path.join(self.root, "findata"))
        flat = os.path.join(self.root, "findata", "plan.json")
        open(flat, "w").close()
        self.assertEqual(layout.path(self.root, "plan.json"), flat)
        self.assertFalse(layout.is_split(self.root))

    def test_once_the_folder_exists_the_flat_file_is_ignored(self):
        layout.ensure(self.root)
        open(os.path.join(self.root, "findata", "plan.json"), "w").close()
        p = layout.path(self.root, "plan.json")
        self.assertIn("register", p)

    def test_ensure_is_idempotent(self):
        layout.ensure(self.root); layout.ensure(self.root)
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "findata"))), sorted(layout.FOLDERS))


if __name__ == "__main__":
    unittest.main()
