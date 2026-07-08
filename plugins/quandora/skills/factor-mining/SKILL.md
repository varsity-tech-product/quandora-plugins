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
- Claude Desktop: the plugin alone is not enough. Tell the user to open Settings -> Connectors, add a Connector named `quandora` with URL `https://mcp.quandora.ai/factor-mining`, click Connect, authorize Quandora in the browser, then start a new chat.
- OpenClaw: run `openclaw mcp login quandora`, complete the printed authorization flow, then start a new chat.

Do not ask for Quandora API keys, `vt_` keys, bearer tokens, service tokens, or credentials. Do not use raw HTTP calls, local helper scripts, direct internal service calls, local execution keys, or credential paste flows as a fallback.

## Available Actions

Use only the Factor Mining actions exposed by `quandora`:

- `factor_mining_status`
- `factor_mining_list_public_tasks`
- `factor_mining_get_plugin_contract`
- `factor_mining_create_task_session`
- `factor_mining_create_custom_session`
- `factor_mining_validate_plugin_source`
- `factor_mining_request_dedup_context`
- `factor_mining_upload_backtest_wait`
- `factor_mining_resume_run`
- `factor_mining_get_backtest_window_cards`
- `factor_mining_create_backtest_png_download_ticket`
- `factor_mining_create_backtest_raw_artifact_download_ticket`
- `factor_mining_get_backtest_png_artifact_chunk`

Some hosts may prefix action names with the server name, such as `quandora__factor_mining_status`. Treat those as the same actions.

## Plugin Construction Contract

Before writing `plugin.py`, call `factor_mining_get_plugin_contract` and use the returned `plugin_contract` as the source of truth for Python inputs, C# runtime expressions, runtime globals, and horizon defaults.

- For a public task, pass either the selected `task_id` before session creation or the created `session_id` after `factor_mining_create_task_session`.
- For a custom idea, pass the full custom `task_payload` before session creation or the created `session_id` after `factor_mining_create_custom_session`.
- Use `plugin_contract.allowed_data` to decide which input columns the factor may use.
- Use `plugin_contract.fwd_period` unless the user explicitly asked for another supported horizon.
- Use `plugin_contract.data_columns[].python_kwarg` for `build_signal` parameters.
- For every C# runtime queue/buffer enqueue and every numeric C# runtime expression, use the matching `plugin_contract.data_columns[].csharp_double_expression`.
- Follow `plugin_contract.runtime_rules` for required globals, `FACTOR_SECTIONS`, runtime variant, leak rules, extra-buffer rules, and reserved identifiers.

Never infer C# bar fields, field types, decimal/double casts, runtime buffer expressions, or supported data columns from memory. The returned plugin construction contract wins.

## Workflow

Start with `factor_mining_status`. If authorization is missing or the tools are not exposed, use the host's Quandora connection path: desktop hosts use their Connector settings, while CLI/TUI hosts use their MCP login command. Do not ask the user for direct keys.

Determine whether the user wants a public task or a custom idea:

- For public tasks, call `factor_mining_list_public_tasks`, show concise choices, and ask the user to pick one unless they explicitly ask the agent to choose. Then call `factor_mining_get_plugin_contract` with the selected `task_id` or create the session with `factor_mining_create_task_session` and call `factor_mining_get_plugin_contract` with the returned `session_id`.
- For a custom idea, prepare a clear title, category, description, non-empty `allowed_data`, and `fwd_period`. Include every input column the generated factor needs, such as `close`, `volume`, `funding_rate_close`, or `open_interest_close`. Call `factor_mining_get_plugin_contract` with that `task_payload` before session creation, or create the session with `factor_mining_create_custom_session` and call `factor_mining_get_plugin_contract` with the returned `session_id`.

Do not write `plugin.py` until the plugin construction contract has been returned. If the contract cannot be fetched, stop and report that plugin authoring is blocked by missing contract metadata.

After a session exists, prepare one local result archive when the host supports file writes. Use a stable factor slug for the run folder. Prefer the generated top-level `FACTOR_TYPE`; if it is missing, convert `FACTOR_NAME` to lowercase snake_case. For example, `FACTOR_TYPE = "aggressive_flow_exhaustion_reversal"` uses:

```text
Quandora result/factor-mining/aggressive_flow_exhaustion_reversal/
Quandora result/factor-mining/aggressive_flow_exhaustion_reversal/artifacts/
```

Use only the factor slug as the canonical archive directory. The latest run for a factor updates that factor's folder. Keep session and run ids only inside `run_summary.json` / `artifact_manifest.json` when they are needed for traceability, not in the user-facing directory name.

Before submission, call `factor_mining_request_dedup_context` with the session context and revise the factor if the returned similar-factor guidance shows a near duplicate.

Create or locate one `plugin.py` source:

- In local coding hosts with a writable workspace, save the submitted source as `plugin.py` inside the run archive. Read the file back and submit the full contents as inline `plugin_source`.
- In chat-only hosts without file writes, keep the generated source in the conversation/tool-call context and submit it directly as inline `plugin_source`.

When writing `plugin.py`, keep `build_signal` inputs aligned with `plugin_contract.data_columns[].python_kwarg`. Keep `FACTOR_SECTIONS` runtime code aligned with the same columns, and use only `plugin_contract.data_columns[].csharp_double_expression` for numeric runtime references to market data columns.

Never submit a filesystem path or ask Quandora to read local files. Validate the source with `factor_mining_validate_plugin_source`, inline `plugin_source`, and the same context used for the plugin construction contract. Prefer `session_id` after session creation. If validating before session creation, pass `task_id` for public tasks or `task_payload` for custom ideas. The validation step is static; do not import, execute, eval, or shell-run generated factor code.

If validation returns diagnostics, use `repair_hint`, `expected`, `actual`, `field`, and `contract_key_path` to revise `plugin.py`. If a backtest fails with safe diagnostics, use those diagnostics for one focused repair attempt. For C# type or cast failures, re-read the same plugin construction contract and replace runtime expressions with the corresponding `plugin_contract.data_columns[].csharp_double_expression`.

When the source is valid and the user is ready to submit, call `factor_mining_upload_backtest_wait` with `session_id`, inline `plugin_source`, and the selected `fwd_period` when required. Use `plugin_contract.fwd_period` unless the user explicitly requested another supported horizon.

Use `factor_mining_resume_run` when a prior run was interrupted.

### Waiting Policy

If `upload_backtest_wait` returns `running`, call `factor_mining_resume_run` at most 6 times in the current request. If the run is still `running`, stop waiting, keep the saved files, and tell the user the run is still in progress. Always print the result folder path.

### Artifact Handling

Treat the terminal `factor_mining_upload_backtest_wait` or `factor_mining_resume_run` response as the run summary. After a backtest reaches a terminal state, use the window-card response as the manifest for factor cards and chart files. Also request the raw signal parquet artifact when the host exposes that tool:

1. Save the redacted upload/resume result as `run_summary.json`.
2. Call `factor_mining_get_backtest_window_cards` with `windows: ["is", "all"]` and the bare backtest `job_id` from `run.run_id` or `run.job_ids[]`.
3. Save each available returned `factor_card` to the returned `standard_local_name`: `factor_card_is.json` and `factor_card_all.json`.
4. For every returned `png_artifacts[].source_name`, call `factor_mining_create_backtest_png_download_ticket`. The ticket response gives a short-lived Remote MCP download URL for the PNG bytes. Download that URL directly to the returned `standard_local_path`, then verify `size_bytes` and `md5_hex` when the response provides them.
5. Some hosts cannot download URLs directly from tool output, and a ticket may expire before it is consumed. In that case, call `factor_mining_get_backtest_png_artifact_chunk` for the same server `source_name`. Use `standard_local_path` only as the local output path. Loop with `offset=0`, `limit=262144`, decode each `content_b64` chunk, append bytes to `standard_local_path`, and stop when `next_offset` is null.
6. Call `factor_mining_create_backtest_raw_artifact_download_ticket` with the same bare backtest `job_id` and `name: "step4/signal_raw.parquet"`. If a ticket is returned, download it directly to `signal_raw.parquet` in the factor result folder, then verify `size_bytes` and `sha256_hex` when provided.
7. If the raw signal parquet ticket is unavailable, expired, or the artifact is missing, record `signal_raw.parquet` as unavailable in `artifact_manifest.json` and continue. Do not treat raw parquet unavailability by itself as a failed backtest.
8. Save `artifact_manifest.json` listing every source artifact name, local filename, local path, window key when applicable, `size_bytes`, `md5_hex` or `sha256_hex`, download status, and any omitted or unavailable reason.

Use this standard local layout:

```text
Quandora result/factor-mining/<factor_slug>/
  plugin.py
  signal_raw.parquet
  run_summary.json
  factor_card_is.json
  factor_card_all.json
  artifact_manifest.json
  artifacts/
    is/
      group_return_plot.png
      cs_nav_curves.png
      cs_profile_4panel.png
    all/
      group_return_plot.png
      cs_nav_curves.png
      cs_profile_4panel.png
```

For API calls, use `png_artifacts[].source_name`; for local files, save to `png_artifacts[].standard_local_path`.

The normal PNG save path is window cards -> download ticket -> local file. Chunked retrieval is the compatibility path for hosts that cannot consume the ticket URL. Keep PNG bytes out of the conversation and record the chosen save method in `artifact_manifest.json`.

The raw signal save path is terminal run -> raw artifact download ticket -> `signal_raw.parquet` in the factor result folder. Keep parquet bytes out of the conversation and record the source artifact name, local filename, size, checksum, and download status in `artifact_manifest.json`.

If a returned window card has `status` other than `available`, record the omitted or unavailable reason and continue. If a PNG download, chunk fetch, or raw signal download fails, record the failure in `artifact_manifest.json` without failing the completed run.

Do not save bearer tokens, download URLs, raw service metadata, internal IDs, or credentials. If the host does not support file writes, continue the workflow and say local archiving is not available in that host.

## Final Response

Summarize status, factor name, key metrics from the IS factor card when available, and safe diagnostics if the run failed. Inspect `ok`, `status`, `terminal_status`, `failures`, sanitized job statuses, artifact availability, and factor-card metrics. Do not mention internal implementation details, and do not treat optional artifact unavailability as failure.

Never show job IDs, download URLs, bearer tokens, raw credentials, or full `plugin.py` source in user-facing summaries. It is safe to show local result and artifact folder paths created by the current host.

At the end of every completed, failed, or interrupted run, always explicitly show absolute paths for the result folder, artifact folder, PNG chart folder, `plugin.py`, `run_summary.json`, `factor_card_is.json`, `factor_card_all.json`, and `artifact_manifest.json`. If a specific file was not created, say `not created` for that line. Still print the result folder if available.

For GUI/Desktop hosts, use Markdown links with absolute local paths and angle-bracket link targets so paths with spaces work:

Result folder: [Open result folder](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/>)
Artifact folder: [Open artifact folder](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/artifacts/>)
PNG chart folder: [Open PNG chart folder](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/artifacts/>)
Plugin source: [plugin.py](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/plugin.py>)
Run summary: [run_summary.json](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/run_summary.json>)
IS factor card: [factor_card_is.json](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/factor_card_is.json>)
ALL factor card: [factor_card_all.json](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/factor_card_all.json>)
Artifact manifest: [artifact_manifest.json](</absolute/path/to/Quandora result/factor-mining/<factor_slug>/artifact_manifest.json>)

For CLI/TUI hosts, use plain absolute paths, not Markdown links:

Result folder: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/
Artifact folder: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/artifacts/
PNG chart folder: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/artifacts/
Plugin source: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/plugin.py
Run summary: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/run_summary.json
IS factor card: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/factor_card_is.json
ALL factor card: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/factor_card_all.json
Artifact manifest: /absolute/path/to/Quandora result/factor-mining/<factor_slug>/artifact_manifest.json

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

Keep `build_signal` and `FACTOR_SECTIONS` compute logic aligned. Return a `pd.DataFrame` aligned with `close`, use only current and historical data, and keep all data columns within `plugin_contract.allowed_data`.

## Security

- Use only Quandora actions for formal product workflows.
- Never ask for API keys, auth files, user credentials, local execution keys, `vt_` keys, bearer tokens, or service tokens.
- Never print, persist in logs, or summarize full credential values.
- Do not call hosted generation endpoints; the active agent generates factor source in its current host session.
- Do not call internal service URLs or generic URL/API surfaces.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.
- Do not submit filesystem paths instead of inline `plugin_source`.
- Do not print generated `plugin.py` source in summaries.
- Treat downstream IDs, download URLs, and service metadata as private.
- Unavailable artifacts should be recorded in `artifact_manifest.json`. Authentication, authorization, network, malformed response, and server errors must fail clearly with redacted messages.
