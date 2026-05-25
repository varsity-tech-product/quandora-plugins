---
name: factor-mining
description: Use when the user wants Codex to create or submit a Factor Mining plugin.py, run a user-scoped backtest, wait for workflow and job results, fetch artifacts, summarize outcomes, or resume a Factor Mining local-agent run through the Codex plugin helpers.
---

# Factor Mining Local Agent

Use this skill for the Factor Mining Codex plugin product flow. Codex writes or
locates one local `plugin.py`. Factor Mining validates, stores, backtests, and
returns workflow, job, artifact, and factor result data through orchestrator
APIs.

Codex runs the helper commands from the plugin directory and summarizes the
result for the user. The user does not need to run the command sequence manually.

## Setup And Status

Setup uses the production Factor Mining API URL by default:

```text
https://d25q1jf66e8y4g.cloudfront.net
```

If setup is missing, run setup from the plugin directory. Never ask the user to
paste the Factor Mining Agent API Key into chat.

```bash
python3 scripts/factor_setup.py
```

The setup script collects the Agent API Key through a hidden terminal prompt.
For automation, it can read `FACTOR_MINING_AGENT_API_KEY` from the environment
or non-echo stdin:

```bash
python3 scripts/factor_setup.py --api-key-stdin
```

Use `--base-url` only when the user explicitly provides a staging or private
Factor Mining API environment:

```bash
python3 scripts/factor_setup.py --base-url <staging-or-private-api-url>
```

Setup and status must call `/agent/status`. Continue only when the response
reports `key_purpose: external_agent`. If the configured API does not expose
`/agent/status`, tell the user that the Factor Mining API environment must
include the external-agent status endpoint before this plugin can be configured.

Configuration is stored outside project repositories at:

```text
~/.factor-mining-agent/config.json
```

Run state is stored at:

```text
~/.factor-mining-agent/runs/<client_run_id>.json
```

## Hard Security Rules

- Use only a delegated Factor Mining Agent API Key whose `/agent/status`
  response has `key_purpose: external_agent`.
- Never ask for OpenAI API keys, Codex auth files, BYOK secrets, or frontend
  user credentials.
- Never print, persist in logs, or summarize full API keys.
- Do not call QuantAI service endpoints directly.
- Do not call hosted generation endpoints such as `/brainstorm`, `/generate`,
  or `/regenerate`; local-agent mode generates code inside Codex.
- Do not call `/models`, `/prompts/preview`, `/llm-credentials/*`,
  `/codex-profiles/*`, or `/me/external-agent-key`.
- Do not create, update, or patch tasks; delegated external-agent keys are
  read-only for task publication surfaces.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.
- Use `python3 scripts/factor_api.py metadata` or the same `ast` plus
  `ast.literal_eval` approach for static metadata extraction.
- Do not print generated `plugin.py` source in summaries.
- Use only user-visible orchestrator IDs in reports: `session_id`, `plugin_id`,
  `job_id`, `factor_id`, and `strategy_run_id`.
- Treat downstream IDs, presigned URLs, and service metadata as internal fields.

## Acceptance Flow

1. Confirm setup.
   - If config is missing or invalid, run setup.
   - If setup rejects the key, tell the user to provide a Factor Mining Agent
     API Key, not a frontend user key.

2. Understand the task or idea.
   - Worker mode: read tasks, pick one, and tell the user the `task_id` and
     title.
   - Free mode: start from the user's custom factor idea.

```bash
python3 scripts/factor_api.py tasks --limit 20 --status open
```

3. Create or reuse a task-backed session.

For worker mode, a published `task_id` is enough:

```bash
python3 scripts/factor_api.py create-session --task-id <task_id> --client-run-id <client_run_id>
```

For free mode, create a direct `task_payload` before upload. It must include at
minimum:

- `task_id`
- `title`
- `category`
- `description`
- `allowed_data`
- `fwd_period`

`allowed_data` must include every input column the generated `plugin.py` needs,
such as `close`, `volume`, `funding_rate_close`, or `open_interest_close`.
Include useful hints, economic mechanisms, regime considerations, risk sources,
and target behavior when they are available.

```bash
python3 scripts/factor_api.py create-session --idea "<research idea>" --task-payload-file task_payload.json --client-run-id <client_run_id>
```

4. Request dedup context when you have a draft description and formula. Use the
   returned similar factors and duplicate-risk guidance to avoid
   near-duplicates.

```bash
python3 scripts/factor_api.py dedup-context --session-id <session_id> --description "<draft description>" --formula "<draft formula>"
```

5. Write or locate one `plugin.py`.
   - Return a `pd.DataFrame` aligned with `close`.
   - Use only current and historical data.
   - Keep Python `build_signal` and `FACTOR_SECTIONS` C# compute logic aligned.
   - Keep the data columns within the session `allowed_data` contract.

6. Inspect metadata statically before upload.

```bash
python3 scripts/factor_api.py metadata --plugin-path plugin.py
```

7. Run one waitable upload and backtest command. Use `fwd_period=7` when neither
   the task nor user specifies a horizon.

```bash
python3 scripts/factor_upload_backtest.py --session-id <session_id> --plugin-path plugin.py --client-run-id <client_run_id> --position-mode both --fwd-period 7 --wait
```

The upload helper intentionally omits optional `submitter_label` and `agent_id`
fields. Factor Mining applies its external-agent provenance defaults from the
delegated API key.

8. Summarize the compact JSON returned by the wait command. Always inspect
   `ok`, `status`, `terminal_status`, and `failures`. If `ok` is false or
   `failures` is present, report the failed or cancelled job clearly instead of
   presenting the run as successful.

## plugin.py Contract

Use this minimum shape when the user has not supplied an existing plugin. The
metadata values must be static top-level literals so the helper can parse them
without executing source code.

```python
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

Factor Mining backend validation is the authority for runtime contract details.
If upload returns validation `errors` or `warnings`, read them, edit
`plugin.py`, and retry upload. Do not call platform regenerate.

## Backtest And Artifacts

For asynchronous POST endpoints, HTTP `202 Accepted` is expected success.
Treat either `200` or `202` as success for session creation, plugin upload, and
backtest submission.

Short-term deployments may return one job with `position_mode: "cs_only"`.
Do not expect separate TS and CS jobs unless the configured Factor Mining API
environment explicitly returns them.

The wait command fetches `default_factor_card.json` when available. It reports
artifact `404` and `410` as unavailable and continues with the core job result.
Authentication, authorization, network, malformed response, and server errors
must fail clearly with redacted stderr.

Use resume with waiting after an interrupted Codex session:

```bash
python3 scripts/factor_api.py resume --client-run-id <client_run_id> --wait
```

## Result Report

Always include fields that are available in the factor card or job response:

- `ok`
- `status`
- `terminal_status`
- `failures`
- `position_mode`
- `cs_success` and `cs_fail_reasons` when present
- `ts_success` and `ts_fail_reasons` only when present
- `composite_sharpe`, `composite_annual_ret`, and `composite_max_dd`
- `cs_branch.simulation.{sharpe,return,max_drawdown,turnover,fitness}`
- `ts_branch.simulation.{sharpe,return,max_drawdown,turnover,fitness}` only
  when TS results are present
- `icir`, `win_rate`, and `rank_icir`
- `requested_fwd_period`, `actual_fwd_period`, and `horizon_warning`

## Advanced Surfaces

Retest, factor library, promotion, and strategy composition are outside the
normal helper flow. If the user explicitly asks for those operations, inspect
the current Factor Mining API docs, keep all calls user-scoped, and respect
feature gates returned by the API.
