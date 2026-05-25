#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .mock_backend import start_mock_backend
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mock_backend import start_mock_backend


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
FAKE_AGENT_KEY = "vt_mock_acceptance_key_1234567890"


class AcceptanceFailure(RuntimeError):
    pass


@dataclass
class ScenarioResult:
    name: str
    setup: dict[str, Any]
    tasks: dict[str, Any]
    session: dict[str, Any]
    dedup: dict[str, Any]
    metadata: dict[str, Any]
    upload_summary: dict[str, Any]
    artifact: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "setup": self.setup,
            "tasks": self.tasks,
            "session": self.session,
            "dedup": self.dedup,
            "metadata": self.metadata,
            "upload_summary": self.upload_summary,
            "artifact": self.artifact,
        }


def _write_plugin(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                'FACTOR_TYPE = "mock_liquidity_stress"',
                'FACTOR_NAME = "Mock Liquidity Stress"',
                'FACTOR_DEFAULT_PARAMS = {"lookback": 7}',
                "",
                "def build_signal(close, params, **data):",
                "    window = int(params.get('lookback', FACTOR_DEFAULT_PARAMS['lookback']))",
                "    return close.pct_change(window).reindex_like(close)",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_task_payload(path: Path) -> None:
    payload = {
        "task_id": "task_mock_liquidity_stress",
        "title": "Mock Liquidity Stress",
        "category": "acceptance",
        "description": "Exercise the local external-agent plugin flow.",
        "allowed_data": ["close", "volume"],
        "fwd_period": 7,
        "hints": ["Use a small static metadata surface for acceptance."],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_command(args: list[str], *, env: dict[str, str]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=str(PLUGIN_ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise AcceptanceFailure(
            "command failed: "
            + " ".join(args)
            + f"\nexit={completed.returncode}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AcceptanceFailure(
            "command did not return JSON: " + " ".join(args) + f"\nstdout={completed.stdout}"
        ) from exc
    if not isinstance(payload, dict):
        raise AcceptanceFailure("command returned non-object JSON: " + " ".join(args))
    return payload


def _run_scenario(name: str, backend_scenario: str) -> ScenarioResult:
    with start_mock_backend(scenario=backend_scenario) as backend:
        with tempfile.TemporaryDirectory(prefix="factor-mining-acceptance-") as tmp:
            root = Path(tmp)
            home = root / "home"
            work = root / "work"
            artifact_dir = root / "artifacts"
            work.mkdir()
            plugin_path = work / "plugin.py"
            task_payload_path = work / "task_payload.json"
            _write_plugin(plugin_path)
            _write_task_payload(task_payload_path)

            env = dict(os.environ)
            env["FACTOR_MINING_AGENT_API_KEY"] = FAKE_AGENT_KEY

            setup = _json_command(
                [
                    "scripts/factor_setup.py",
                    "--base-url",
                    backend.base_url,
                    "--home",
                    str(home),
                ],
                env=env,
            )
            tasks = _json_command(["scripts/factor_api.py", "tasks", "--home", str(home)], env=env)
            session = _json_command(
                [
                    "scripts/factor_api.py",
                    "create-session",
                    "--home",
                    str(home),
                    "--idea",
                    "Mock liquidity stress factor",
                    "--task-payload-file",
                    str(task_payload_path),
                    "--client-run-id",
                    f"{name}_session_run",
                ],
                env=env,
            )
            dedup = _json_command(
                [
                    "scripts/factor_api.py",
                    "dedup-context",
                    "--home",
                    str(home),
                    "--session-id",
                    session["session_id"],
                    "--description",
                    "Volume-confirmed liquidity stress.",
                    "--formula",
                    "close momentum adjusted by volume confirmation",
                ],
                env=env,
            )
            metadata = _json_command(
                ["scripts/factor_api.py", "metadata", "--plugin-path", str(plugin_path)],
                env=env,
            )
            upload_summary = _json_command(
                [
                    "scripts/factor_upload_backtest.py",
                    "--home",
                    str(home),
                    "--session-id",
                    session["session_id"],
                    "--plugin-path",
                    str(plugin_path),
                    "--client-run-id",
                    f"{name}_backtest_run",
                    "--position-mode",
                    "both",
                    "--fwd-period",
                    "7",
                    "--wait",
                    "--poll-interval",
                    "0",
                    "--timeout",
                    "5",
                    "--output-dir",
                    str(artifact_dir),
                ],
                env=env,
            )
            artifact = _json_command(
                [
                    "scripts/factor_api.py",
                    "artifact",
                    "--home",
                    str(home),
                    "--job-id",
                    upload_summary["job_ids"][0],
                    "--name",
                    "default_factor_card.json",
                ],
                env=env,
            )

    return ScenarioResult(
        name=name,
        setup=setup,
        tasks=tasks,
        session=session,
        dedup=dedup,
        metadata=metadata,
        upload_summary=upload_summary,
        artifact=artifact,
    )


def _assert_success(result: ScenarioResult) -> None:
    agent_status = result.setup.get("agent_status", {})
    if agent_status.get("status") != "ok" or agent_status.get("agent_key") != "valid":
        raise AcceptanceFailure("setup did not verify an external-agent key")
    if result.session.get("session_id") != "session_mock_1":
        raise AcceptanceFailure("session creation did not return the mock session")
    if result.metadata.get("factor_name") != "Mock Liquidity Stress":
        raise AcceptanceFailure("metadata parse did not inspect the mock plugin")
    if result.upload_summary.get("ok") is not True or result.upload_summary.get("status") != "succeeded":
        raise AcceptanceFailure("success scenario did not finish with ok=true and status=succeeded")
    if result.upload_summary.get("artifact", {}).get("status") != "available":
        raise AcceptanceFailure("success scenario did not retrieve the default factor card")


def _assert_failed_job(result: ScenarioResult) -> None:
    if result.upload_summary.get("ok") is not False or result.upload_summary.get("status") != "failed":
        raise AcceptanceFailure("failed-job scenario did not return a terminal failure summary")


def run_success_scenario() -> ScenarioResult:
    result = _run_scenario("success", "success")
    _assert_success(result)
    return result


def run_failed_job_scenario() -> ScenarioResult:
    result = _run_scenario("failed_job", "failed_job")
    _assert_failed_job(result)
    return result


def run_all_scenarios() -> dict[str, ScenarioResult]:
    return {
        "success": run_success_scenario(),
        "failed_job": run_failed_job_scenario(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Factor Mining mock backend acceptance scenarios.")
    parser.add_argument(
        "--scenario",
        choices=("all", "success", "failed-job"),
        default="all",
        help="Acceptance scenario to run.",
    )
    args = parser.parse_args(argv)

    try:
        if args.scenario == "success":
            results = {"success": run_success_scenario()}
        elif args.scenario == "failed-job":
            results = {"failed_job": run_failed_job_scenario()}
        else:
            results = run_all_scenarios()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":"), sort_keys=True))
        return 1

    summary = {
        "ok": True,
        "scenarios": {
            name: {
                "ok": result.upload_summary.get("ok"),
                "status": result.upload_summary.get("status"),
                "terminal_status": result.upload_summary.get("terminal_status"),
                "artifact_status": result.upload_summary.get("artifact", {}).get("status"),
            }
            for name, result in results.items()
        },
    }
    print(json.dumps(summary, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
