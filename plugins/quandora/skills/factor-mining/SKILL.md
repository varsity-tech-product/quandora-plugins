---
name: factor-mining
description: Use when an agent should create or submit a Quandora Factor Mining plugin.py, run a user-scoped backtest, fetch safe artifacts, save local result files, summarize outcomes, or resume a run through Quandora.
---

# Quandora Factor Mining

Use this skill to run Factor Mining through the authenticated Quandora connection exposed by the host as `quandora`.

The agent drafts a valid Factor Mining `plugin.py`, submits the complete source inline, waits for the backtest result, fetches available artifacts, saves safe local files when the host allows it, and summarizes the outcome.

If the required Quandora tools are visible, continue automatically. If they are not visible, use the host's normal Quandora connection path before stopping:

- Codex CLI/TUI: run `codex mcp login quandora`. Wait for the user to complete the browser authorization flow, then check again for `factor_mining_status`.
- Codex Desktop: the plugin provides the Quandora connector. If the first use opens the authorization flow, wait for the user to authorize Quandora in the browser, then continue in a new chat. If the tools still are not visible, tell the user to fully quit and reopen Codex Desktop.
- Claude Code: open `/mcp`, authenticate `quandora`, then start a new chat.
- Claude Desktop: the plugin alone is not enough. Tell the user to open Settings -> Connectors, add a Connector named `quandora` with URL `https://mcp-staging.varsity.lol/factor-mining`, click Connect, authorize Quandora in the browser, then start a new chat.
- OpenClaw: run `openclaw mcp login quandora`, complete the printed authorization flow, then start a new chat.

Do not ask for Quandora API keys, `vt_` keys, bearer tokens, service tokens, or credentials. Do not use raw HTTP calls, local helper scripts, direct internal service calls, local execution keys, or credential paste flows as a fallback.

## Available Actions

Use only the Factor Mining actions exposed by `quandora`:

- `factor_mining_status`
- `factor_mining_list_public_tasks`
- `factor_mining_create_task_session`
- `factor_mining_create_custom_session`
- `factor_mining_validate_plugin_source`
- `factor_mining_request_dedup_context`
- `factor_mining_upload_backtest_wait`
- `factor_mining_resume_run`
- `factor_mining_get_artifact`
- `factor_mining_get_backtest_png_artifacts`
- `factor_mining_get_backtest_png_artifact_chunk`

Some hosts may prefix action names with the server name, such as `quandora__factor_mining_status`. Treat those as the same actions.

Do not use or advertise batch mining.

## Runtime Field Mapping

When writing Factor Sections, use the runtime `bar` object in C# code. Do not reference Python column names directly inside C#.

- `close` -> `bar.Close`
- `volume` -> `bar.Volume`
- `taker_buy_volume` -> `bar.TakerBuyVolume`
- `taker_sell_volume` -> `bar.TakerSellVolume`

For example, use `_takerBuyBuf.Enqueue(bar.TakerBuyVolume);`, not `_takerBuyBuf.Enqueue(takerBuyVolume);`.

## Workflow

Start with `factor_mining_status`. If authorization is missing or the tools are not exposed, use the host's Quandora connection path: desktop hosts use their Connector settings, while CLI/TUI hosts use their MCP login command. Do not ask the user for direct keys.

Determine whether the user wants a public task or a custom idea:

- For public tasks, call `factor_mining_list_public_tasks`, show concise choices, and ask the user to pick one unless they explicitly ask the agent to choose. The selected task's returned `allowed_data` is the authoritative list of data columns available for that task: use only fields included there and do not invent unavailable market fields. If a public task does not include `allowed_data`, stay conservative and use only `close` unless the user chooses a custom idea/session with explicit `allowed_data`. Then call `factor_mining_create_task_session`.
- For a custom idea, call `factor_mining_create_custom_session` with a clear title, category, description, non-empty `allowed_data`, and `fwd_period`. Include every input column the generated factor needs, such as `close`, `volume`, `funding_rate_close`, or `open_interest_close`.

After a session exists, prepare a local result archive when the host supports file writes. Name the run folder from the factor name, not the session ID:

```text
results/factor-mining/<safe_factor_name>/
results/factor-mining/<safe_factor_name>/factor_mining_artifacts/
```

Use the static `FACTOR_NAME` or `FACTOR_TYPE` from the submitted source to create `<safe_factor_name>`. Convert it to lowercase snake_case, replace unsafe characters with `_`, trim repeated separators, and keep it concise. If that folder already exists, append `-2`, `-3`, or another small unique suffix rather than overwriting a prior run. If a local folder is needed before the factor name is known, use `results/factor-mining/local-YYYYMMDD-HHMMSS/`, then move or copy the files into the factor-name folder after the source exists.

Before submission, call `factor_mining_request_dedup_context` with the session context and revise the factor if the returned similar-factor guidance shows a near duplicate.

Create or locate one `plugin.py` source:

- In local coding hosts with a writable workspace, save the submitted source as `plugin.py` inside the run archive. Read the file back and submit the full contents as inline `plugin_source`.
- In chat-only hosts without file writes, keep the generated source in the conversation/tool-call context and submit it directly as inline `plugin_source`.

Never submit a filesystem path or ask Quandora to read local files. Validate the source with `factor_mining_validate_plugin_source`. The validation step is static; do not import, execute, eval, or shell-run generated factor code.

When the source is valid and the user is ready to submit, call `factor_mining_upload_backtest_wait` with `session_id`, inline `plugin_source`, and the selected `fwd_period` when required. Use `fwd_period=7` only when neither the task nor the user specifies a horizon.

Use `factor_mining_resume_run` when a prior run was interrupted.

### Waiting Policy

If `upload_backtest_wait` returns `running`, call `factor_mining_resume_run` at most 6 times in the current request. If the run is still `running`, stop waiting, keep the saved files, and tell the user the run is still in progress. Always print the result folder path.

### Artifact Handling

Treat `factor_card.metrics` returned by `factor_mining_upload_backtest_wait` or `factor_mining_resume_run` as the authoritative backtest result. `factor_mining_get_artifact` is only for optional artifacts listed in the response `artifacts[]`.

Only call `factor_mining_get_artifact` with an `artifact_id` returned from `upload_backtest_wait` or `resume_run`. Do not call it without `artifact_id`. Missing, null, unavailable, omitted, or non-inline artifact content is not a run failure. Treat artifact fetch failures as optional attachment failures unless the run itself failed. Never tell the user backend-oriented messages such as "the factor-card artifact has no inline body", "artifact body is missing", `structuredContent`, "MCP response shape", or "backend envelope".

After a backtest reaches a terminal state, fetch chart PNGs with `factor_mining_get_backtest_png_artifacts` when the tool is available. Use the bare backtest `job_id` from `run.run_id` or each value in `run.job_ids[]`; do not pass an `artifact_id` to this tool. If multiple job IDs are present, fetch PNGs for each job ID. Treat PNG fetch issues as optional artifact failures, not run failures.

When the host supports file writes, save `plugin.py` in the factor-name folder and save all generated or fetched result files inside `factor_mining_artifacts/`:

- Always save `<safe_factor_name>/plugin.py`.
- Always save `factor_mining_artifacts/run_summary.json` from the redacted structured run response.
- Always save `factor_mining_artifacts/factor_card.json` from `run_response.factor_card`, not from artifact fetching.
- Always save `factor_mining_artifacts/artifact_manifest.json` with each returned artifact's `artifact_id`, `name`, `content_type`, and fetch status.
- Save `factor_mining_artifacts/<artifact_name>` only when `factor_mining_get_artifact` returns safe inline JSON/text content or another supported safe content envelope.
- Save PNG chart images under `factor_mining_artifacts/`. Prefer `factor_mining_get_backtest_png_artifact_chunk` when it is available. For each allowed PNG item from the manifest, loop with `offset=0`, `limit=262144`, decode each `content_b64` chunk, append bytes locally, and stop when `next_offset` is null. Verify the final byte length equals `size_bytes`; if possible, verify `md5_hex`.
- If chunk fetching is unavailable and a PNG manifest item includes non-empty `content_b64` small enough for the host to handle, decode it and save `factor_mining_artifacts/<safe_name>.png`. Never print or expose base64 payloads to the user.
- Include PNG chart metadata in `artifact_manifest.json`: `job_id`, `name`, `window`, `content_type`, `size_bytes`, `md5_hex`, `saved_path`, `omitted`, `omitted_windows`, and fetch status for every saved, omitted, withheld, or failed chart.

If artifact content is null, omitted, unavailable, or unsupported, record that status in `artifact_manifest.json` and continue. If a PNG item has `content_b64=null`, record its `omitted` reason such as `oversize` or `total_cap` and do not treat it as a failed run. If `omitted_windows` reports withheld `oos` or `all` charts, mention only that additional chart windows were withheld from local display; do not imply the charts do not exist.

Do not save bearer tokens, presigned URLs, raw service metadata, hidden backend IDs, or credentials. If the host does not support file writes, continue the workflow and say local archiving is not available in that host.

## Final Response

Summarize status, factor name, key metrics from `factor_card.metrics`, and safe diagnostics if the run failed. Inspect `ok`, `status`, `terminal_status`, `failures`, sanitized job statuses, artifact availability, and factor-card metrics. Do not mention backend internals, and do not treat optional artifact unavailability as failure.

Never show backend job IDs, presigned URLs, bearer tokens, raw credentials, or full `plugin.py` source in user-facing summaries. It is safe to show local result and artifact folder paths created by the current host.

At the end of every completed, failed, or interrupted run, always explicitly show where local result files were saved. If a specific file was not created, omit only that file line. Still print the result folder if available.

For GUI/Desktop hosts, use Markdown links with absolute local paths and angle-bracket link targets so paths with spaces work:

Result folder: [Open result folder](</absolute/path/to/results/factor-mining/<safe_factor_name>/>)
Artifact folder: [Open artifact folder](</absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/>)
Plugin source: [plugin.py](</absolute/path/to/results/factor-mining/<safe_factor_name>/plugin.py>)
Run summary: [run_summary.json](</absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/run_summary.json>)
Factor card: [factor_card.json](</absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/factor_card.json>)
Artifact manifest: [artifact_manifest.json](</absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/artifact_manifest.json>)

For CLI/TUI hosts, use plain absolute paths, not Markdown links:

Result folder: /absolute/path/to/results/factor-mining/<safe_factor_name>/
Artifact folder: /absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/
Plugin source: /absolute/path/to/results/factor-mining/<safe_factor_name>/plugin.py
Run summary: /absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/run_summary.json
Factor card: /absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/factor_card.json
Artifact manifest: /absolute/path/to/results/factor-mining/<safe_factor_name>/factor_mining_artifacts/artifact_manifest.json

If the host could not write files, print:

Result folder: not available in this host
Artifact folder: not available in this host

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
