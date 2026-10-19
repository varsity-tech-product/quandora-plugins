---
name: strategy-building
description: Builds one non-optimizer Quandora Strategy and lists available, eligible, or selectable factors. Use when the user asks to create, revise, backtest, rerun, retrieve, or export that Strategy. Do not use for multi-Strategy Portfolio composition, Paper execution, or deep diagnosis.
---

# Quandora Strategy Building

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery and the once-per-session release check; preserve existing update authority.
Follow [Research intent and evidence](../../references/research-workflows.md) for backtest/forward
scope, capability-aware conclusions and authorization-preserving handoffs.

Use the authenticated `quandora` connection for one canonical lifecycle:
StrategyFolder → immutable Strategy → StrategyRun. Creating a definition and submitting its Run
are distinct calls within the same authorized task. There is no alternate ad-hoc submission path.

Route one to five exact Strategies to `$portfolio-building`, simulated execution and observation
to `$portfolio-trading-analysis`, and diagnosis of existing results to `$strategy-analysis`.

For archive waits, stale `sync_failed`, inline `too_large`, or bundle channel limits,
follow [Strategy delivery recovery](../../references/strategy-delivery-recovery.md).
For named objects, follow [Name discovery](../../references/object-discovery.md) to resolve exact identities.

## Tools

- Factor selection: `get_strategy_capabilities`, `list_eligible_strategy_factors`,
  `get_eligible_strategy_factor`.
- Folders: `create_strategy_folder`, `list_strategy_folders`, `get_strategy_folder`.
- Immutable definitions: `create_strategy`, `list_strategies`, `get_strategy`.
- Runs: `submit_strategy_backtest`, `list_strategy_backtests`, `get_strategy_backtest`.
- Export: `download_result_bundle` with `kind: "strategy"` and the canonical StrategyRun ID.

These are canonical actions on the configured MCP dependency. Let the host resolve its qualified
names. Missing tools do not authorize aliases or direct internal HTTP. Use `get_quandora_guidance`
only when the current schema leaves a relevant workflow detail unclear; it is not an entry gate.

## Route and Execute

For a bare factor-list request, call only `list_eligible_strategy_factors` with one bounded page.
Use a supplied name as `query`, exact supported constraints as `filters`, and preserve the opaque
page token byte-for-byte. Do not start research or auto-page from an inventory request.
Preserve returned `strategy_use` and `unresolved_factor_ids`; an explicitly included Factor can
appear with `strategy_use.status=needs_optimization` and is not selectable merely because it is
listed. Report that state without adding local grade thresholds or silently substituting Factors.

For a Strategy request, follow [Canonical Strategy Workflow](references/ordinary-strategy-workflow.md).
Resolve exact admitted Factors, prepare one named immutable definition, create its Folder if
needed, then submit a Run with a fresh `client_request_id` when requested. A request to build and backtest covers both calls;
do not add a confirmation at each step or Skill handoff. Ask only for unresolved material choices
or authorization. Never upload a local plugin directly to Strategy: use `$factor-mining`, finish
its canonical Factor backtest/admission, then select the admitted Factor here.

The Factor Plugin Contract owns raw input definitions, including `binance_intraday` semantics and
D/D+1 availability. Strategy construction consumes exact admitted Factor identities; it must not
copy the 86-field semantic registry or reviewed research policy, select raw data columns,
re-normalize a Factor's inputs, or apply an
additional date shift. Route a request to author or change an input-level thesis to
`$factor-mining` before returning to the eligible Factor inventory.

For a changed definition or another Run of an existing Strategy, follow
[Immutable Definition Changes](references/canonical-strategy-workflow.md).

## Observe and Deliver

Copy `run.strategy_run_id` from submission and read it with `get_strategy_backtest`.
For history, `list_strategy_backtests` requires the exact `strategy_id`. Folder and Run lists use
`page_size`/`page_token`; they do not accept `query` or `filters`. Definitions in a Folder are read
with `list_strategies(strategy_folder_id=...)`. Preserve the returned identities and states.

An ambiguous write is not permission to submit a replacement or change its payload. In particular,
`invalid_backend_response` after submit leaves acceptance uncertain even when `retryable=false`:
the Run may already exist. Read `list_strategy_backtests` for the original immutable `strategy_id`
and reconcile any exact returned Run with `get_strategy_backtest`; do not use an internal command
ID or treat a merely similar Run as proof. Allow bounded reads for delayed visibility, then report
remaining uncertainty. When the original submission included `client_request_id`, a bounded retry
with that same ID and identical parameters recovers the same operation; never replace an uncertain
submission with a fresh ID. Without the original ID, keep reconciliation read-only.
A definitive `factor_needs_optimization` rejection identifies the affected Factors in
`error.details.factor_ids`. Report those returned IDs and the reason. Do not retry the same
rejected input, silently remove or substitute Factors, or infer that the rejection created a Run.
Continue Factor repair only within the user's authorized scope, then use newly admitted evidence.
A failed Run remains historical evidence. A requested rerun calls `submit_strategy_backtest`
for the same immutable Strategy with a fresh `client_request_id`; a changed definition must first
create a new Strategy. Generate the ID before submitting, preserve it across retries, and never
reuse it with different dates or a different Strategy.

After a terminal Run and a readable archive, use
[Strategy Result Bundle Delivery](references/result-bundle-delivery.md) for requested export.
The default completed local path is `Quandora result/strategy/<strategy_slug>.zip`.
Analysis uses server artifacts through `$strategy-analysis`; a local ZIP is not a prerequisite.

For Trading preparation, hand the exact Strategy to `$portfolio-building` for a one-component
Portfolio. After its backtest, PB automatically provisions Paper; the Portfolio workflow returns
the exact association for `$portfolio-trading-analysis` to read. Do not start an extra TradingRun here.

## Final Response

State the Strategy name, Folder/definition/Run identities when useful, observed Run/archive state,
safe diagnostics, and verified export path when saved. Preserve missing evidence as unavailable.
Use the user's language while preserving tool names, schema fields, and returned identifiers.


## Library Favorites

For Factor/Strategy stars and folder-independent metadata, follow
[Library Favorites](../../references/library-favorites.md).
