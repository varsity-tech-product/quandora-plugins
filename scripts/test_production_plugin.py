"""Regression checks against disposable copies of the shipped plugin package."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("plugin_check", ROOT / "scripts/check-production-plugin.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class RuntimePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("plugins", ".claude-plugin", ".codebuddy-plugin"):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copy2(ROOT / "kimi.plugin.json", self.root / "kimi.plugin.json")
        self.plugin = self.root / "plugins/quandora"
        self.skill = self.plugin / "skills/paper-trading/SKILL.md"

    def run_check(self):
        replacements = dict(
            ROOT=self.root, PLUGIN=self.plugin, SKILLS=self.plugin / "skills",
            DIRECT_MANIFESTS=tuple(self.root / p.relative_to(ROOT) for p in check.DIRECT_MANIFESTS),
            MARKETPLACES=tuple(self.root / p.relative_to(ROOT) for p in check.MARKETPLACES),
        )
        output = io.StringIO()
        with patch.multiple(check, **replacements), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = check.main()
        return status, output.getvalue()

    def test_shipped_package_passes(self):
        self.assertEqual(self.run_check()[0], 0)

    def test_stale_paper_version_is_rejected(self):
        with self.skill.open("a") as f:
            f.write("\nPass `3.0-preview` verbatim as `installed_version`.\n")
        self.assertNotEqual(self.run_check()[0], 0)

    def test_token_refresh_boilerplate_is_rejected(self):
        with self.skill.open("a") as f:
            f.write("\nA Quandora MCP access token is valid for 7 days.\n")
        self.assertNotEqual(self.run_check()[0], 0)

    def test_missing_shared_policy_is_rejected(self):
        (self.plugin / "references/connection-and-version.md").unlink()
        self.assertNotEqual(self.run_check()[0], 0)

    def test_hardcoded_version_in_shared_policy_is_rejected(self):
        with (self.plugin / "references/connection-and-version.md").open("a") as f:
            f.write("\nUse `3.0-preview`.\n")
        self.assertNotEqual(self.run_check()[0], 0)

    def test_manifest_skew_is_rejected(self):
        p = self.plugin / ".claude-plugin/plugin.json"
        d = json.loads(p.read_text()); d["version"] = "wrong-release"
        p.write_text(json.dumps(d))
        self.assertNotEqual(self.run_check()[0], 0)

    def test_next_release_needs_no_skill_or_checker_version_edit(self):
        for original in (*check.DIRECT_MANIFESTS, *check.MARKETPLACES):
            p = self.root / original.relative_to(ROOT)
            d = json.loads(p.read_text()); d["version"] = "future-release+canary"
            for plugin in d.get("plugins", []):
                if plugin.get("name") == "quandora":
                    plugin["version"] = d["version"]
            p.write_text(json.dumps(d))
        self.assertEqual(self.run_check()[0], 0)

    def test_missing_installed_manifest_is_rejected(self):
        (self.plugin / ".codex-plugin/plugin.json").unlink()
        self.assertNotEqual(self.run_check()[0], 0)


if __name__ == "__main__":
    unittest.main()
