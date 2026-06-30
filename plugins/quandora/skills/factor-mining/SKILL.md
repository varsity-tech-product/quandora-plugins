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
- `factor_mining_get_backtest_window_cards`
- `factor_mining_get_backtest_png_artifacts`
- `factor_mining_create_backtest_png_download_ticket`
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

After a session exists, prepare a local result archive when the host supports file writes. Use the session id and attempt id for the stable run folder:

```text
results/factor-mining/<session_id>/<attempt_id>/
results/factor-mining/<session_id>/<attempt_id>/artifacts/
```

Use the exact session id returned by `factor_mining_create_task_session` or `factor_mining_create_custom_session`. Use the attempt id from the upload/resume result when present; otherwise create a stable local attempt folder such as `attempt-1`, incrementing only to avoid overwriting an existing run. Do not use the factor name for the canonical result folder.

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

Treat the terminal `factor_mining_upload_backtest_wait` or `factor_mining_resume_run` response as the run summary. After a backtest reaches a terminal state, follow this required local result workflow:

1. Save the redacted upload/resume result as `run_summary.json`.
2. Call `factor_mining_get_backtest_window_cards` with `windows: ["is", "all"]` and the bare backtest `job_id` from `run.run_id` or `run.job_ids[]`.
3. Save each available returned `factor_card` to the returned `standard_local_name`: `factor_card_is.json` and `factor_card_all.json`.
4. For every returned `png_artifacts[].source_name`, prefer `factor_mining_create_backtest_png_download_ticket`. Download the short-lived ticket URL directly to the returned `standard_local_path`, verify `size_bytes` and `md5_hex` when the download response provides them, and never print or persist the URL.
5. Fall back to `factor_mining_get_backtest_png_artifact_chunk` only if ticket download is unavailable or fails with an optional artifact error. Use the exact server `source_name` in API calls. Loop with `offset=0`, `limit=262144`, decode each `content_b64` chunk, append bytes to the returned `standard_local_path`, and stop when `next_offset` is null.
6. Save `artifact_manifest.json` listing every source artifact name, local path, window key, `size_bytes`, `md5_hex`, download status, and any omitted or unavailable reason.

Use this standard local layout:

```text
results/factor-mining/<session_id>/<attempt_id>/
  plugin.py
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

Remove the `default_` prefix only for local saved filenames. Do not rename server artifact names in API calls.

Inline content is only an optimization for small artifacts. Missing inline content is not a failure. Agents must use download tickets or chunks for PNGs and must not inline large binary payloads in the conversation. Do not treat an empty JSON artifact body as failure when window card data is available from `factor_mining_get_backtest_window_cards`.

`factor_mining_get_artifact` remains optional and is only for artifacts listed by upload/resume responses. Only call it with an `artifact_id` returned from `upload_backtest_wait` or `resume_run`. Missing, null, unavailable, omitted, or non-inline artifact content is not a run failure. Treat artifact fetch failures as optional attachment failures unless the run itself failed. Never tell the user backend-oriented messages such as "the factor-card artifact has no inline body", "artifact body is missing", `structuredContent`, "MCP response shape", or "backend envelope".

If artifact content is null, omitted, unavailable, or unsupported, record that status in `artifact_manifest.json` and continue. If a returned window card has `status` other than `available`, record the omitted/unavailable reason and continue. If a PNG download or chunk fetch fails, record the failure in `artifact_manifest.json` without failing the completed run.

Do not save bearer tokens, presigned URLs, raw service metadata, hidden backend IDs, or credentials. If the host does not support file writes, continue the workflow and say local archiving is not available in that host.

## Final Response

Summarize status, factor name, key metrics from the IS factor card when available, and safe diagnostics if the run failed. Inspect `ok`, `status`, `terminal_status`, `failures`, sanitized job statuses, artifact availability, and factor-card metrics. Do not mention backend internals, and do not treat optional artifact unavailability as failure.

Never show backend job IDs, presigned URLs, bearer tokens, raw credentials, or full `plugin.py` source in user-facing summaries. It is safe to show local result and artifact folder paths created by the current host.

At the end of every completed, failed, or interrupted run, always explicitly show where local result files were saved. If a specific file was not created, omit only that file line. Still print the result folder if available.

For GUI/Desktop hosts, use Markdown links with absolute local paths and angle-bracket link targets so paths with spaces work:

Result folder: [Open result folder](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/>)
Artifact folder: [Open artifact folder](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/artifacts/>)
PNG chart folder: [Open PNG chart folder](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/artifacts/>)
Plugin source: [plugin.py](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/plugin.py>)
Run summary: [run_summary.json](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/run_summary.json>)
IS factor card: [factor_card_is.json](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/factor_card_is.json>)
ALL factor card: [factor_card_all.json](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/factor_card_all.json>)
Artifact manifest: [artifact_manifest.json](</absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/artifact_manifest.json>)

For CLI/TUI hosts, use plain absolute paths, not Markdown links:

Result folder: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/
Artifact folder: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/artifacts/
PNG chart folder: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/artifacts/
Plugin source: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/plugin.py
Run summary: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/run_summary.json
IS factor card: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/factor_card_is.json
ALL factor card: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/factor_card_all.json
Artifact manifest: /absolute/path/to/results/factor-mining/<session_id>/<attempt_id>/artifact_manifest.json

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
