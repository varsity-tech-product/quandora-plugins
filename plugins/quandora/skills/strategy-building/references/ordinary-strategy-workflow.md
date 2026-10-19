# Canonical Strategy Workflow

## Select Factors

A bare available-factor request calls only `list_eligible_strategy_factors` with a bounded page.
Use `query` and `filters` only as accepted by this eligible-factor tool. Preserve every selection
constraint and copy `next_page_token` byte-for-byte on requested continuation.

For composition, read `get_strategy_capabilities` when needed to establish supported choices.
The current tool input schema is the sole request boundary; `caller_supplied_fields` describes
caller choices when returned. Do not copy server-managed values into Skill guidance or proposed
inputs, and do not add any field absent from the live submit schema. Do not display or ask for
confirmation of server-managed fields.

Resolve exact Factors through `list_eligible_strategy_factors`; use `get_eligible_strategy_factor`
for eligible detail when needed. Use `include_factor_ids` for supplied exact selectors and preserve
`unresolved_factor_ids` as unresolved; do not replace them with similarly named Factors.
Included rows can carry `strategy_use.status=needs_optimization`. Report the exact Factor and
returned `reasonCode`, `phase`, `runtimeError`, and `observedAt`; preserve nullable support and
admission evidence, and do not select that row or retry detail to override its state. Continue
Factor repair only within the user's authorized scope through `$factor-mining`.
Source and eligibility come from returned data. Grade F or a negative grade score remains
selectable when returned as eligible; do not derive another eligibility rule from metrics.
Copy each selected row's exact `admission.factor_id`,
`admission.factor_version_id`, and `admission.job_id` into `factor_references`. These are the
current Factor input field names; do not infer them from a display name or an admission-row ID.

Sharing or Publication visibility does not establish Strategy eligibility. Resolve a requested
shared Factor through the eligible-factor tools above and select it only when the server returns
an eligible admission record. If it is absent or ineligible, report that limitation; do not copy
source, infer eligibility from a Publication child ID, or switch to an internal endpoint.

A newly authored Factor must go through `$factor-mining` validation, backtest, and admission.
Never reconstruct a retired import action or treat a local plugin as an eligible Factor.

## Create the Definition

Choose a nonblank user-facing name from the user's name or the selected Factor theme and task.
Build one `specification` with `strategy_kind: "cs"`, required `ranking`, and only requested
optional `weighting`, `strategy_type`, and `rebalance_bars`. Equal weighting is server-derived;
for custom weighting use `weighting.mode: "custom"` and finite positive `weighting.weights`
totaling 1, aligned in order with the exact selected `factor_references`.
Never send `portfolio_optimizer`, including null.

For a new Folder, call `create_strategy_folder` with `name`, `specification`, and
`factor_references`. The response contains `strategy_folder.strategy_folder_id` and the first
immutable `strategy.strategy_id`. They are different resources; creation does not itself imply
a Run exists. Preserve the complete returned Strategy definition.

For an existing Folder and a changed definition, read the exact base with `get_strategy`, then
call `create_strategy` with `strategy_folder_id`, `base_strategy_id`, the complete new
`specification`, and `factor_references`. The base remains unchanged.

## Submit and Observe

Call `submit_strategy_backtest` with the exact immutable `strategy_id` and a fresh
`client_request_id` UUID generated before the first submission. Only `start_date` and
`end_date` are optional run choices; omit unspecified dates. Cash, fees, attribution, universe,
provider settings, and execution controls are not caller inputs.

A request to build and backtest authorizes both definition creation and Run submission. Present
consequential choices, but do not require fresh approval merely because another tool is needed.

Use the response as the first snapshot. Copy `run.strategy_run_id` to
`get_strategy_backtest(strategy_run_id=...)`. Read that persisted Run with bounded observation;
no continue command or internal command receipt belongs to this lifecycle. For history call
`list_strategy_backtests(strategy_id=..., page_size=...)`; it accepts no search query or filters.

For a timeout, malformed response, or `invalid_backend_response`, acceptance is uncertain even
when the error says `retryable=false`; the backend may already have created and started the Run.
Reconcile any exact returned identity. If none was returned, inspect
`list_strategy_backtests(strategy_id=...)` for the original immutable Strategy and read an exact
candidate with `get_strategy_backtest`. Compare retained creation time and execution choices with
the original request. Use bounded repeated reads when the first page has not yet exposed the Run.
If attribution remains uncertain and the original call carried `client_request_id`, a bounded
retry with the exact same ID and parameters safely recovers the original operation. Never
use a fresh ID or change parameters to recover an uncertain submission. If the original call
omitted the ID, retain read-only reconciliation and report remaining uncertainty; do not pick a
merely similar Run as proof.

Preserve safe failure details and retryability. A rejected request is not a completed backtest.
A requested rerun uses a fresh `client_request_id`, even for identical dates and a completed
or still-running previous Run (normal quota/concurrency limits still apply). The same ID is
reserved for retries, including after reconnection or more than ten minutes. A response with
`idempotency_key_reused` means that ID was used with different parameters; report the conflict
and reconcile the original operation, rather than silently generating another ID.
The field is an operation identifier, not part of the Strategy definition or Run parameters.
Its omission exists only for old-client compatibility and cannot reliably express an identical
intentional rerun on modern MCP. If the live schema lacks the field, report the connection's
schema limitation rather than inventing it or forcing another request.

An authorized rerun submits a new Run of the same Strategy; changing a frozen definition requires
an authorized new Strategy first. Do not repeat failed execution merely to manufacture evidence.

Read `get_strategy` for immutable composition/specification and the Run for execution state.
Use available server artifacts for effective execution parameters; preserve missing fields as
unknown. A terminal zero-order/no-result outcome is not a reason to keep polling missing charts.
