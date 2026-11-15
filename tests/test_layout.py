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


class TheAppsOwnFolder(unittest.TestCase):
    """.firetoad — it was .jade until 1.0.5 (layout.state_dir, jlock)."""

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def test_a_new_workspace_gets_the_new_name_and_nothing_is_made(self):
        self.assertEqual(layout.state_dir(self.root), os.path.join(self.root, ".firetoad"))
        self.assertEqual(os.listdir(self.root), [])

    def test_a_folder_under_the_old_name_is_renamed_with_what_is_in_it(self):
        os.makedirs(os.path.join(self.root, ".jade", "log"))
        open(os.path.join(self.root, ".jade", "settings.json"), "w").write("{}")
        d = layout.state_dir(self.root)
        self.assertEqual(sorted(os.listdir(self.root)), [".firetoad"])
        self.assertEqual(sorted(os.listdir(d)), ["log", "settings.json"])

    def test_when_both_exist_the_new_one_is_used_and_the_old_left_alone(self):
        os.makedirs(os.path.join(self.root, ".jade")); os.makedirs(os.path.join(self.root, ".firetoad"))
        self.assertEqual(layout.state_dir(self.root), os.path.join(self.root, ".firetoad"))
        self.assertTrue(os.path.isdir(os.path.join(self.root, ".jade")))

    def test_the_lock_has_the_new_name(self):
        import jlock
        self.assertIsNone(jlock.acquire(self.root, "import"))
        self.assertTrue(os.path.exists(os.path.join(self.root, ".firetoad.lock")))
        jlock.release(self.root)
        self.assertFalse(os.path.exists(os.path.join(self.root, ".firetoad.lock")))

    def test_a_live_holder_under_the_old_lock_name_is_still_a_holder(self):
        import jlock, json
        json.dump({"pid": os.getppid(), "verb": "import", "since": "2026-01-01T00:00:00"}, open(os.path.join(self.root, ".jade.lock"), "w"))
        self.assertEqual(jlock.held_by_other(self.root), "import")

    def test_a_dead_holder_under_the_old_lock_name_is_cleared(self):
        import jlock, json
        json.dump({"pid": 2 ** 22 + 12345, "verb": "import", "since": "2026-01-01T00:00:00"}, open(os.path.join(self.root, ".jade.lock"), "w"))
        self.assertIsNone(jlock.held_by_other(self.root))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".jade.lock")))


if __name__ == "__main__":
    unittest.main()
