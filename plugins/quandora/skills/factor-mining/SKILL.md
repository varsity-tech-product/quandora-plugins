---
name: factor-mining
description: Use when the user explicitly asks about caller-owned or reusable Factor Mining factor families or history, or asks to construct, submit, backtest, resume, retrieve, or briefly summarize artifacts for a Factor Mining plugin. Route deep diagnosis and optimization of an existing factor result to factor-analysis.
---

# Quandora Factor Mining

Bundled plugin version: 3.1-preview

Use this skill to run Factor Mining through the authenticated Quandora connection exposed by the host as `quandora`.

The agent drafts a valid Factor Mining `plugin.py`, submits the complete source inline, waits for the backtest result, saves one verified FM-owned Result Bundle ZIP when the host allows it, and summarizes the outcome.

OAuth and all credentials are handled by the host. Quandora access tokens expire after 7 days, and the host MCP client should use its stored rotating refresh token automatically. Never inspect, print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

## Plugin Version Reminder

On the first entry into any Quandora skill in the current conversation, if the conversation history does not already contain one successful `qd_plugin_ver` call and no earlier version-check attempt has occurred, call it once before the business entry point. Pass the bundled plugin version declared by the current skill verbatim as `installed_version`; never infer it from memory, the remote latest version, or the host name.

Treat the bundled version as an opaque release label: pass it verbatim and never parse, order, or normalize it.

- If `update_available=false`, continue silently.
- If `update_available=true`, say exactly: `The latest Quandora plugin version is <latest_version>. Please update the plugin.` Then say: `A Quandora MCP access token is valid for 7 days. After 7 days, use the prompt below to ask your agent to refresh the connection; it should use automatic refresh first and CLI re-authentication only if required.` Then provide this exact copyable prompt in a fenced `text` block: `Refresh the Quandora MCP connection. If automatic refresh fails, re-authenticate it with the CLI.` Then immediately continue the user's original request.
- If `qd_plugin_ver` is missing, disabled, invisible, or fails, do not report that the plugin is outdated, do not retry the check anywhere later in the current conversation, and continue the original request without a version message or any change to the business workflow. OAuth or connection failures continue through the existing safe connection-handling path; never bypass MCP with raw HTTP.
- Never install, update, uninstall, or reload a plugin; execute an update command; ask whether to update; immediately start OAuth or reauthorize merely because of the version result; provide a platform-specific command in the version reminder; or delay the original request. The copyable prompt is information for the user to invoke after 7 days, not permission to run it during the version check.
- A later entry into Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, or Paper Trading in the same conversation recognizes the prior successful version check and does not call it or remind again.
- Treat `qd_plugin_ver` as optional for connection readiness. Its absence alone never triggers connection recovery or changes the required business-tool set.

The version check is not a business action. For a normal Factor Mining workflow, check first when required above and then call `fm_status` under the existing rules. For a bare Strategy factor-list request, check first when required and then make the one business call `sb_list_eligible`. For Strategy composition, check first when required and then call `sb_get_contract` under the existing rules. All other exact call-count, pagination, and mutation constraints remain unchanged.

<!-- end-plugin-version-reminder -->

If the required Quandora tools are visible, continue automatically. If they are not visible, tell the user to update or reinstall the current Quandora plugin, then use the host's normal Quandora reconnect and browser re-authorization path before stopping:

- Codex CLI/TUI: run `codex mcp login quandora`. Wait for the user to complete the browser authorization flow, then check again for `fm_status`.
- Codex Desktop: the plugin provides the Quandora connector. If the first use opens the authorization flow, wait for the user to authorize Quandora in the browser, then continue in a new chat. If the tools still are not visible, tell the user to fully quit and reopen Codex Desktop.
- Kimi Code: run `/mcp-config login plugin-quandora:quandora`, complete the browser authorization flow, then start a new chat and check `/mcp`.
- Claude Code: open `/mcp`, authenticate `quandora`, then start a new chat.
- Claude Desktop: the plugin alone is not enough. Tell the user to open Settings -> Connectors, add a Connector named `quandora` with URL `https://mcp.quandora.ai/quant`, click Connect, authorize Quandora in the browser, then start a new chat.
- CodeBuddy and the WorkBuddy China edition: update or reinstall the `quandora` plugin, reconnect its plugin-managed Remote MCP server, complete the host-native browser authorization flow, then start a new chat.

Do not start a new authorization flow merely because an access token reached its seven-day lifetime or because of a single authorization response while the host is refreshing. Reauthorize only when the host reports a terminal authorization failure or still requires authorization after refresh handling.

Do not ask for Quandora API keys, `vt_` keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, service tokens, or pasted credentials. Do not use raw HTTP calls, local helper scripts, direct internal service calls, local execution keys, or credential paste flows. The only permitted direct HTTP download is consuming a short-lived Remote MCP artifact URL returned by a Factor Mining download-ticket action; never construct, modify, reuse, or persist that URL.

## Available Actions

After routing has confirmed Factor Mining scope, use only the Factor Mining actions exposed by `quandora`. The artifact-ticket download exception above is only for consuming returned artifact bytes; it is not permission to call a service API directly.

- `fm_status`
- `fm_list_factors`
- `fm_get_history`
- `fm_list_tasks`
- `fm_get_contract`
- `fm_task_session`
- `fm_custom_sess`
- `fm_validate`
- `fm_dedup_context`
- `fm_run_backtest`
- `fm_resume_run`
- `fm_bundle_ticket`
- `fm_bundle_chunk`
- `qd_get_guidance`
- `qd_plugin_ver` (conversation-level read-only reminder check; not a business action)

Some hosts may prefix action names with the server name, such as `quandora__fm_status`. Treat those as the same actions.

## Plugin Construction Contract

Before writing `plugin.py`, call `fm_get_contract` and use the returned `plugin_contract` as the source of truth for Python inputs, C# runtime expressions, runtime globals, and horizon defaults.

- Use `plugin_contract.allowed_data` to decide which input columns the factor may use.
- Use `plugin_contract.fwd_period` after the contract is returned. For custom ideas, pass `fwd_period: 7` to `fm_custom_sess` unless the user explicitly asks for another supported horizon.
- Use `plugin_contract.data_columns[].python_kwarg` for `build_signal` parameters.
- Whenever C# reads a market-data column from `bar`, including every extra-buffer enqueue, use the matching `plugin_contract.data_columns[].csharp_double_expression`. Do not use `bar` expressions inside `__FACTOR_COMPUTE_BODY__`; that section can use only the variables listed by its contract, normally `prices`, canonical extra-buffer arrays, `rawSignal`, and factor-owned fields.
- Follow `plugin_contract.runtime_rules` for required globals, `FACTOR_SECTIONS`, runtime variant, leak rules, extra-buffer rules, and reserved identifiers.
- When an additional runtime column is needed, use its matching `plugin_contract.runtime_rules.extra_buffer.column_patterns` entry. Copy that entry's field, enqueue, dequeue, and to-array snippets exactly into the corresponding `FACTOR_SECTIONS` values; do not reconstruct or normalize the snippets.

For public work, consume `plugin_contract.task_payload` as the final selected Task definition,
including its description, hints, alpha source, research directions, feature hints, regimes,
risks, and target behavior. If it materially differs from the Task the user selected, stop and
present the changed semantics instead of silently authoring a different thesis. Consume each
selected column's returned source, meaning, unit, comparability, normalization, missing-value,
caution, and upstream-version metadata plus `plugin_contract.runtime_rules.research_guidance`.
Do not maintain a local field dictionary or a static copy of the nine public Task definitions.
Read [86-Field Research Contract Consumption](references/binance-intraday-contract.md) after the
scoped contract is returned.

C# naming rules have this strict precedence:

1. Copy every contract-generated field, enqueue, dequeue, and to-array snippet byte-for-byte. A general naming rule never rewrites an identifier inside a returned canonical snippet.
2. Name factor-owned class fields with the contract's current `_factor...` prefix/style.
3. Name compute-body locals created by the factor with a descriptive `factor...` prefix. Avoid broad names such as `n` or `past`, and avoid every returned reserved local or extra-array reserved identifier.

When `plugin_contract.runtime_rules.factor_sections.all_values_must_be_string_literals` is true, every `FACTOR_SECTIONS` value must be a static string literal. In particular, write `"__FACTOR_TYPE__": "my_factor_type"`, not `"__FACTOR_TYPE__": FACTOR_TYPE`. Keep the top-level `FACTOR_TYPE` literal and the duplicated `__FACTOR_TYPE__` literal byte-for-byte identical. Name factor-owned C# identifiers with `plugin_contract.runtime_rules.csharp_runtime_rules.factor_owned_identifier_prefix` when that rule is returned.

Do not send multiple selectors in one plugin-contract call. Do not retry an identical non-retryable request. Do not silently change the user's research mechanism after a non-retryable validation error.

Never infer C# bar fields, field types, decimal/double casts, runtime buffer expressions, or supported data columns from memory. The returned plugin construction contract wins.

## Workflow

Before entering a Factor Mining workflow, route the request:

- Bare requests to list available, eligible, or selectable Strategy factors, and requests for the Strategy factor pool, exit this skill and hand off to the Strategy Building skill. That skill calls only `sb_list_eligible` for the request. Do not first call `fm_status` or `fm_list_factors`, do not call both lists, and do not ask a clarification question for a bare request.
- Requests explicitly about the caller's Factor Mining factors, reusable Factor Mining factor families, factor history, branches, versions, or previous Factor Mining runs remain in this skill and route to `fm_list_factors`.

After routing has confirmed Factor Mining scope, call `fm_status` exactly once at the start of the normal Factor Mining workflow. If authorization is missing or the tools are not exposed, use the host's Quandora connection path: desktop hosts use their Connector settings, while CLI/TUI hosts use their MCP login command. Do not ask the user for direct keys.

Before routing to factor creation, recognize intentional reuse and history intent. If the user asks
about existing factors, stable versions, prior successful factors, factor evolution, or past runs,
follow the reuse workflow below. Otherwise keep the existing creation workflow unchanged.

### Approved Guidance

Use `qd_get_guidance` only when approved product semantics are needed. It accepts only a
known `guide_id`. Supply `sections` only for `operation.factor.history.read` or
`operation.result.read`; omit `sections` for the capability-only `metric.backtest.grade` guide.
Pass `if_guide_revision` when revalidating a previous response, and honor a not-modified response
without fabricating content. The known ids for this release are:

- `operation.factor.history.read`
- `operation.result.read`
- `metric.backtest.grade`

Use each guide only for its named factor-history, result, or grade operation. Do not browse for
Guidance or invent a guide id. Treat each returned
`mcp_invocation.tools.<tool>.caller_supplied_fields` list as
the only invocation boundary. Upstream sections marked semantic background may explain identity,
verification, privacy, results, or grades, but they never create a mutation/retest tool or an input
field. Service-level `Actor.idempotency_key` / `Idempotency-Key` is transport-managed and is never
an MCP tool argument.

### Intentional Reuse and History

1. `fm_list_factors` lists caller-owned reusable Factor Mining factor families; it is
   not the Strategy eligible-factor pool. Call it first and show compact factor-family rows. Omit
   `page_size` unless pagination is needed; when present it must be an integer from 1 through 20.
   Do not hydrate or fetch history for every row. A failed list call is an error, not an empty
   result. Never claim zero factors unless a successful response contains an empty `items` array.
   After a list error, stop that read workflow. Do not call
   `fm_get_history` as a fallback.
2. Ask the user to select an exact `factor_id` returned by a successful
   `fm_list_factors` response for the current caller. Only after that explicit selection
   call `fm_get_history`. Never substitute a backtest `run_id`, `job_id`,
   `plugin_id`, `session_id`, PB `intake_result.factor.factor_id`, Strategy top-level compatibility
   selector, Strategy admission ID, or any locally cached ID.
3. Start with the default `summary` view. Request only the controlled `branches`, `versions`, or
   `runs` view needed for the user's next decision. Use only these safe selector combinations:
   - `summary`: do not send `branch_id`, `version_id`, `page_size`, or `page_token`.
   - `branches`: either list with optional `page_size` / `page_token`, or select one exact
     `branch_id` without pagination; do not send `version_id`.
   - `versions`: list all or one `branch_id` with optional pagination, or select one exact
     `version_id` without `branch_id`, `page_size`, or `page_token`.
   - `runs`: may use `version_id` plus `page_size` / `page_token`; do not send `branch_id`.
4. Use only returned metadata and run summaries. Historical source reading and editing are not
   exposed in this release. Do not read a local cache, call another service, or devise a workaround.

When controlled history semantics are needed, call `qd_get_guidance` with
`operation.factor.history.read`, only the relevant `sections`, and `if_guide_revision` when
revalidating a previous response. Honor a not-modified response without fetching unrelated
Guidance.

When the reuse request is complete, stop unless the user also asked to create or backtest a new
factor. Never treat browsing history as permission to edit or resubmit historical source.

Determine whether the user wants a public task or a custom idea:

- For a public task: call `fm_list_tasks`, show concise choices, and select one exact public `task_id`, asking the user to pick unless they explicitly ask the agent to choose. For a task-list-only request, render exactly two user-facing fields per row: the exact returned `name` and the exact returned `category`. Use localized equivalents of `Task name` and `Category` as the only table columns. Never render a `Task ID` column, raw task rows, raw JSON, code-formatted selectors, or any `task_id` value anywhere in the response. If the user needs to select a task, use temporary ordinal choices such as 1, 2, and 3 and map the selected ordinal back to the exact row's `task_id` internally. In every other user-facing task list or selection prompt, label each choice with the exact returned `name`, optionally followed by the exact returned `category`; never display `task_id` or derive a display label from it. Treat `task_id`, including any `task_...` or `taskn...` prefix, as an opaque internal selector used only in subsequent tool calls. When the user selects a displayed name, category, or temporary ordinal, resolve it back to the exact row's `task_id` internally. Treat the selected Task's returned category as authoritative and do not replace or reinterpret it. Internally, treat the selected public Task's returned research fields as one live research thesis for mechanism, feature, regime, risk, and target-behavior choices; do not reduce construction to name/category. Either call `fm_get_contract` with only that exact `task_id` before creating the task session and then create the session for that same task, or create the session first with `fm_task_session` and call `fm_get_contract` with only the returned `session_id`.
- For a custom idea: before choosing `category` and before `fm_custom_sess`, obtain one complete current successful `fm_list_tasks` response. Reuse a complete response already obtained in the same conversation and workflow; otherwise call once in the normal flow. If that read fails with a retryable transport error, the single bounded identical retry below is allowed, but never call it again after a complete success. Require a non-empty bounded list of open public task references. Every row must have `status: open`, a unique non-empty opaque `task_id`, a non-empty bounded returned `category`, non-empty `allowed_data`, and non-empty `core_question`, `primary_alpha_source`, `economic_principle`, `microstructure_logic`, `crypto_specific_mechanism`, `research_directions`, and `target_behavior` arrays. Any malformed row, duplicate ID, missing required semantic field, or empty list is a backend/plugin contract mismatch: stop before `fm_custom_sess`, report the mismatch, and do not fall back to a static classification guess, stale model memory, or invented content. Treat every returned category as authoritative because Product Backend has already applied FM's closed category contract. Do not add a plugin-side backend row-count or category-distribution assertion. Do not require one row per category, and do not fail merely because a new valid public category or an additional valid task appears.

  Compare the user's thesis semantically with the returned research fields across all current rows; never classify from task ID or title alone. Choose exactly the category of the best honestly matching returned public reference. This includes `Technical` when the current response returns it and the thesis matches technical price action, trend, reversal, breakout, range, candlestick, or volume-confirmed pattern semantics. If no returned public reference honestly fits, use the explicit product fallback `Other`. Do not fabricate an `Other` public row, copy a public `task_id` into the custom task/session, or turn this branch into `fm_task_session`.

  Separately, before creating the session, call `fm_get_contract({})` exactly once to read the global construction and data-column contract; the runtime classification read and this construction-contract read are both required. Validate the selected label as either the exact category of the matching row in the complete current response or the unmatched fallback `Other`; do not maintain a separate static copy of the backend category vocabulary. Prepare a clear title, category, description, non-empty `allowed_data`, and `fwd_period` for `fm_custom_sess`, using only exact column names returned by the global contract's `plugin_contract.allowed_data`, including `close`, `volume`, `funding_rate_close`, or `open_interest_close` only when returned. Use `fwd_period: 7` unless the user explicitly asks for another supported horizon. Create the custom session, then call `fm_get_contract` with only the returned `session_id`; treat that scoped contract as authoritative for writing and validating `plugin.py`. Never send a hand-built custom `task_payload` to `fm_get_contract`.

  `fm_custom_sess` has only the canonical flat shape below. This example is valid only when the immediately preceding global contract returned `close` exactly:

  ```json
  {
    "title": "Funding-adjusted trend persistence",
    "description": "Test whether recent close-price persistence survives funding pressure.",
    "category": "Momentum",
    "allowed_data": ["close"],
    "fwd_period": 7
  }
  ```

  Never send `name`, `idea`, `task_id`, or `task_payload` to `fm_custom_sess`.

After either branch returns its scoped contract, continue through the single shared plugin.py writing,
deduplication, validation, upload, resume/polling, and terminal Result Bundle workflow below.

Do not write `plugin.py` until the plugin construction contract has been returned. If the contract cannot be fetched, stop and report that plugin authoring is blocked by missing contract metadata.

After a session exists, do not create a local result archive, extracted result directory, or
`artifacts/` directory. The canonical completed local output is the verified FM-owned ZIP beneath
the exact directory `{user_home}/Quandora result/factor/`. Resolve `{user_home}` to the current
user's absolute home directory before any file operation or user-facing link; never keep the
placeholder or hard-code an account name. Create that directory if it
does not exist; never save a completed Factor ZIP in the parent result directory, the current
workspace, or a Strategy directory. Build `{factor_slug}` from the current user-facing factor name (`FACTOR_NAME`
or the exact returned display name): lowercase it, replace each run of non-`[a-z0-9]` characters
with one underscore, trim outer underscores, and use `factor` if the result is empty. The slug must
not contain a backend UUID, internal selector, snapshot revision, remote filename prefix, or path
separator. A pre-terminal pending diagnostic may retain the existing redacted summary behavior in
the normal authoring workspace, but it is not a completed result and must not be presented as the
canonical Result Bundle.

After session creation, call `fm_dedup_context` with only the `session_id`. Use `query_mode`, `scope`, `memory_stats`, `similar_factors`, and `task_memory_pressure` only to select a fresher research hypothesis. A high `task_memory_pressure` must never stop the workflow, reject a draft, or trigger repeated rewrites.

Before drafting, form a concise research thesis. For public tasks, stay inside the task's economic direction and allowed data. For custom ideas, stay inside the user's stated idea. Consider two or three plausible mechanisms, then choose the one with the clearest economic rationale, the best fit to the plugin contract, and the least overlap with the returned task memory. Prefer genuinely different mechanisms over parameter variants of the same formula.

Treat Task `category` and plugin `FACTOR_TYPE` as separate but strictly aligned fields. `category` is exactly the chosen product label retained by the custom Task/session lineage; `FACTOR_TYPE` is an agent-authored, mechanism-specific, unique snake_case identifier. For every custom factor, the thesis, formula, selected inputs, `FACTOR_NAME`, and `FACTOR_TYPE` must all semantically belong to the category supplied to `fm_custom_sess`. Use a mechanism-specific value such as `funding_adjusted_trend_persistence` inside `Momentum`; `FACTOR_TYPE` must never be a bare category label such as `momentum`, and never infer or rewrite the category from `FACTOR_TYPE`, names, tags, or backtest performance.

Immediately before validation and again after any source repair, verify this category-to-mechanism alignment. For a public task, revise an out-of-category draft to remain inside the selected Task or start the appropriate different task/session; never relabel the published Task. For a custom idea, if the mechanism has changed so that it no longer belongs to the category bound at session creation, do not validate or upload it through that session. Create a new custom session with the correct current returned category and a new invocation identity, then repeat the scoped contract, deduplication, validation, and ordinary upload flow. Do not silently keep a mismatched category or coerce an unrelated mechanism into a category that does not honestly fit.

For named indicators or established formulas, use the canonical inputs when the plugin contract allows them. For example, MFI should use high, low, close, and volume when those columns are available. If required inputs are unavailable, clearly treat the factor as a variant and reflect that in `FACTOR_NAME`, `FACTOR_TYPE`, description, and formula.

Create or locate one `plugin.py` source:

- In local coding hosts with a writable workspace, keep the submitted source as `plugin.py` in the
  normal authoring workspace, read it back, and submit the full contents as inline `plugin_source`.
  Do not copy it into the result directory; the accepted FM-owned `plugin.py` is delivered in the
  Result Bundle ZIP.
- In chat-only hosts without file writes, keep the generated source in the conversation/tool-call context and submit it directly as inline `plugin_source`.

When writing `plugin.py`, keep `build_signal` inputs aligned with `plugin_contract.data_columns[].python_kwarg`. Keep `FACTOR_SECTIONS` runtime code aligned with the same columns. Use each column's `csharp_double_expression` only at runtime sites where `bar` is visible, such as canonical extra-buffer enqueue snippets; inside `__FACTOR_COMPUTE_BODY__`, use `prices` and canonical extra-buffer arrays instead.

After a concrete `plugin.py` exists and before validation or upload, call `fm_dedup_context` again with the `session_id`, source, and concise factor metadata:

```json
{
  "session_id": "<session_id>",
  "source": "<full plugin.py source>",
  "description": "<short natural-language thesis>",
  "formula": "<short formula summary>",
  "limit": 5
}
```

Use `draft_duplicate_risk` as the only duplicate-risk verdict. When it identifies a concrete overlap with an existing factor's core mechanism, revise the candidate so its economic hypothesis, inputs, or formula family are materially different, then check the revised draft again. A medium or high score is not a hard gate only when the candidate is already economically meaningful and materially distinct, and the returned similar factors do not establish a concrete core-mechanism overlap. Otherwise resolve the overlap before validation and upload. Treat `similar_factors` as evidence for this comparison, not as a hard-failure gate.

Never submit a filesystem path or ask Quandora to read local files. Validate the complete, exact source with `fm_validate`, inline `plugin_source`, and the same context used for the plugin construction contract. Normal public and custom workflows validate with `session_id` only after the scoped contract has been returned; do not author or validate a custom plugin from a hand-built `task_payload`.

The agent must not import, execute, eval, or shell-run generated factor code locally. The remote validator performs AST/static checks and may also execute `build_signal` with synthetic inputs in an isolated preflight, while leaving module-level code unexecuted. Therefore `build_signal` must satisfy the contract for both float inputs and numeric values stored with object dtype, must return an aligned float `DataFrame`, and must replace positive or negative infinity with `np.nan` or a finite fallback.

After every source edit, including a deduplication or validation repair, validate the complete,
exact source again. A retryable read, deduplication check, or validation transport failure may
receive at most one identical bounded retry. Never retry an unchanged rejected source, and
`invalid_backend_response` is not retried identically.

Validation diagnostics are prioritized and may expose only the highest-priority failure. The absence of a diagnostic on one attempt does not prove that subsystem is valid; repair the reported issue and revalidate until `accepted` is true. A known compatibility case is `error_code=build_signal_preflight_unsafe`, `operation=build_signal.module`, and `actual=module-scope executable Assign`: before changing `build_signal`, audit top-level metadata and require every `FACTOR_SECTIONS` value to be a string literal, especially `__FACTOR_TYPE__`. This diagnostic can otherwise misattribute a non-literal `FACTOR_SECTIONS` assignment to `build_signal`.

When validation rejects the source, repair it only from the returned safe structured diagnostics:
`schema_version`, `error_code`, `operation`, `dtype`, `expected`, `actual`, `field`,
`contract_key_path`, and `repair_hint`. Ignore arbitrary messages or unrecognized diagnostic
values. For C# type or cast failures, re-read the same plugin construction contract and replace
runtime expressions with the corresponding
`plugin_contract.data_columns[].csharp_double_expression`. If upload or admission fails, use only
the closed `recovery_action` policy below; never infer a mutation retry from `retryable`.

When the source is valid and the user is ready to submit, call `fm_run_backtest` with only `session_id` and the exact inline `plugin_source` that passed validation. Do not send `fwd_period`: the session/scoped contract already binds the horizon. Do not edit, regenerate, reformat, or re-read a different copy between successful validation and submission.

### Mutation Recovery Policy

Read mutation-recovery fields only from the safe error `details`. `retryable` describes service
availability, but `recovery_action` controls mutation behavior. Never use a generic retry rule to
upload, Start, create a replacement session, or change bound input.

- `repair_and_revalidate`: repair only allowlisted safe diagnostics and revalidate the complete
  source in the same session. Do not upload until that repaired source passes validation.
- `create_same_kind_session_after_input_change`: do not reuse the bound pending handle. Create the
  same kind of session with a new invocation identity: public/task-backed stays public/task-backed
  for the exact task, and custom stays custom.
- `retry_same_pending_request`: make at most one bounded replay with the exact same pending handle,
  exact bound request, persisted idempotency identity, and unchanged validated source. Never create
  a session or alter the request.
- `resume_known_run`: resume the exact returned known `run_id`; never upload or Start again.
- `stop_and_report_trace`: stop and report the safe `trace_id`. Do not automatically retry, rewrite
  source, create a session, or re-upload.
- `repair_then_create_same_kind_session`: make one allowlisted diagnostics-led repair, revalidate
  the complete repaired source, then create the same kind of session with a new invocation identity
  before following the ordinary validated upload path once.

Normal `running` with `next_action=resume` resumes only through `fm_resume_run`; it never
uploads or Starts again. Use `fm_resume_run` when a prior known run was interrupted.
These recovery actions do not add an automatic retry loop.

### Waiting Policy

If `upload_backtest_wait` returns `running`, call `fm_resume_run` at most 4 times in the current request.

If the run is still `running` after the fourth resume, stop waiting and treat the archive as a pending run snapshot, not a completed result. Save only files that are already true at that point, such as `plugin.py` and a redacted pending run summary. Do not request Result Bundle metadata or attempt ZIP delivery until a later `fm_resume_run` returns a terminal status. In the final response, clearly say the backtest is still running, the Result Bundle was not requested, and the user can ask to resume later. Show the `{user_home}/Quandora result/factor/` folder path when the host supports local files.

### Result Bundle Handling

Run bundle handling only after `fm_run_backtest` or `fm_resume_run` returns a terminal status such as `succeeded`, `failed`, or `cancelled`. If the run is still `running`, skip this section. Use the redacted terminal response for status and interpretation. For completed runs, the FM-owned ZIP is the only canonical completed-result archive; never create a second completed-result `run_summary.json` beside it.

For a terminal Factor run, issue one initial `fm_bundle_ticket` with the exact canonical backtest
`job_id` from the terminal response. The returned closed metadata and runtime manifest are
authoritative for the immutable FM-owned ZIP. Treat both `available` and a persisted readable
`partial` response as downloadable. Raw Parquet is optional and its absence or pending sync must
not block a readable partial. Do not make any individual artifact a prerequisite or hardcode an
artifact inventory.

Validate the server-provided `safe_filename` as a basename and bind it consistently across the
selected ticket and every chunk response. It is transport metadata only and never determines the
local display filename. Likewise bind the bundle kind, selector, snapshot revision, content type,
size, whole-ZIP SHA-256, and runtime manifest according to the existing closed response contract.

Apply this one bounded materialization recheck before the readable-partial freshness step:

1. If the initial metadata is `pending` with `reason_code=bundle_materializing`, treat it as a
   valid non-readable state, not as a transport or backend failure. Do not use its revision for a
   chunk call, create a file or `.partial`, consume a URL, retry a download ticket, or use a
   legacy-artifact fallback.
2. Wait at most 10 seconds with a host-native bounded wait or timer, then make exactly one fresh current `fm_bundle_ticket`
   call with the same canonical terminal `job_id` and without a
   caller-supplied `snapshot_revision`. Never resubmit or resume the completed Factor run merely
   to make a bundle appear.
3. If that single recheck is still `pending` with `reason_code=bundle_materializing`, stop safely
   and tell the user the Result Bundle is still materializing and can be requested later. Never
   loop. If it is readable `available` or persisted readable `partial`, continue with the ordinary
   URL-first flow. If it becomes another truthful non-readable state, preserve its exact safe
   status and reason and stop. A malformed recheck remains fail-closed.

Apply this one optional freshness step before downloading:

1. If the initial ticket is persisted readable `partial` and its runtime manifest reports one or
   more items with a pending status, wait at most 10 seconds with a short host-native wait or timer.
   Then issue exactly one fresh current `fm_bundle_ticket` with the same public selector and
   without `snapshot_revision`. Never loop or poll for freshness.
2. Do not consume, reuse, display, or log the superseded ticket URL; let it expire naturally. If
   the refresh returns a valid readable newer snapshot, select that response. If it has a transient
   transport failure, retain the initial valid readable partial. If it is a malformed contract
   response, fail closed instead of masking it.
3. If the selected response remains readable `partial`, download it normally, state clearly that
   the snapshot is partial, and report the exact runtime omissions and pending reasons from its
   selected manifest. If the initial partial reports no pending item, do not wait or refresh. A
   later independent user request may obtain a newer current snapshot after synchronization.

The bounded materialization recheck, this optional readable-partial freshness refresh, and the one
fresh-ticket retry after a transient single-use URL failure are three separate bounds. Never
collapse them into a loop. The freshness refresh does not consume the URL retry. Do not use legacy
per-file tools to fill an omitted item, complete Raw Parquet, or
rebuild the selected immutable ZIP. Keep the legacy single-artifact actions only for a user request
that explicitly asks for one compatibility artifact; they are not bundle-completion tools.

Use this URL-first delivery once per request:

1. Require ZIP content type, non-negative size, lowercase SHA-256, and the exact safe local
   destination `{user_home}/Quandora result/factor/{factor_slug}.zip`. Before creating
   any file, create `{user_home}/Quandora result/factor/` if needed. Write only to
   `{user_home}/Quandora result/factor/{factor_slug}.zip.partial` until verification finishes. If the final path
   already contains unrelated bytes or cannot be proven to match the selected ZIP, do not
   overwrite it silently: tell the user and use a different safe user-facing slug chosen with the
   user, never an internal backend identifier.
2. Immediately consume the selected `download_url` in the same execution context that receives it:
   pass it unchanged to the host-native HTTP downloader and stream the response directly to the
   task-created `.partial`, maintaining byte count and SHA-256. Never delete, redact, clear, or
   transform the URL before the HTTP attempt, and do not split ticket parsing and URL consumption
   across unrelated commands or agent turns. This returned URL is an approved short-lived transfer
   capability, not a value to redact before use. Its transient appearance in the ticket response
   and host download-tool invocation is safe and expected. Do not copy it into a persistent file or
   diagnostic log, or retain it after the attempt; it need not be repeated in the final summary.
3. Do not declare the URL unavailable unless an actual HTTP download attempt was made and returned
   a network-policy, expiry, transport, or non-success HTTP failure. After one such transient URL
   failure, issue at most one fresh ticket and immediately consume its new URL for one retry. After
   that actual retry fails, move to MCP fallback. Never reuse a single-use URL/ticket.
4. Verify exact size and SHA-256, ZIP magic/openability, and that every ZIP entry is a safe relative
   path contained by the archive. Then atomically rename the verified `.partial` file to
   `{user_home}/Quandora result/factor/{factor_slug}.zip`.

If the URL is unavailable, blocked by local host network policy, expired, or fails after that one retry, automatically use `fm_bundle_chunk` with the same canonical `job_id` and `snapshot_revision`. This fallback uses the already-working authenticated MCP connection and requires no new host-native file sink or shell network access:

1. Start at offset `0` and request at most `256 KiB` (`262144`) raw bytes per call. For every valid response, decode and append `content_b64` before acting on `terminal`; never print or log the base64. A `terminal: true` response may carry the final non-empty `content_b64`, so those bytes are part of the ZIP and must be appended before stopping. When `terminal` is false, require `next_offset` to equal the current offset plus the decoded byte length and continue from exactly that value. When `terminal` is true, require `next_offset` to be null and the appended total to equal `size_bytes`; do not request another public empty chunk.
2. Enforce the 10 MiB ZIP cap and at most 40 chunk calls. Keep every response bound to the same kind, job ID, snapshot revision, filename, content type, size, and whole-object SHA. Never mix revisions or append an old partial. Do not start a local receiver that exits when its setup command reaches EOF; use a per-response binary-safe append operation, or keep one verified writer session open until the terminal response has been appended.
3. The public chunk contract's `terminal: true` means that response ends the stream; the client must not require `content_b64` itself to be empty and must not request an extra empty response. After appending the terminal response, verify the assembled byte count, whole-ZIP SHA-256, ZIP magic/openability, and safe entry paths before atomic rename. On interruption or any terminal fallback failure, discard only the task-created unverified `.partial` and report that no verified ZIP was saved.

After the bounded materialization recheck when applicable, if the selected bundle metadata is `pending`, `not_available`, or `integrity_failure`, stop before URL/chunk/file creation: no URL, no chunk, no fabricated file. Preserve its safe status/reason. Do not save bearer tokens, download URLs, raw service metadata, artifact IDs, admission IDs, credentials, or any other downstream IDs. The only exception is the current `session_id` / `run_id` local-traceability allowlist described above. If the host does not support file writes, report that no local verified ZIP was saved.

Preserve the verified ZIP as the canonical local output. Do not automatically extract the ZIP,
delete it, re-ZIP it, rename its entries, synthesize missing files, or reconstruct a replacement
archive from individual files. Do not modify ZIP entry timestamps: stable entry timestamps belong
to the FM-owned archive, and the agent must not rebuild the ZIP to change how a file browser
displays them. Normal logs may be present; when the manifest truthfully omits a log because FM
detected concrete prohibited credential or storage-topology content, preserve that omission and do
not bypass it. Do not hardcode an artifact registry, item count, entry-name list, backend commit,
safe-filename UUID pattern, or FM storage implementation. Existing immutable snapshot revisions
are not expected to gain later parity fixes; acceptance of those fixes uses a fresh snapshot.

### Result Insight and Optimization

Give only a brief evidence-based result summary during an ordinary mining workflow. When the user
asks for deep diagnosis, explanation, comparison, or optimization of an existing factor result,
route to `$factor-analysis` with the exact factor and run identity. The saved ZIP remains an optional
export and is not analysis evidence. That skill
owns metric semantics, chart diagnosis, mechanism alternatives, controlled experiments, and
Strategy-readiness assessment. Never auto-submit an optimization from either skill.

## Final Response

Summarize status, factor name, safe diagnostics if the run failed, bundle state, and the exact
verified `{user_home}/Quandora result/factor/{factor_slug}.zip` path when saved. Inspect `ok`, `status`,
`terminal_status`, `failures`, sanitized job statuses, and bundle metadata. Do not mention internal
implementation details or treat an optional bundle item omission recorded by FM as a failed run.
For a selected partial snapshot, state that it is partial and report the exact omissions and pending
reasons from the runtime manifest without claiming completeness.

Never show job IDs, snapshot revisions, bearer tokens, raw credentials, or full `plugin.py` source in user-facing summaries. Do not repeat a consumed or expired download URL in the final summary; this does not prohibit its safe transient appearance in the ticket response or download-tool invocation. It is safe to show the local result folder and verified ZIP path created by the current host.

At the end of every completed, failed, or interrupted run, show the `{user_home}/Quandora result/factor/` folder and
the verified Result Bundle ZIP when saved. For a pending run, mention a redacted pending summary
only if the normal authoring workflow saved one. For a completed run, the FM-owned ZIP is the only
canonical completed-result archive. If the ZIP could not be saved, say so accurately. Never show
job IDs, snapshot revisions, download URLs, tickets, credentials, or bundle base64.

For GUI/Desktop hosts, replace `{user_home}` with the resolved absolute home path and use Markdown
links with angle-bracket link targets so paths with spaces work:

Result folder: [Open result folder](<{user_home}/Quandora result/factor/>)
Result Bundle ZIP: [verified ZIP](<{user_home}/Quandora result/factor/{factor_slug}.zip>)

For CLI/TUI hosts, replace `{user_home}` with the resolved absolute home path and use plain
absolute paths, not Markdown links:

Result folder: {user_home}/Quandora\ result/factor/
Result Bundle ZIP: {user_home}/Quandora\ result/factor/{factor_slug}.zip

If the host could not write files, print:

Result folder: not available in this host
Result Bundle ZIP: not available in this host

## plugin.py Contract

Use this minimum shape when the user has not supplied an existing plugin. The metadata values must be static top-level literals so Quandora can parse them without executing module-level code. The current cross-sectional runtime requires `__FACTOR_LOG__` to exist but does not inject it; keep it only as compatible metadata and do not depend on it for runtime diagnostics.

```python
from typing import Any, Dict

import numpy as np
import pandas as pd

FACTOR_TYPE = "snake_case_unique_factor_type"
FACTOR_NAME = "human_readable_factor_name"
FACTOR_DEFAULT_PARAMS = {"window": 7}

FACTOR_SECTIONS = {
    "__FACTOR_DESCRIPTION__": "Trailing close-to-close momentum.",
    "__FACTOR_FORMULA__": "close / close[window bars ago] - 1",
    "__FACTOR_TYPE__": "snake_case_unique_factor_type",
    "__FACTOR_PARAM_FIELDS__": "        private int _factorWindow;\n",
    "__FACTOR_INIT__": '            _factorWindow = GetIntParameter("window", 7);\n',
    "__FACTOR_LOG__": '            Log($"[INIT] window={_factorWindow}");\n',
    "__PRICE_WINDOW_EXPR__": "_factorWindow + 1",
    "__EXTRA_BUF_FIELDS__": "",
    "__EXTRA_BUF_ENQUEUE__": "",
    "__EXTRA_BUF_DEQUEUE__": "",
    "__EXTRA_BUF_TOARRAY__": "",
    "__FACTOR_COMPUTE_BODY__": """
            var factorPriceCount = prices.Length;
            if (_factorWindow < 1 || factorPriceCount < _factorWindow + 1) return false;
            var factorPastPrice = prices[factorPriceCount - _factorWindow - 1];
            if (Math.Abs(factorPastPrice) < 1e-12) return false;
            rawSignal = prices[factorPriceCount - 1] / factorPastPrice - 1.0;
            if (double.IsNaN(rawSignal) || double.IsInfinity(rawSignal)) return false;
            return true;
""",
}


def build_signal(close: pd.DataFrame, params: Dict[str, Any], **data: Any) -> pd.DataFrame:
    window = int(params.get("window", FACTOR_DEFAULT_PARAMS["window"]))
    values = close.apply(pd.to_numeric, errors="coerce").astype(float)
    if window < 1:
        return (values * np.nan).reindex_like(close)
    signal = values.pct_change(window)
    signal = signal.replace([np.inf, -np.inf], np.nan).astype(float)
    return signal.reindex_like(close)
```

Keep `build_signal` and `FACTOR_SECTIONS` compute logic aligned:

1. Defaults: each `GetIntParameter("k", N)` literal in `__FACTOR_INIT__` must equal the matching `FACTOR_DEFAULT_PARAMS` value. The composer inlines those literals, so a mismatch silently produces two different factors.
2. Window: consume the same number of bars as the matching Python rolling window, slicing the required trailing bars from the end of the C# array. Never assume `prices.Length` equals the factor's own window.
3. Missing data: Python must produce `NaN` under the same conditions in which C# returns `false`.

Return a float `pd.DataFrame` aligned with `close`, use only current and historical data, and keep all data columns within `plugin_contract.allowed_data`. The duplicated `FACTOR_TYPE` and `__FACTOR_TYPE__` strings must match exactly; never replace the section value with a reference to the top-level variable.

## Security

- Use only Quandora actions for formal product workflows, except for consuming a short-lived opaque Result Bundle URL returned by `fm_bundle_ticket` exactly once.
- Never ask for API keys, auth files, user credentials, local execution keys, `vt_` keys, bearer tokens, or service tokens.
- Never print, persist in logs, or summarize full credential values.
- Do not call hosted generation endpoints; the active agent generates factor source in its current host session.
- Do not call internal service URLs or generic URL/API surfaces, and never construct a download URL. The returned Remote MCP Result Bundle URL is the sole direct-download exception.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.
- Do not submit filesystem paths instead of inline `plugin_source`.
- Do not print generated `plugin.py` source in summaries.
- Treat downstream IDs and service metadata as private. Treat the returned one-time Result Bundle URL as an approved immediate download capability under the URL-first rules above, not as a credential that must be removed before use.
- Bundle states and safe reason codes are authoritative. Authentication, authorization, network, malformed response, and server errors must fail clearly with redacted messages.
