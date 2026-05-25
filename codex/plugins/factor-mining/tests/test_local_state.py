import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[2]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from factor_mining_agent_lib.config import AgentConfig, load_config, save_config
from factor_mining_agent_lib.metadata import MetadataError, parse_plugin_metadata
from factor_mining_agent_lib.redaction import redact_text
from factor_mining_agent_lib.run_state import RunState, load_run_state, save_run_state


class LocalStateTests(unittest.TestCase):
    def test_gitignore_ignores_macos_ds_store_files(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(".DS_Store", gitignore.splitlines())

    def test_docs_describe_agent_driven_acceptance_flow(self):
        root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        skill = (PLUGIN_ROOT / "skills" / "factor-mining" / "SKILL.md").read_text(encoding="utf-8")
        combined = root_readme + "\n" + readme + "\n" + skill

        self.assertIn("python3 scripts/factor_setup.py", readme)
        self.assertNotIn("factor_setup.py --base-url <factor-mining-api-url>", combined)
        self.assertIn("https://d25q1jf66e8y4g.cloudfront.net", readme)
        self.assertIn("--wait", readme)
        self.assertIn("--wait", skill)
        self.assertIn("task_payload", skill)
        self.assertIn("allowed_data", skill)
        self.assertIn("Codex runs", skill)
        self.assertIn("The user does not need to run the command sequence manually.", skill)
        self.assertIn("fwd_period=7", combined)
        banned_terms = (
            "M" + "VP",
            "private " + "repo",
            "Development " + "Validation",
            "local" + "host",
            "/Users/" + "richsion",
        )
        for banned in banned_terms:
            self.assertNotIn(banned, combined)

    def test_config_is_saved_outside_repo_with_restrictive_permissions(self):
        secret = "vt_test_secret_1234567890abcdef"
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            config = AgentConfig(
                base_url="https://factor.example",
                api_key=secret,
                agent_status={"ok": True, "key_purpose": "external_agent"},
            )

            path = save_config(config, home=home)

            self.assertEqual(path, home / "config.json")
            mode = stat.S_IMODE(path.stat().st_mode)
            self.assertEqual(mode, 0o600)
            loaded = load_config(home=home)
            self.assertEqual(loaded.base_url, "https://factor.example")
            self.assertEqual(loaded.api_key, secret)

    def test_redaction_removes_known_and_factor_mining_key_values(self):
        secret = "vt_test_secret_1234567890abcdef"
        text = f"Authorization: Bearer {secret}\napi_key={secret}\n"

        redacted = redact_text(text, extra_secrets=[secret])

        self.assertNotIn(secret, redacted)
        self.assertIn("vt_...cdef", redacted)
        self.assertEqual(redacted.count("vt_...cdef"), 2)

    def test_plugin_metadata_parser_uses_ast_without_executing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "plugin.py"
            side_effect_path = Path(tmp) / "executed.txt"
            plugin_path.write_text(
                "\n".join(
                    [
                        'FACTOR_TYPE = "alpha"',
                        'FACTOR_NAME = "Liquidity Stress"',
                        'FACTOR_DEFAULT_PARAMS = {"lookback": 48, "winsorize": True}',
                        f'__import__("pathlib").Path({str(side_effect_path)!r}).write_text("executed")',
                    ]
                ),
                encoding="utf-8",
            )

            metadata = parse_plugin_metadata(plugin_path)

            self.assertEqual(metadata.factor_type, "alpha")
            self.assertEqual(metadata.factor_name, "Liquidity Stress")
            self.assertEqual(metadata.params, {"lookback": 48, "winsorize": True})
            self.assertFalse(side_effect_path.exists())

    def test_plugin_metadata_parser_rejects_dynamic_assignments(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "plugin.py"
            plugin_path.write_text(
                "\n".join(
                    [
                        'FACTOR_TYPE = "alpha"',
                        "FACTOR_NAME = build_name()",
                        "FACTOR_DEFAULT_PARAMS = {}",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(MetadataError, "FACTOR_NAME"):
                parse_plugin_metadata(plugin_path)

    def test_run_state_round_trips_without_plugin_source_or_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            state = RunState(
                client_run_id="run_123",
                session_id="session_123",
                plugin_id="plugin_123",
                job_ids=["job_a", "job_b"],
                plugin_path="/workspace/plugin.py",
                workflow_stage="running",
                artifact_paths={"default_factor_card.json": "/tmp/card.json"},
            )

            path = save_run_state(state, home=home)
            loaded = load_run_state("run_123", home=home)

            self.assertEqual(path, home / "runs" / "run_123.json")
            self.assertEqual(loaded, state)
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("api_key", raw)
            self.assertNotIn("plugin_source", raw)
            self.assertNotIn("FACTOR_NAME", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
