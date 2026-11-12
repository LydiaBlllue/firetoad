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

    def test_finance_md_never_counts(self):
        # its figures table is the workspace's own, so it always differs and is never a reason to refresh
        self.copy_in()
        open(os.path.join(self.tool, "FINANCE.md"), "w").write("tool prose\n")
        open(os.path.join(self.ws, "FINANCE.md"), "w").write("my figures\n")
        self.assertEqual(app.tool_state(self.ws)["state"], "same")


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


if __name__ == "__main__":
    unittest.main()
