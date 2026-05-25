from __future__ import annotations

import json
import re
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterator
from urllib.parse import parse_qs, unquote, urlparse


MOCK_SESSION_ID = "session_mock_1"
MOCK_PLUGIN_ID = "plugin_mock_1"
MOCK_JOB_ID = "job_mock_1"


@dataclass
class MockBackendState:
    scenario: str = "success"
    request_log: list[dict[str, Any]] = field(default_factory=list)
    sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    plugins: dict[str, dict[str, Any]] = field(default_factory=dict)
    jobs: dict[str, dict[str, Any]] = field(default_factory=dict)

    def record(self, method: str, path: str, body: Any = None) -> None:
        self.request_log.append({"method": method, "path": path, "body": body})

    def job_status(self) -> str:
        if self.scenario == "failed_job":
            return "failed"
        return "succeeded"


@dataclass
class RunningMockBackend:
    server: ThreadingHTTPServer
    thread: threading.Thread
    state: MockBackendState

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class _ThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _handler_for(state: MockBackendState) -> type[BaseHTTPRequestHandler]:
    class MockBackendHandler(BaseHTTPRequestHandler):
        server_version = "FactorMiningMock/1"

        def log_message(self, format: str, *args: Any) -> None:
            return None

        def _send_json(self, status: int, payload: Any) -> None:
            data = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or "0")
            if length == 0:
                return {}
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))

        def _read_bytes(self) -> bytes:
            length = int(self.headers.get("Content-Length") or "0")
            if length == 0:
                return b""
            return self.rfile.read(length)

        def _require_auth(self) -> bool:
            auth = self.headers.get("Authorization") or ""
            if not auth.startswith("Bearer vt_"):
                self._send_json(401, {"detail": "A delegated Agent API Key is required."})
                return False
            return True

        def _require_agent_status_auth(self) -> bool:
            auth = self.headers.get("Authorization") or ""
            if not auth.startswith("Bearer "):
                self._send_json(401, {"detail": "A delegated Agent API Key is required."})
                return False
            if not auth.removeprefix("Bearer ").startswith("vt_") or state.scenario == "non_external_agent":
                self._send_json(403, {"detail": "The provided key is not an external-agent credential."})
                return False
            return True

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)
            state.record("GET", path, dict(query))

            if path == "/health":
                self._send_json(200, {"ok": True, "service": "factor-mining-mock"})
                return

            if path == "/agent/status":
                if not self._require_agent_status_auth():
                    return
                self._send_json(200, {"status": "ok", "agent_key": "valid"})
                return

            if not self._require_auth():
                return

            if path == "/tasks":
                self._send_json(
                    200,
                    {
                        "tasks": [
                            {
                                "task_id": "task_mock_liquidity_stress",
                                "title": "Mock Liquidity Stress",
                                "category": "acceptance",
                                "description": "Exercise the local external-agent flow.",
                                "allowed_data": ["close", "volume"],
                                "fwd_period": 7,
                                "status": "open",
                            }
                        ]
                    },
                )
                return

            workflow_match = re.fullmatch(r"/workflows/([^/]+)", path)
            if workflow_match:
                session_id = unquote(workflow_match.group(1))
                if session_id not in state.sessions:
                    self._send_json(404, {"detail": "session not found"})
                    return
                self._send_json(
                    200,
                    {
                        "stage": "done",
                        "status": "done",
                        "stage_label": "Backtest complete",
                        "next_action": "review_results",
                        "progress": 1.0,
                    },
                )
                return

            job_match = re.fullmatch(r"/jobs/([^/]+)", path)
            if job_match:
                job_id = unquote(job_match.group(1))
                job = state.jobs.get(job_id)
                if not job:
                    self._send_json(404, {"detail": "job not found"})
                    return
                self._send_json(200, job)
                return

            artifact_match = re.fullmatch(r"/jobs/([^/]+)/files/default_factor_card\.json", path)
            if artifact_match:
                job_id = unquote(artifact_match.group(1))
                if job_id not in state.jobs:
                    self._send_json(404, {"detail": "job not found"})
                    return
                self._send_json(
                    200,
                    {
                        "factor_name": "Mock Liquidity Stress",
                        "metrics": {
                            "composite_sharpe": 1.23,
                            "composite_annual_ret": 0.18,
                            "composite_max_dd": -0.07,
                        },
                        "artifacts": {"default_factor_card.json": "available"},
                    },
                )
                return

            self._send_json(404, {"detail": "not found"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            if not self._require_auth():
                return

            if path == "/sessions":
                body = self._read_json()
                state.record("POST", path, body)
                if body.get("origin") == "custom" and not isinstance(body.get("task_payload"), dict):
                    self._send_json(400, {"detail": "custom sessions require task_payload"})
                    return
                state.sessions[MOCK_SESSION_ID] = body
                self._send_json(
                    200,
                    {
                        "session_id": MOCK_SESSION_ID,
                        "id": MOCK_SESSION_ID,
                        "origin": body.get("origin"),
                        "task_payload": body.get("task_payload"),
                    },
                )
                return

            if path == "/factors/dedup-context":
                body = self._read_json()
                state.record("POST", path, body)
                if body.get("session_id") not in state.sessions:
                    self._send_json(404, {"detail": "session not found"})
                    return
                self._send_json(
                    200,
                    {
                        "matches": [],
                        "duplicate_risk": "low",
                        "guidance": "No close local matches in the mock catalog.",
                    },
                )
                return

            upload_match = re.fullmatch(r"/sessions/([^/]+)/plugins/upload", path)
            if upload_match:
                session_id = unquote(upload_match.group(1))
                body = self._read_bytes()
                state.record("POST", path, {"bytes": len(body)})
                if session_id not in state.sessions:
                    self._send_json(404, {"detail": "session not found"})
                    return
                if b"Mock Liquidity Stress" not in body:
                    self._send_json(400, {"detail": "plugin metadata was not uploaded"})
                    return
                state.plugins[MOCK_PLUGIN_ID] = {"session_id": session_id}
                self._send_json(202, {"plugin_id": MOCK_PLUGIN_ID, "id": MOCK_PLUGIN_ID, "status": "uploaded"})
                return

            backtest_match = re.fullmatch(r"/sessions/([^/]+)/plugins/([^/]+)/backtest", path)
            if backtest_match:
                session_id = unquote(backtest_match.group(1))
                plugin_id = unquote(backtest_match.group(2))
                body = self._read_json()
                state.record("POST", path, body)
                if session_id not in state.sessions or plugin_id not in state.plugins:
                    self._send_json(404, {"detail": "session or plugin not found"})
                    return
                status = state.job_status()
                job = {
                    "job_id": MOCK_JOB_ID,
                    "id": MOCK_JOB_ID,
                    "status": status,
                    "position_mode": body.get("position_mode") or "both",
                    "factor_card_ready": True,
                    "factor_card_summary": {"composite_sharpe": 1.23, "cs_success": status == "succeeded"},
                }
                if status == "failed":
                    job["failure_reason"] = "mock terminal failure"
                state.jobs[MOCK_JOB_ID] = job
                self._send_json(202, {"job_ids": [MOCK_JOB_ID], "jobs": [job], "status": "queued"})
                return

            self._send_json(404, {"detail": "not found"})

    return MockBackendHandler


@contextmanager
def start_mock_backend(scenario: str = "success") -> Iterator[RunningMockBackend]:
    state = MockBackendState(scenario=scenario)
    server = _ThreadingHTTPServer(("127.0.0.1", 0), _handler_for(state))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    backend = RunningMockBackend(server=server, thread=thread, state=state)
    thread.start()
    try:
        yield backend
    finally:
        backend.stop()
