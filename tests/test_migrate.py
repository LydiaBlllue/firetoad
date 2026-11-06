"""tools/migrate.py and the migrate_<n>to<n+1> steps — a workspace at an older schema reaches the
tool's, and the money still adds up when it gets there.

A migration runs once, on a user's real data, with no way back. Nothing else tests the chain
end to end. Each folder under tests/fixtures/ is the demo owner's findata/ as a release left it
(`schema9/`: the first public commit; `schema18/`: release 1.0.0), and every test here copies
one to a temporary folder — the fixtures themselves are never written.

When rebuild.py's SCHEMA goes up, this file needs nothing: `Chain` runs the new step over every
fixture, and `CurrentDemo` fails until demo.py writes the new schema. Add a fixture for each
schema a release shipped — that is the only schema a real user can be at.
"""
import glob, hashlib, json, os, shutil, subprocess, sys, tempfile, unittest
import _paths
import layout

ROOT = _paths.ROOT
MIGRATE = os.path.join(ROOT, "tools", "migrate.py")
CHECK = os.path.join(ROOT, ".claude", "skills", "workspace-checks", "scripts", "check_data.py")
REBUILD = os.path.join(ROOT, ".claude", "skills", "update-dashboard", "scripts", "rebuild.py")
FIXTURES = sorted(glob.glob(os.path.join(ROOT, "tests", "fixtures", "schema*")),
                  key=lambda p: int(os.path.basename(p)[6:]))


def tool_schema():
    sys.path.insert(0, os.path.dirname(MIGRATE))
    import migrate
    return migrate.tool_schema()


def workspace_from(findata_parent):
    """A temporary workspace with a copy of that findata/, empty archive/ and dashboards/, and the
    tool's templates (so the page can be built from the migrated data)."""
    ws = tempfile.mkdtemp()
    shutil.copytree(os.path.join(findata_parent, "findata"), os.path.join(ws, "findata"))
    os.makedirs(os.path.join(ws, "archive")); os.makedirs(os.path.join(ws, "dashboards"))
    shutil.copytree(os.path.join(ROOT, "templates"), os.path.join(ws, "templates"))
    return ws


def run(*cmd, cwd=None):
    p = subprocess.run([sys.executable, *cmd], cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def read_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_json(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def schema_of(ws):
    return read_json(layout.path(ws, "profile.json")).get("schema")


def digest(folder):
    h = hashlib.sha256()
    for dp, _, fs in sorted(os.walk(folder)):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            with open(p, "rb") as f:
                h.update(os.path.relpath(p, folder).encode()); h.update(f.read())
    return h.hexdigest()


class Chain(unittest.TestCase):
    """Every fixture reaches the tool's schema, reconciles, and builds a page."""

    def test_fixtures_exist(self):
        self.assertTrue(FIXTURES, "tests/fixtures/schema<N>/findata is missing")

    def test_each_fixture_migrates_to_the_tool_schema(self):
        want = tool_schema()
        for fx in FIXTURES:
            with self.subTest(fixture=os.path.basename(fx)):
                ws = workspace_from(fx)
                rc, out = run(MIGRATE, ws)
                self.assertEqual(rc, 0, out)
                self.assertEqual(schema_of(ws), want)
                self.assertTrue(layout.is_split(ws), "findata/ is not in its three folders")

    def test_the_migrated_money_reconciles(self):
        for fx in FIXTURES:
            with self.subTest(fixture=os.path.basename(fx)):
                ws = workspace_from(fx)
                run(MIGRATE, ws)
                rc, out = run(CHECK, ws, "--money")
                self.assertEqual(rc, 0, out)

    def test_the_migrated_data_builds_a_page(self):
        for fx in FIXTURES:
            with self.subTest(fixture=os.path.basename(fx)):
                ws = workspace_from(fx)
                run(MIGRATE, ws)
                rc, out = run(REBUILD, ws, "--write")
                self.assertEqual(rc, 0, out)
                self.assertTrue(glob.glob(os.path.join(ws, "dashboards", "*.html")))

    def test_a_second_run_changes_nothing(self):
        for fx in FIXTURES:
            with self.subTest(fixture=os.path.basename(fx)):
                ws = workspace_from(fx)
                run(MIGRATE, ws)
                before = digest(os.path.join(ws, "findata"))
                rc, out = run(MIGRATE, ws)
                self.assertEqual(rc, 0, out)
                self.assertIn("Nothing to do", out)
                self.assertEqual(digest(os.path.join(ws, "findata")), before)


class CurrentDemo(unittest.TestCase):

    def test_the_shipped_demo_is_already_at_the_tool_schema(self):
        # demo.py writes the schema by hand; forgetting it ships a demo every clone has to migrate.
        self.assertEqual(schema_of(ROOT), tool_schema())
        rc, out = run(MIGRATE, ROOT)
        self.assertEqual(rc, 0); self.assertIn("Nothing to do", out)

    def test_every_step_from_the_oldest_fixture_has_a_script(self):
        oldest = int(os.path.basename(FIXTURES[0])[6:])
        for n in range(oldest, tool_schema()):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tools", f"migrate_{n}to{n + 1}.py")), f"migrate_{n}to{n + 1}.py")


class Refusals(unittest.TestCase):

    def test_a_schema_with_no_step_script_is_refused_not_guessed(self):
        ws = workspace_from(FIXTURES[0])
        p = layout.path(ws, "profile.json")
        prof = read_json(p); prof["schema"] = 1
        write_json(p, prof)
        rc, out = run(MIGRATE, ws)
        self.assertEqual(rc, 1)
        self.assertIn("migrate_1to2.py", out)
        self.assertEqual(schema_of(ws), 1)          # untouched

    def test_a_folder_with_no_findata_is_refused(self):
        rc, out = run(MIGRATE, tempfile.mkdtemp())
        self.assertEqual(rc, 2)

    def test_a_workspace_ahead_of_the_tool_is_left_alone(self):
        ws = workspace_from(FIXTURES[-1])
        p = layout.path(ws, "profile.json")
        prof = read_json(p); prof["schema"] = tool_schema() + 5
        write_json(p, prof)
        before = digest(os.path.join(ws, "findata"))
        rc, out = run(MIGRATE, ws)
        self.assertEqual(rc, 0); self.assertIn("Nothing to do", out)
        self.assertEqual(digest(os.path.join(ws, "findata")), before)


if __name__ == "__main__":
    unittest.main()
