import json
import sys
import unittest
from urllib import request
from urllib.error import HTTPError


PLUGIN_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
TESTS_ROOT = PLUGIN_ROOT / "tests"
sys.path.insert(0, str(TESTS_ROOT))

from acceptance.mock_backend import start_mock_backend
from acceptance.run_mock_acceptance import run_failed_job_scenario, run_success_scenario


class MockAcceptanceTests(unittest.TestCase):
    def test_mock_backend_rejects_protected_endpoint_without_agent_key(self):
        with start_mock_backend() as backend:
            req = request.Request(f"{backend.base_url}/tasks", method="GET")

            with self.assertRaises(HTTPError) as raised:
                request.urlopen(req, timeout=5)

        self.assertEqual(raised.exception.code, 401)

    def test_mock_backend_agent_status_contract(self):
        with start_mock_backend() as backend:
            unauthenticated = request.Request(f"{backend.base_url}/agent/status", method="GET")
            external_agent = request.Request(f"{backend.base_url}/agent/status", method="GET")
            external_agent.add_header("Authorization", "Bearer vt_mock_valid")
            rejected = request.Request(f"{backend.base_url}/agent/status", method="GET")
            rejected.add_header("Authorization", "Bearer user_mock_invalid")

            with self.assertRaises(HTTPError) as raised_unauthenticated:
                request.urlopen(unauthenticated, timeout=5)
            with request.urlopen(external_agent, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            with self.assertRaises(HTTPError) as raised_rejected:
                request.urlopen(rejected, timeout=5)

        self.assertEqual(raised_unauthenticated.exception.code, 401)
        self.assertEqual(payload, {"agent_key": "valid", "status": "ok"})
        self.assertEqual(raised_rejected.exception.code, 403)

    def test_success_scenario_runs_full_helper_flow(self):
        result = run_success_scenario()

        self.assertEqual(result.setup["agent_status"]["status"], "ok")
        self.assertEqual(result.setup["agent_status"]["agent_key"], "valid")
        self.assertEqual(result.session["session_id"], "session_mock_1")
        self.assertEqual(result.metadata["factor_name"], "Mock Liquidity Stress")
        self.assertTrue(result.upload_summary["ok"])
        self.assertEqual(result.upload_summary["status"], "succeeded")
        self.assertEqual(result.upload_summary["artifact"]["status"], "available")
        self.assertEqual(result.artifact["factor_name"], "Mock Liquidity Stress")

    def test_failed_job_scenario_returns_terminal_failure_summary(self):
        result = run_failed_job_scenario()

        self.assertFalse(result.upload_summary["ok"])
        self.assertEqual(result.upload_summary["status"], "failed")
        self.assertEqual(result.upload_summary["terminal_status"], "failed")
        self.assertEqual(result.upload_summary["failures"][0]["job_id"], "job_mock_1")

    def test_acceptance_results_are_json_serializable(self):
        result = run_success_scenario()

        json.dumps(result.to_dict(), sort_keys=True)


if __name__ == "__main__":
    unittest.main()
