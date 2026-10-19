---
name: portfolio-building
description: Selects complementary Strategies and builds, revises or backtests an immutable Quandora Portfolio, including one-member Portfolios. Use when the user asks for a composition plan, capital weights, creation, Community discovery, favorites, publication or sharing. Do not use for single-Strategy authoring, deep diagnosis of an existing Portfolio result or Trading account management.
---

# Portfolio Building

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery first and version diagnostics on demand; involve users only when unavoidable.
Follow [Research intent and evidence](../../references/research-workflows.md) for backtest/forward
scope, capability-aware conclusions and authorization-preserving handoffs.

Use the authenticated `quandora` MCP connection for
PortfolioFolder → immutable Portfolio → PortfolioRun. Route Strategy authoring to
`$strategy-building`, single-Strategy diagnosis to `$strategy-analysis`, Portfolio result diagnosis to
`$portfolio-analysis`, and Trading lifecycle
and observations to `$portfolio-trading-analysis`. A one-component Portfolio supports one Strategy.
Carry the user's goal and existing authorization through these handoffs.
The MCP tools reach Product Backend (PB); PB owns the product response and coordinates FM.
Use PB-returned states and research evidence throughout this workflow.
For named objects, follow [Name discovery](../../references/object-discovery.md) to resolve exact identities.

## Tools

- Folders: `create_portfolio_folder`, `list_portfolio_folders`, `get_portfolio_folder`.
- Immutable definitions: `create_portfolio`, `list_portfolios`, `get_portfolio`.
- Runs: `submit_portfolio_backtest`, `list_portfolio_backtests`, `get_portfolio_backtest`,
  `get_portfolio_backtest_result`.
- Shares: `list_portfolio_shares`, `get_portfolio_share`, `get_portfolio_share_research`,
  `create_portfolio_share`,
  `download_result_bundle` (`kind: "portfolio_share"`), `get_portfolio_sharing`,
  `search_portfolio_share_recipients`, `share_portfolio_with_user`, `publish_portfolio_to_community`,
  `extend_portfolio_share`, `update_portfolio_share_intro`.
- Community and favorites: `list_community_portfolios`, `get_community_portfolio`,
  `get_community_portfolio_research`, `get_community_strategy_research`,
  `get_community_factor_research`, `read_community_research_artifact`,
  `set_portfolio_favorite`, `list_favorite_portfolios`.

Use `get_quandora_guidance` for `operation.portfolio.manage` only when a relevant detail
is unclear. Missing tools do not authorize aliases, alternate services, or internal HTTP.
Never request credentials; recover connection failures through the shared policy.

## Route Selection, Design and Execution

Use [Selection and weighting](references/selection-and-weighting.md) when the user delegates
member choice or asks for a design. Reuse `$strategy-analysis` Strategy Cards and the shared
[neutrality framework](../../references/portfolio-neutrality.md), with missing evidence explicit.
For design-only requests, return the proposed members and weights without creating or submitting.
For exact supplied members and weights, validate and execute that intent without forcing a full
selection study. Research uncertainty is not an additional product eligibility gate.

Freeze the goal, actual candidate scope, selection reasons, initial weights and intended baseline.
Do not default to in-sample maximum-Sharpe weights or claim global optimality. A same-member equal-
capital or leave-one-out control is a separate experiment requiring existing authorization.
After a requested backtest, use `$portfolio-analysis` for an evidence-based historical verdict.

## Discover and Compose

`list_portfolio_folders` accepts `page_size`, `page_token`, and `include_archived`.
It does not accept `query` or `filters`; select from the returned names without inventing search
arguments. Include archived folders only when requested. Copy continuation tokens byte-for-byte.
Use `list_portfolios(portfolio_folder_id=...)` for immutable definitions in an exact Folder.

Resolve one to five distinct exact immutable `strategy_id` values. If a needed Strategy does not
exist, continue its authorized preparation through `$strategy-building`.
For equal initial capital weights, omit every `target_weight`. For custom weights, supply a
positive decimal string for every component with an exact sum of 1, for example `"0.7"` and
`"0.3"`. Never mix supplied and omitted weights, use exponent notation, or round automatically.
These allocate initial capital between Strategies; they are not Factor signal weights, leverage,
or daily rebalancing instructions. Changing weights creates a new immutable Portfolio and does
not alter historical backtests or running accounts. Research normalizes capital to 100000;
do not send cash, dates, fees, leverage, or source-run overrides to Portfolio backtesting.

Raw Factor inputs remain governed by the Factor Plugin Contract. Portfolio composition consumes
immutable Strategies and must not copy the `binance_intraday` field registry, reinterpret D/D+1
availability, re-normalize Factor inputs, or shift source timestamps. FM-owned source preparation
must preserve the retained StrategyRun evidence. Default Paper-ready bucket exclusions are Factor
research guidance, not permission for Portfolio or Paper to drop symbols with missing required
history.

For a new Folder call `create_portfolio_folder` with optional `name` and
`components: [{"strategy_id": "<exact Strategy ID>"}, ...]`. Copy
`portfolio_folder.portfolio_folder_id` and `portfolio.portfolio_id` from the response.
For changed components in an existing Folder, read the exact base with `get_portfolio`, then call
`create_portfolio` with `portfolio_folder_id`, `base_portfolio_id`, and the complete component list.
This creates an immutable Portfolio; no Folder ID or Run ID substitutes for its `portfolio_id`.

Present consequential selections and proceed within existing authorization. Do not add approvals
between definition, backtest, and automatic Paper observation. An ambiguous response requires
reconciliation with exact returned identities, not a replacement definition or submission.

## Backtest and Read Results

Call `submit_portfolio_backtest` with the immutable `portfolio_id` for the requested
backtest or rerun. Follow the current schema for any user-selected `exchange`; otherwise preserve
the server default. Do not add fields absent from that schema. PB requests the latest available closed monthly
data. FM prepares sources starting on 2022-01-01, resolves the actual latest data endpoint,
and reruns missing or stale StrategyRuns before aggregating their actual aligned interval.
Leave dates omitted; do not insert a remembered month-end or pre-submit component Runs locally.
This source preparation is part of the requested backtest. Preserve returned `command_kind`,
`target_data_through`, `start_date`, and `end_date` without inventing unresolved dates.
The returned `run.portfolio_run_id` identifies a
durable accepted Run, including when its status is `preparing_sources` and component StrategyRun
identities are not yet resolved. Read that exact Run using `get_portfolio_backtest` as it moves
through `preparing_sources`, `running`, and terminal `completed` or `failed`. FM resumes accepted
preparation; do not submit again to advance it. Use `list_portfolio_backtests(portfolio_id=...)`
for persisted history, with bounded page size and unchanged continuation tokens.

A timeout, malformed response, or `invalid_backend_response` leaves acceptance uncertain even
when `retryable=false`. Recover through the exact Portfolio's persisted history and any returned
Run identity; do not choose a merely similar Run or submit a replacement. Do not resubmit
automatically for `source_result_evidence_unavailable`; preserve the bounded failure evidence.
A definitive `factor_needs_optimization` rejection identifies affected source Factors in
`error.details.factor_ids`. Report those IDs and the reason; do not retry unchanged inputs,
silently replace components, or infer that the rejected submission created a Run. Continue
authorized Factor/Strategy repair through the corresponding Skill, preserving immutable identities.
The same submit tool covers latest-data reruns; there is no separate latest-data tool,
public explicit-source selection, or compatibility-list step.

Read `get_portfolio_backtest_result(portfolio_run_id=...)` after a terminal Run, including a
failed Run, to obtain its persisted result or failure. `pending` is not a
completed result; `unavailable` is failure evidence; only `ready` is a readable aggregate. Preserve
`summary.net_profit_pct`, `annual_return_pct`, `annual_std`, `max_drawdown_pct`, `start_equity`,
`end_equity`, and other returned metrics, along with `equity_curve.points[].t` and
`equity_curve.points[].value` as the timestamp and normalized equity.
Percentage-suffixed metrics are percentages; `annual_std` is annualized standard deviation.
These are normalized research results, not executed orders or a Trading account balance.
For failures, show the returned safe `error.code`, `error.message`, and `retryable` when present.
If failure detail is absent or unavailable, say so; do not invent a diagnosis or retry permission.

Read research benchmark evidence from that same PB result: `benchmark_symbol`,
`benchmark_readiness`, `benchmark_curve.points[].t`, `benchmark_curve.points[].value`,
`benchmark_return`, `tracking_error`, and `information_ratio`. The research benchmark is BTCUSDT;
the immutable Portfolio's `trading_benchmark_symbol` is a separate Trading choice.
`benchmark_return` is a ratio (`0.20` means 20%); the benchmark curve is normalized equity.
Keep pending/unavailable benchmark evidence and nullable metrics explicit even when the Portfolio
result is ready. Do not fetch substitute prices, fill missing points, average component risk,
or assemble authoritative metrics or benchmark results locally. Never supply demo values.

## Read Automatic Paper First

PB automatically provisions Paper after the Portfolio backtest. Read
`get_portfolio_backtest` → `run.automatic_paper` and preserve its `status`,
`source_portfolio_run_id`, and exact nullable `portfolio_trading_run_id`.
The association belongs to the immutable Portfolio and may refer to an earlier backtest of that
same Portfolio. It is authoritative even when other TradingRuns exist for that Portfolio.

Hand the exact non-null `portfolio_trading_run_id` to `$portfolio-trading-analysis` for existing-run reads.
A null association or pending/retrying/failed provisioning is not an instruction to call start.
Observe within the task's bounded wait and report unresolved provisioning with its canonical
Portfolio/Run identity. Starting an additional run requires an explicit separate Trading request.
Do not select a nearby run by date or replace the automatic run with a new start.

## Community and Sharing

Follow [Community discovery and sharing](references/community-and-sharing.md) for public or
specified-user sharing, active-grant extensions, intro edits, favorites and source-free reads.
These operations remain here; they do not require a new composition or backtest.

## Final Response

For a design, state proposed members, weights, reasons and evidence gaps. For execution, state
the exact composition, Folder/Portfolio/Run identities, preparation or backtest state,
research result, and automatic Paper association when returned. Keep research metrics separate
from Trading observations. Use the user's language and preserve schema fields and identifiers.
