"""app.py — the launcher's rules that do not need a window: how a folder's copy of the tool
compares with the app's (same / differs / migrate / newer), where the folder is remembered, and
that the script mode only ever runs an existing .py file.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401
sys.path.insert(0, _paths.ROOT)
sys.path.insert(0, os.path.join(_paths.ROOT, "tools"))
import app  # noqa: E402
import sync  # noqa: E402


def mini_tool(d, schema=18):
    """The smallest folder tool_state can read: a rebuild.py with a SCHEMA and one synced file."""
    os.makedirs(os.path.join(d, ".claude", "skills", "update-dashboard", "scripts"))
    open(os.path.join(d, ".claude", "skills", "update-dashboard", "scripts", "rebuild.py"), "w").write(f"SCHEMA = {schema}\n")
    open(os.path.join(d, "CLAUDE.md"), "w").write("tool\n")
    os.makedirs(os.path.join(d, "templates", "dashboards"))
    open(os.path.join(d, "templates", "dashboards", "finance_dashboard.html"), "w").write('const VERSION = "9.9.9";\n')


def mini_ws(d, schema=18):
    os.makedirs(os.path.join(d, "findata", "register"))
    json.dump({"schema": schema, "demo": True}, open(os.path.join(d, "findata", "register", "profile.json"), "w"))
    os.makedirs(os.path.join(d, "dashboards"))


class ToolState(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="jt_app_")
        self.tool = os.path.join(self.base, "tool"); mini_tool(self.tool)
        self.ws = os.path.join(self.base, "ws"); mini_ws(self.ws)
        self._tool, self._sync_tool = app.TOOL, sync.TOOL
        app.TOOL = sync.TOOL = self.tool

    def tearDown(self):
        app.TOOL, sync.TOOL = self._tool, self._sync_tool
        shutil.rmtree(self.base, ignore_errors=True)

    def copy_in(self):
        for rel in (".claude/skills", "CLAUDE.md", "templates/dashboards"):
            s, d = os.path.join(self.tool, rel), os.path.join(self.ws, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy(s, d)

    def test_a_folder_with_the_tools_copy_is_same(self):
        self.copy_in()
        st = app.tool_state(self.ws)
        self.assertEqual(st["state"], "same")
        self.assertEqual(st["changed"], [])
        self.assertEqual(st["version"], "9.9.9")

    def test_a_renamed_tool_file_leaves_no_old_copy(self):
        # RELEASE-ROADMAP.md was ROADMAP.md: a folder synced before the rename still holds the
        # old file, and a stale plan left behind reads as the current one (2026-11-13).
        self.copy_in()
        open(os.path.join(self.tool, "RELEASE-ROADMAP.md"), "w").write("what is released next\n")
        open(os.path.join(self.ws, "RELEASE-ROADMAP.md"), "w").write("what is released next\n")
        open(os.path.join(self.ws, "ROADMAP.md"), "w").write("the old plan\n")
        self.assertIn("ROADMAP.md", sync.pending(self.ws))
        # while the tool itself still has a file of the old name, nothing is taken away
        open(os.path.join(self.tool, "ROADMAP.md"), "w").write("still shipped\n")
        self.assertNotIn("ROADMAP.md", sync.pending(self.ws))

    def test_one_file_apart_is_differs_and_named(self):
        self.copy_in()
        open(os.path.join(self.ws, "CLAUDE.md"), "a").write("edited\n")
        st = app.tool_state(self.ws)
        self.assertEqual(st["state"], "differs")
        self.assertEqual(st["changed"], ["CLAUDE.md"])

    def test_a_newer_folder_is_newer_whatever_the_files_say(self):
        self.copy_in()
        json.dump({"schema": 19}, open(os.path.join(self.ws, "findata", "register", "profile.json"), "w"))
        self.assertEqual(app.tool_state(self.ws)["state"], "newer")

    def test_an_older_folder_has_to_migrate_first(self):
        self.copy_in()
        json.dump({"schema": 17}, open(os.path.join(self.ws, "findata", "register", "profile.json"), "w"))
        self.assertEqual(app.tool_state(self.ws)["state"], "migrate")

    def test_finance_md_counts_for_its_prose_never_for_its_figures(self):
        # the figures table is the workspace's own; the prose around it is the tool's
        self.copy_in()
        fig = "<!-- LINT:FIGURES -->\n| net | {} |\n<!-- LINT:FIGURES:END -->\n"
        open(os.path.join(self.tool, "FINANCE.md"), "w").write("tool prose\n" + fig.format(1))
        open(os.path.join(self.ws, "FINANCE.md"), "w").write("tool prose\n" + fig.format(999))
        self.assertEqual(app.tool_state(self.ws)["state"], "same")
        open(os.path.join(self.ws, "FINANCE.md"), "w").write("older prose\n" + fig.format(999))
        self.assertEqual(app.tool_state(self.ws)["changed"], ["FINANCE.md"])

    def test_the_setups_lines_in_gitignore_are_the_owners(self):
        # setup adds a block that keeps the owner's data out of a remote: not a difference, and a
        # sync keeps it (it used to copy the tool's file over it)
        self.copy_in()
        open(os.path.join(self.tool, ".gitignore"), "w").write(".DS_Store\n# findata/\n")
        open(os.path.join(self.ws, ".gitignore"), "w").write(
            ".DS_Store\n\n" + sync.OWN_LINES + " (setup, 2026-11-12): never in a remote.\nfindata/\n")
        self.assertEqual(app.tool_state(self.ws)["state"], "same")
        open(os.path.join(self.tool, ".gitignore"), "w").write(".DS_Store\n*.tmp\n# findata/\n")
        self.assertEqual(app.tool_state(self.ws)["changed"], [".gitignore"])
        new = sync.seam_text(".gitignore", os.path.join(self.tool, ".gitignore"), os.path.join(self.ws, ".gitignore"))
        self.assertIn("*.tmp\n", new)
        self.assertTrue(new.endswith("findata/\n"))
        self.assertNotIn("# findata/", new)


class Remembering(unittest.TestCase):
    def test_the_settings_live_outside_any_workspace(self):
        p = app.settings_path()
        self.assertTrue(p.endswith(os.path.join(app.APP_NAME, "settings.json")))
        self.assertNotIn("findata", p)

    def test_settings_under_the_old_name_come_along(self):
        # renamed from Jade Toad (2026-11-12): the folder an owner chose has to keep opening
        home = tempfile.mkdtemp(prefix="jt_home_")
        try:
            env = {"HOME": home, "XDG_CONFIG_HOME": os.path.join(home, ".config"), "APPDATA": os.path.join(home, "AppData")}
            with mock.patch.dict(os.environ, env):
                old = os.path.join(os.path.dirname(app.support_dir()), app.LEGACY_NAMES[0])
                os.makedirs(old)
                json.dump({"workspace": "/somewhere/mine"}, open(os.path.join(old, "settings.json"), "w"))
                p = app.settings_path()
                self.assertTrue(p.endswith(os.path.join(app.APP_NAME, "settings.json")))
                self.assertEqual(json.load(open(p))["workspace"], "/somewhere/mine")
                self.assertTrue(os.path.exists(os.path.join(old, "settings.json")))   # the old one stays
        finally:
            shutil.rmtree(home)

    def test_is_workspace_needs_both_folders(self):
        d = tempfile.mkdtemp(prefix="jt_ws_")
        try:
            self.assertFalse(app.is_workspace(d))
            os.makedirs(os.path.join(d, "findata"))
            self.assertFalse(app.is_workspace(d))
            os.makedirs(os.path.join(d, "dashboards"))
            self.assertTrue(app.is_workspace(d))
        finally:
            shutil.rmtree(d)


class CreateMyFolder(unittest.TestCase):
    """*Create my folder* picks no folder from the owner, so it can never pick a wrong one."""
    def setUp(self):
        self.docs = tempfile.mkdtemp(prefix="jt_docs_")

    def tearDown(self):
        shutil.rmtree(self.docs)

    def test_it_is_documents_fire_toad(self):
        self.assertEqual(app.new_folder(self.docs), os.path.join(self.docs, app.APP_NAME))

    def test_an_empty_folder_of_that_name_is_used(self):
        os.makedirs(os.path.join(self.docs, app.APP_NAME))
        self.assertEqual(app.new_folder(self.docs), os.path.join(self.docs, app.APP_NAME))

    def test_an_existing_fire_toad_folder_is_used(self):
        mini_ws(os.path.join(self.docs, app.APP_NAME))
        self.assertEqual(app.new_folder(self.docs), os.path.join(self.docs, app.APP_NAME))

    def test_someone_elses_folder_of_that_name_is_left_alone(self):
        os.makedirs(os.path.join(self.docs, app.APP_NAME))
        open(os.path.join(self.docs, app.APP_NAME, "notes.txt"), "w").write("mine\n")
        open(os.path.join(self.docs, app.APP_NAME + " 2"), "w").write("a file, not a folder\n")
        self.assertEqual(app.new_folder(self.docs), os.path.join(self.docs, app.APP_NAME + " 3"))

    def test_a_full_folder_gets_a_fire_toad_folder_inside_not_an_error(self):
        open(os.path.join(self.docs, "notes.txt"), "w").write("mine\n")
        with mock.patch.object(sync, "main", lambda argv: 0):
            made = app.make_workspace(self.docs)
        self.assertEqual(made, os.path.join(self.docs, app.APP_NAME))
        self.assertTrue(os.path.exists(os.path.join(made, "findata", "register", "profile.json")))
        self.assertEqual(sorted(os.listdir(self.docs)), [app.APP_NAME, "notes.txt"])


class InstallFromDiskImage(unittest.TestCase):
    """Double-clicked in the disk image, the app copies itself into Applications; anywhere else it
    does nothing."""
    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="jt_inst_")
        self.vols = os.path.join(self.base, "Volumes")
        self.src = os.path.join(self.vols, app.APP_NAME, app.APP_NAME + ".app")
        os.makedirs(os.path.join(self.src, "Contents", "MacOS"))
        open(os.path.join(self.src, "Contents", "MacOS", app.APP_NAME), "w").write("new\n")
        self.apps = os.path.join(self.base, "Applications")

    def tearDown(self):
        shutil.rmtree(self.base)

    def run_from(self, where):
        return app.install_from_disk_image(app=where, apps_dir=self.apps, volumes=self.vols)

    def exe(self, bundle):
        return open(os.path.join(bundle, "Contents", "MacOS", app.APP_NAME)).read()

    @unittest.skipUnless(sys.platform == "darwin", "ditto is macOS's")
    def test_from_the_disk_image_it_lands_in_applications(self):
        dest = self.run_from(self.src)
        self.assertEqual(dest, os.path.join(self.apps, app.APP_NAME + ".app"))
        self.assertEqual(self.exe(dest), "new\n")
        self.assertEqual(os.listdir(self.apps), [app.APP_NAME + ".app"])   # no .installing left

    @unittest.skipUnless(sys.platform == "darwin", "ditto is macOS's")
    def test_translocated_it_finds_the_original_on_the_disk(self):
        dest = self.run_from("/private/var/folders/xx/AppTranslocation/ABC/d/" + app.APP_NAME + ".app")
        self.assertEqual(self.exe(dest), "new\n")

    @unittest.skipUnless(sys.platform == "darwin", "ditto is macOS's")
    def test_an_older_version_is_replaced_not_kept_beside(self):
        old = os.path.join(self.apps, app.APP_NAME + ".app", "Contents", "MacOS")
        os.makedirs(old)
        open(os.path.join(old, app.APP_NAME), "w").write("old\n")
        open(os.path.join(old, "stale"), "w").write("x\n")
        dest = self.run_from(self.src)
        self.assertEqual(self.exe(dest), "new\n")
        self.assertFalse(os.path.exists(os.path.join(dest, "Contents", "MacOS", "stale")))

    def test_from_applications_it_does_nothing(self):
        self.assertIsNone(self.run_from("/Applications/" + app.APP_NAME + ".app"))
        self.assertFalse(os.path.exists(self.apps))

    def test_outside_a_packaged_app_it_does_nothing(self):
        self.assertIsNone(app.install_from_disk_image())   # tests run as python, not frozen

    def test_eject_never_touches_anything_outside_volumes(self):
        with mock.patch.object(app.subprocess, "Popen") as p:
            app.eject_later("/private/tmp/somewhere")
            app.eject_later(None)
        p.assert_not_called()


if __name__ == "__main__":
    unittest.main()
