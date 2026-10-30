"""Exercise package, research-routing and connection boundaries in disposable copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ConnectionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "package"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.plugin = self.root / "plugins/quandora"
        self.policy = self.plugin / "references/connection-and-security.md"
        self.skill = self.plugin / "skills/portfolio-trading-analysis/SKILL.md"

    def check(self):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/check-production-plugin.py")],
            text=True, capture_output=True,
        )
        return result.returncode, result.stdout + result.stderr

    def append(self, path, text):
        path.write_text(path.read_text() + "\n" + text + "\n")

    def rejected(self, expected):
        code, output = self.check()
        self.assertNotEqual(code, 0)
        self.assertIn(expected, output)

    def test_shipped_package(self):
        code, output = self.check()
        self.assertEqual(code, 0, output)

    def test_old_bundle_fallback_is_not_taught_in_references(self):
        self.append(self.policy, "Use `read_strategy_result_bundle_chunk` after HTTP fails.")
        self.rejected("unified Result Bundle export tool")

    def test_account_and_seven_research_and_trading_entry_points(self):
        self.assertEqual(
            {p.parent.name for p in (self.plugin / "skills").glob("*/SKILL.md")},
            {"account-connection", "factor-mining", "factor-analysis", "strategy-building", "strategy-analysis",
             "portfolio-building", "portfolio-analysis", "portfolio-trading-analysis"},
        )

    def test_account_skill_cannot_require_authentication_to_load(self):
        self.append(
            self.plugin / "skills/account-connection/agents/openai.yaml",
            'dependencies:\n  tools:\n    - type: "mcp"\n      value: "quandora"',
        )
        self.rejected("account-connection must load before MCP authentication")

    def test_problem_report_keeps_consent_and_secret_boundaries(self):
        skill = self.plugin / "skills/account-connection/SKILL.md"
        original = skill.read_text()
        for boundary in ("Never file a report on your own", "Never include credentials",
                         "never guess one", "do not retry in a loop"):
            with self.subTest(boundary=boundary):
                skill.write_text(original.replace(boundary, "Removed report boundary"))
                self.rejected("account-connection/SKILL.md: missing routing boundary")
                skill.write_text(original)

    def test_problem_report_tool_has_one_owner(self):
        skill = self.plugin / "skills/account-connection/SKILL.md"
        skill.write_text(skill.read_text().replace("`submit_feedback_report`", "the report tool"))
        self.rejected("missing primary tool ownership for submit_feedback_report")

    def test_missing_portfolio_analysis(self):
        (self.plugin / "skills/portfolio-analysis/SKILL.md").unlink()
        self.rejected("missing required production Skills")

    def test_retired_handoff_in_supporting_reference(self):
        self.append(self.plugin / "references/research-workflows.md", "Use $strategy-portfolio.")
        self.rejected("retired Skill entry")

    def test_unknown_handoff(self):
        self.append(self.skill, "Use $portfolio-optimizer for the next step.")
        self.rejected("unknown Skill handoff")

    def test_missing_shared_research_contract(self):
        (self.plugin / "references/research-workflows.md").unlink()
        self.rejected("missing shared research intent/evidence contract")

    def test_each_research_skill_routes_to_research_contract(self):
        for skill in (self.plugin / "skills").glob("*/SKILL.md"):
            if skill.parent.name == "account-connection":
                continue
            with self.subTest(skill=skill.parent.name):
                original = skill.read_text()
                skill.write_text(original.replace("../../references/research-workflows.md", "../../README.md"))
                self.rejected("missing shared research intent/evidence link")
                skill.write_text(original)

    def test_broken_link_in_nested_research_reference(self):
        self.append(
            self.plugin / "skills/portfolio-building/references/selection-and-weighting.md",
            "[Logic card](../../portfolio-analysis/references/missing-card.md)",
        )
        self.rejected("broken supporting reference")

    def test_lost_research_and_forward_boundaries(self):
        cases = (
            ("references/research-workflows.md", "For design-only requests, stop at the proposed definition"),
            ("references/portfolio-neutrality.md", "Positive constant scaling does not change correlation"),
            ("skills/portfolio-building/references/selection-and-weighting.md", "one-component Portfolio remains valid"),
            ("skills/portfolio-analysis/SKILL.md", "This is read-only backtest diagnosis"),
            ("skills/portfolio-analysis/SKILL.md", "components[].strategy_run_id"),
            ("skills/portfolio-analysis/references/evidence-contract.md", "Without a supported same-window projection"),
            ("skills/portfolio-trading-analysis/SKILL.md", "For analysis-only requests, remain read-only"),
            ("skills/portfolio-trading-analysis/references/forward-test-analysis.md", "Do not\nsum legacy member snapshots"),
            ("skills/portfolio-trading-analysis/references/forward-test-analysis.md", "bounded recent records, not a full\nhistorical export"),
        )
        for relative, boundary in cases:
            with self.subTest(boundary=boundary):
                path = self.plugin / relative
                original = path.read_text()
                self.assertIn(boundary, original)
                path.write_text(original.replace(boundary, "Removed boundary"))
                self.rejected("missing research boundary")
                path.write_text(original)

    def test_live_write_in_forward_reference_is_rejected(self):
        self.append(self.plugin / "skills/portfolio-trading-analysis/references/forward-test-analysis.md",
                    "Call `start_live_portfolio_run` after analyzing losses.")
        self.rejected("retired tool name remains")

    def test_retired_shared_factor_tools_are_rejected(self):
        for tool in ("list_shared_strategy_factor_candidates", "admit_shared_strategy_factor"):
            for relative in ("SKILL.md", "references/ordinary-strategy-workflow.md"):
                with self.subTest(tool=tool, file=relative):
                    path = self.plugin / "skills/strategy-building" / relative
                    original = path.read_text()
                    self.append(path, f"Call `{tool}` to select a shared Factor.")
                    self.rejected(f"retired tool name remains: {tool}")
                    path.write_text(original)

    def test_required_management_tools_stay_with_their_owner(self):
        cases = (
            ("portfolio-building", "share_portfolio_with_user"),
            ("portfolio-trading-analysis", "pause_portfolio_trading_run"),
            ("portfolio-trading-analysis", "rename_simulation_account"),
            ("portfolio-analysis", "get_portfolio_backtest_result"),
        )
        for name, tool in cases:
            with self.subTest(owner=name, tool=tool):
                path = self.plugin / f"skills/{name}/SKILL.md"
                original = path.read_text()
                path.write_text(original.replace(f"`{tool}`", "unrouted operation"))
                self.rejected(f"missing primary tool ownership for {tool}")
                path.write_text(original)

    def test_metadata_exposes_portfolio_analysis(self):
        path = self.plugin / ".codex-plugin/plugin.json"
        path.write_text(path.read_text().replace("Portfolio Analysis", "Portfolio Review"))
        self.rejected("metadata omits Portfolio Analysis")

    def test_missing_shared_policy(self):
        self.policy.unlink()
        self.rejected("missing shared connection recovery policy")

    def test_codex_recovery_guide_is_bundled_and_routed(self):
        guide = self.plugin / "references/codex-authorization-recovery.md"
        self.assertTrue(guide.is_file())
        original = self.policy.read_text()
        self.policy.write_text(original.replace(
            "](codex-authorization-recovery.md)", "](plugin-update.md)"))
        self.rejected("missing Codex authorization recovery link")
        self.policy.write_text(original)
        guide.unlink()
        self.rejected("missing bundled Codex authorization recovery guide")

    def test_codex_recovery_preserves_capability_and_consent_boundaries(self):
        guide = self.plugin / "references/codex-authorization-recovery.md"
        cases = (
            "`plugin_not_found`",
            "same desktop host and configuration context",
            "Do not assume a global `codex` executable shares the desktop configuration",
            "codex mcp get quandora --json",
            "https://mcp.quandora.ai/quant",
            "codex mcp login quandora",
            "one foreground native OAuth flow",
            "Do not ask the user to paste a recovery prompt or run the command",
            "Respect a security denial; never try another execution path to bypass it",
            "Only the user approves additional access",
            "Do not repeat login when the callback succeeds but the grant remains unchanged",
            "Do not use a fixed tool count",
            "Do not create a Portfolio or submit a backtest as a recovery probe",
        )
        original = guide.read_text()
        for boundary in cases:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, original)
                guide.write_text(original.replace(boundary, "Removed recovery boundary"))
                self.rejected("Codex authorization recovery: missing boundary")
                guide.write_text(original)

    def test_each_skill_routes_to_shared_policy(self):
        for skill in (self.plugin / "skills").glob("*/SKILL.md"):
            with self.subTest(skill=skill.parent.name):
                original = skill.read_text()
                skill.write_text(original.replace("../../references/connection-and-security.md", "../../README.md"))
                self.rejected("missing shared connection recovery policy link")
                skill.write_text(original)

    def test_reinstall_first_in_readme(self):
        self.append(self.root / "README.md", "If tools are missing, update or reinstall the plugin.")
        self.rejected("premature reinstall guidance")

    def test_token_lifetime_in_supporting_reference(self):
        self.append(self.policy, "A Quandora MCP access token is valid for 7 days.")
        self.rejected("user-facing token lifetime boilerplate")

    def test_refresh_prompt(self):
        self.append(self.skill, "Refresh the Quandora MCP connection.")
        self.rejected("user-facing refresh prompt")

    def test_hardcoded_version(self):
        self.append(self.skill, "Pass `2.5` as `installed_version`.")
        self.rejected("hardcoded release label")

    def test_mandatory_probe_in_shared_policy(self):
        self.append(self.policy, "Before every business call run `check_quandora_plugin_version`.")
        self.rejected("repeated blocking version probe")

    def test_update_guide_ships_inside_plugin(self):
        (self.plugin / "references/plugin-update.md").unlink()
        self.rejected("missing bundled plugin update guide")

    def test_marketplace_refresh_cannot_be_skipped(self):
        guide = self.plugin / "references/plugin-update.md"
        guide.write_text(guide.read_text().replace("codex plugin marketplace upgrade quandora", "skip refresh"))
        self.rejected("host-managed refresh/update command")

    def test_unsafe_mutation_recovery(self):
        self.policy.write_text(self.policy.read_text().replace("original idempotency key", "new idempotency key"))
        self.rejected("missing recovery boundary")

    def test_manifest_skew(self):
        path = self.plugin / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text()); data["version"] = "wrong-release"
        path.write_text(json.dumps(data))
        self.rejected("version")

    def test_future_version_needs_no_instruction_change(self):
        paths = [self.root / "kimi.plugin.json", *self.root.glob(".*-plugin/marketplace.json"),
                 *self.plugin.glob(".*-plugin/plugin.json")]
        for path in paths:
            data = json.loads(path.read_text())
            if "version" in data:
                data["version"] = "future-release+canary"
            for plugin in data.get("plugins", []):
                if "version" in plugin:
                    plugin["version"] = "future-release+canary"
            path.write_text(json.dumps(data))
        code, output = self.check()
        self.assertEqual(code, 0, output)



    def test_staging_endpoint_is_rejected(self):
        path = self.plugin / ".mcp.json"
        path.write_text(path.read_text().replace("mcp.quandora.ai", "mcp-staging.varsity.lol"))
        self.rejected("production MCP endpoint mismatch")

    def test_staging_identity_is_rejected(self):
        self.append(self.policy, "Use quandora-staging instead.")
        self.rejected("staging identity leaked")

    def test_stale_installer_hash_is_rejected(self):
        self.append(self.plugin / "scripts/workbuddy-cn-install-macos.js", "// changed component")
        self.rejected("WorkBuddy component integrity mismatch")

    def test_stale_bootstrap_guide_hash_is_rejected(self):
        self.append(self.plugin / "scripts/workbuddy-cn-bootstrap-macos.sh", "# changed bootstrap")
        self.rejected("WorkBuddy bootstrap guide integrity mismatch")


if __name__ == "__main__":
    unittest.main()
