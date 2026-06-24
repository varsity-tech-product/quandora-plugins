---
name: factor-mining
description: Use when an agent should create or submit a Quandora Factor Mining plugin.py, run a user-scoped backtest, fetch safe artifacts, save local result files, summarize outcomes, or resume a run through Quandora.
---

# Quandora Factor Mining

Use this skill to run Factor Mining through the authenticated Quandora connection exposed by the host as `quandora-mcp`.

The agent drafts a valid Factor Mining `plugin.py`, submits the complete source inline, waits for the backtest result, fetches available artifacts, saves safe local files when the host allows it, and summarizes the outcome.

If the required Quandora tools are visible, continue automatically. If they are not visible, use the host's normal Quandora connection path before stopping:

- Codex CLI or Codex Desktop: run `codex mcp login quandora-mcp`. Wait for the user to complete the browser authorization flow, then check again for `factor_mining_status`. If the tools still are not visible in the current host session, tell the user to fully quit/reopen Codex Desktop or start a new chat.
- Claude Code: open `/mcp`, authenticate `quandora-mcp`, then start a new chat.
- Claude Desktop: connect the Quandora connector in Settings, then start a new chat.
- OpenClaw: run `openclaw mcp login quandora-mcp`, complete the printed authorization flow, then start a new chat.

Do not ask for Quandora API keys, `vt_` keys, bearer tokens, service tokens, or credentials. Do not use raw HTTP calls, local helper scripts, direct internal service calls, local execution keys, or credential paste flows as a fallback.

## Available Actions

Use only the Factor Mining actions exposed by `quandora-mcp`:

- `factor_mining_status`
- `factor_mining_list_public_tasks`
- `factor_mining_create_task_session`
- `factor_mining_create_custom_session`
- `factor_mining_validate_plugin_source`
- `factor_mining_request_dedup_context`
- `factor_mining_upload_backtest_wait`
- `factor_mining_resume_run`
- `factor_mining_get_artifact`

Some hosts may prefix action names with the server name, such as `quandora-mcp__factor_mining_status`. Treat those as the same actions.

Do not use or advertise batch mining.

## Workflow

Start with `factor_mining_status`. If authorization is missing or the tools are not exposed, use the host's Quandora connection path. In Codex, run `codex mcp login quandora-mcp` yourself before asking the user to take action. Do not ask the user for direct keys.

Determine whether the user wants a public task or a custom idea:

- For public tasks, call `factor_mining_list_public_tasks`, show concise choices, and ask the user to pick one unless they explicitly ask the agent to choose. Then call `factor_mining_create_task_session`.
- For a custom idea, call `factor_mining_create_custom_session` with a clear title, category, description, non-empty `allowed_data`, and `fwd_period`. Include every input column the generated factor needs, such as `close`, `volume`, `funding_rate_close`, or `open_interest_close`.

After a session exists, prepare a local result archive when the host supports file writes:

```text
results/factor-mining/<session_id>/attempt-<n>/
```

Use `attempt-1` for the first submission in a session and increment it only when submitting a revised factor in the same session. If a local folder is needed before a session exists, use `results/factor-mining/local-YYYYMMDD-HHMMSS/`, then move or copy the files into the session folder after the session exists.

Before submission, call `factor_mining_request_dedup_context` with the session context and revise the factor if the returned similar-factor guidance shows a near duplicate.

Create or locate one `plugin.py` source:

- In local coding hosts with a writable workspace, save the submitted source as `plugin.py` inside the run archive. Read the file back and submit the full contents as inline `plugin_source`.
- In chat-only hosts without file writes, keep the generated source in the conversation/tool-call context and submit it directly as inline `plugin_source`.

Never submit a filesystem path or ask Quandora to read local files. Validate the source with `factor_mining_validate_plugin_source`. The validation step is static; do not import, execute, eval, or shell-run generated factor code.

When the source is valid and the user is ready to submit, call `factor_mining_upload_backtest_wait` with `session_id`, inline `plugin_source`, and the selected `fwd_period` when required. Use `fwd_period=7` only when neither the task nor the user specifies a horizon.

If the run is still running, call `factor_mining_resume_run` until it reaches a terminal state or the host session must stop. Use `factor_mining_resume_run` when a prior run was interrupted. Use `factor_mining_get_artifact` only for artifact identifiers returned by Quandora.

When the host supports file writes, save safe result files in the same run archive:

- `run_summary.json` for the redacted structured run summary.
- `factor_card.json` for factor-card metrics when available.
- `artifacts/<artifact_name>` for safe artifacts fetched with `factor_mining_get_artifact`.

Do not save bearer tokens, presigned URLs, raw service metadata, hidden backend IDs, or credentials. If the host does not support file writes, continue the workflow and say local archiving is not available in that host.

## Final Response

Summarize the result clearly. Inspect `ok`, `status`, `terminal_status`, `failures`, sanitized job statuses, artifact availability, and factor-card metrics. If the run failed or was cancelled, report the terminal status and safe error details.

Never show backend job IDs, presigned URLs, bearer tokens, raw credentials, or full `plugin.py` source in user-facing summaries. It is safe to show local result and artifact folder paths created by the current host.

At the end of every completed, failed, or interrupted run, print these explicit path lines when the host supports file writes. Use absolute local paths so GUI hosts can render them as clickable folders:

```text
Result folder: /absolute/path/to/results/factor-mining/<session_id>/attempt-<n>/
Artifact folder: /absolute/path/to/results/factor-mining/<session_id>/attempt-<n>/artifacts/
```

If the host could not write files, print:

```text
Result folder: not available in this host
Artifact folder: not available in this host
```

## plugin.py Contract

Use this minimum shape when the user has not supplied an existing plugin. The metadata values must be static top-level literals so Quandora can parse them without executing source code.

```text
from typing import Any, Dict

import pandas as pd

FACTOR_TYPE = "snake_case_unique_factor_type"
FACTOR_NAME = "human_readable_factor_name"
FACTOR_DEFAULT_PARAMS = {"window": 7}

FACTOR_SECTIONS = {
    "__FACTOR_DESCRIPTION__": "Trailing close-to-close momentum.",
    "__FACTOR_FORMULA__": "close / close[window bars ago] - 1",
    "__FACTOR_TYPE__": FACTOR_TYPE,
    "__FACTOR_PARAM_FIELDS__": "        private int _window;\n",
    "__FACTOR_INIT__": '            _window = GetIntParameter("window", 7);\n',
    "__FACTOR_LOG__": '            Log($"[INIT] window={_window}");\n',
    "__PRICE_WINDOW_EXPR__": "_window + 1",
    "__EXTRA_BUF_FIELDS__": "",
    "__EXTRA_BUF_ENQUEUE__": "",
    "__EXTRA_BUF_DEQUEUE__": "",
    "__EXTRA_BUF_TOARRAY__": "",
    "__FACTOR_COMPUTE_BODY__": """
            var n = prices.Length;
            if (n < _window + 1) return false;
            var past = prices[n - _window - 1];
            if (past == 0) return false;
            rawSignal = prices[n - 1] / past - 1.0;
            return true;
""",
}


def build_signal(close: pd.DataFrame, params: Dict[str, Any], **data: Any) -> pd.DataFrame:
    window = int(params.get("window", FACTOR_DEFAULT_PARAMS["window"]))
    signal = close.pct_change(window)
    return signal.reindex_like(close)
```

Keep `build_signal` and `FACTOR_SECTIONS` compute logic aligned. Return a `pd.DataFrame` aligned with `close`, use only current and historical data, and keep all data columns within the session `allowed_data` contract.

## Security

- Use only Quandora actions for formal product workflows.
- Never ask for OpenAI API keys, Codex auth files, BYOK secrets, frontend user credentials, raw Factor Mining credentials, local execution keys, `vt_` keys, bearer tokens, or service tokens.
- Never print, persist in logs, or summarize full credential values.
- Do not call hosted generation endpoints; the active agent generates factor source in its current host session.
- Do not call frontend-user credential management, BYOK, Codex profile, task publishing, internal service URLs, or generic URL/API surfaces.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.
- Do not submit filesystem paths instead of inline `plugin_source`.
- Do not print generated `plugin.py` source in summaries.
- Treat downstream IDs, presigned URLs, and service metadata as private.
- Artifact `404` and `410` responses mean unavailable. Authentication, authorization, network, malformed response, and server errors must fail clearly with redacted messages.
