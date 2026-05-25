import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from factor_mining_agent_lib.api import ApiClient, ApiError, AgentStatusError, validate_agent_status
from factor_mining_agent_lib.metadata import PluginMetadata
from factor_mining_agent_lib.workflow import is_workflow_terminal, summarize_factor_card, terminal_outcome


class FakeResponse:
    def __init__(self, status=200, body=None, headers=None):
        self.status = status
        self.code = status
        self.headers = headers or {"Content-Type": "application/json"}
        if body is None:
            body = {}
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self._body = body

    def read(self):
        return self._body

    def close(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class ApiClientTests(unittest.TestCase):
    def test_agent_status_request_and_external_agent_validation(self):
        opener = FakeOpener(
            [
                FakeResponse(
                    body={
                        "ok": True,
                        "mode": "local_agent",
                        "key_purpose": "external_agent",
                        "capabilities": ["plugins:upload"],
                    }
                )
            ]
        )
        client = ApiClient("https://factor.example/api/", "vt_secret", opener=opener)

        status = client.agent_status()

        self.assertEqual(status["key_purpose"], "external_agent")
        request = opener.requests[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://factor.example/api/agent/status")
        self.assertEqual(request.get_header("Authorization"), "Bearer vt_secret")

    def test_non_external_agent_status_is_rejected(self):
        with self.assertRaisesRegex(AgentStatusError, "external_agent"):
            validate_agent_status({"ok": True, "key_purpose": "frontend_user", "mode": "web"})

    def test_missing_agent_status_endpoint_has_actionable_error(self):
        client = ApiClient(
            "https://factor.example",
            "vt_secret",
            opener=FakeOpener([FakeResponse(status=404, body={"detail": "not found"})]),
        )

        with self.assertRaisesRegex(AgentStatusError, "external-agent status endpoint"):
            client.agent_status()

    def test_tasks_session_and_dedup_requests_are_constructed(self):
        opener = FakeOpener(
            [
                FakeResponse(body={"tasks": []}),
                FakeResponse(body={"session_id": "session_1"}),
                FakeResponse(body={"matches": []}),
            ]
        )
        client = ApiClient("https://factor.example", "vt_secret", opener=opener)

        client.list_tasks(limit=5, status="open")
        client.create_session(idea="4h liquidity stress", client_run_id="run_1")
        client.dedup_context(
            session_id="session_1",
            description="liquidity stress",
            formula="volume / spread",
            limit=8,
        )

        self.assertEqual(opener.requests[0].full_url, "https://factor.example/tasks?limit=5&status=open")
        session_body = json.loads(opener.requests[1].data.decode("utf-8"))
        self.assertEqual(session_body, {"origin": "custom", "idea": "4h liquidity stress"})
        self.assertEqual(opener.requests[1].get_header("Idempotency-Key"), "run_1")
        dedup_body = json.loads(opener.requests[2].data.decode("utf-8"))
        self.assertEqual(dedup_body["session_id"], "session_1")
        self.assertEqual(dedup_body["limit"], 8)

    def test_create_session_can_send_direct_task_payload(self):
        task_payload = {
            "task_id": "custom_liquidity_stress",
            "title": "Liquidity Stress",
            "category": "custom",
            "description": "Identify fragile liquidity regimes.",
            "allowed_data": ["close", "volume"],
            "fwd_period": 7,
        }
        opener = FakeOpener([FakeResponse(body={"session_id": "session_1"})])
        client = ApiClient("https://factor.example", "vt_secret", opener=opener)

        client.create_session(idea="liquidity stress", task_payload=task_payload, client_run_id="run_1")

        session_body = json.loads(opener.requests[0].data.decode("utf-8"))
        self.assertEqual(session_body["origin"], "custom")
        self.assertEqual(session_body["idea"], "liquidity stress")
        self.assertEqual(session_body["task_payload"], task_payload)
        self.assertEqual(opener.requests[0].get_header("Idempotency-Key"), "run_1")

    def test_upload_backtest_poll_and_artifact_requests_are_constructed(self):
        opener = FakeOpener(
            [
                FakeResponse(body={"plugin_id": "plugin_1"}),
                FakeResponse(body={"job_ids": ["job_1"], "status": "queued"}),
                FakeResponse(body={"stage": "done"}),
                FakeResponse(body={"job_id": "job_1", "status": "succeeded"}),
                FakeResponse(body={"metrics": {"sharpe": 1.2}}),
            ]
        )
        client = ApiClient("https://factor.example", "vt_secret", opener=opener)
        metadata = PluginMetadata(
            factor_type="alpha",
            factor_name="Liquidity Stress",
            params={"lookback": 48},
        )

        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "plugin.py"
            plugin_path.write_text('FACTOR_NAME = "Liquidity Stress"\n', encoding="utf-8")
            client.upload_plugin(
                session_id="session_1",
                plugin_path=plugin_path,
                metadata=metadata,
                client_run_id="run_1",
                decision_summary="local agent draft",
                boundary="BOUNDARY",
            )
            client.submit_backtest("session_1", "plugin_1", position_mode="both", client_run_id="run_1")
            client.workflow("session_1")
            client.job("job_1")
            client.artifact("job_1", "default_factor_card.json")

        upload = opener.requests[0]
        self.assertEqual(upload.get_method(), "POST")
        self.assertEqual(upload.full_url, "https://factor.example/sessions/session_1/plugins/upload")
        self.assertEqual(upload.get_header("Idempotency-Key"), "run_1")
        self.assertIn("multipart/form-data; boundary=BOUNDARY", upload.get_header("Content-type"))
        body = upload.data.decode("utf-8")
        self.assertIn('name="factor_type"', body)
        self.assertIn("alpha", body)
        self.assertIn('name="client_run_id"', body)
        self.assertIn("run_1", body)
        self.assertIn('name="fwd_period"', body)
        self.assertIn("7", body)
        self.assertNotIn('name="submitter_label"', body)
        self.assertNotIn('name="agent_id"', body)
        backtest_body = json.loads(opener.requests[1].data.decode("utf-8"))
        self.assertEqual(backtest_body, {"position_mode": "both", "wfo_mode": False, "params_override": {}})
        self.assertEqual(opener.requests[2].full_url, "https://factor.example/workflows/session_1")
        self.assertEqual(opener.requests[3].full_url, "https://factor.example/jobs/job_1")
        self.assertEqual(
            opener.requests[4].full_url,
            "https://factor.example/jobs/job_1/files/default_factor_card.json",
        )

    def test_api_error_string_redacts_key_and_response_body(self):
        secret = "vt_test_secret_1234567890abcdef"
        error = HTTPError(
            "https://factor.example/agent/status",
            401,
            "unauthorized",
            {},
            FakeResponse(status=401, body={"detail": f"bad key {secret}"}),
        )
        client = ApiClient("https://factor.example", secret, opener=FakeOpener([error]))

        with self.assertRaises(ApiError) as raised:
            client.agent_status()

        rendered = str(raised.exception)
        self.assertNotIn(secret, rendered)
        self.assertIn("vt_...cdef", rendered)
        self.assertIn("401", rendered)

    def test_documented_http_status_handling(self):
        for status in (200, 202):
            with self.subTest(status=status):
                client = ApiClient(
                    "https://factor.example",
                    "vt_secret",
                    opener=FakeOpener([FakeResponse(status=status, body={"ok": True})]),
                )
                self.assertEqual(client.request("GET", "/health", auth=False), {"ok": True})

        for status in (400, 401, 403, 409, 410, 500):
            with self.subTest(status=status):
                client = ApiClient(
                    "https://factor.example",
                    "vt_secret",
                    opener=FakeOpener([FakeResponse(status=status, body={"detail": "failure"})]),
                )
                with self.assertRaises(ApiError) as raised:
                    client.request("GET", "/health", auth=False)
                self.assertEqual(raised.exception.status, status)

    def test_workflow_terminal_detection_and_factor_card_summary(self):
        self.assertTrue(is_workflow_terminal({"stage": "done"}, []))
        self.assertTrue(is_workflow_terminal({"stage": "failed"}, []))
        self.assertTrue(
            is_workflow_terminal(
                {"stage": "running"},
                [{"status": "succeeded"}, {"status": "failed"}],
            )
        )
        self.assertFalse(is_workflow_terminal({"stage": "running"}, [{"status": "queued"}]))
        self.assertEqual(terminal_outcome({"stage": "done"}, [{"status": "done"}])["status"], "succeeded")
        failed = terminal_outcome({"stage": "done"}, [{"job_id": "job_1", "status": "failed"}])
        self.assertFalse(failed["ok"])
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed["failures"][0]["job_id"], "job_1")

        summary = summarize_factor_card(
            {
                "factor_name": "Liquidity Stress",
                "metrics": {"sharpe": 1.4, "turnover": 0.22},
                "artifacts": {"plot": "available"},
            },
            jobs=[{"job_id": "job_1", "status": "succeeded"}],
        )

        self.assertEqual(summary["factor_name"], "Liquidity Stress")
        self.assertEqual(summary["metrics"]["sharpe"], 1.4)
        self.assertEqual(summary["jobs"][0]["status"], "succeeded")


if __name__ == "__main__":
    unittest.main()
