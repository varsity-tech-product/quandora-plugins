---
name: portfolio-trading-analysis
description: Manages Simulation accounts and runs and analyzes actual forward-test evidence for Simulation and real Live portfolios. Use when the user asks to create, rename, archive or restore a Simulation account, start/pause/resume/stop a simulated run, or analyze observed trading performance, execution and research divergence. Do not use to create or control real Live accounts or author backtest research.
---

# Portfolio Trading Analysis

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery and the once-per-session release check; preserve existing update authority.
Follow [Research intent and evidence](../../references/research-workflows.md) for backtest/forward
scope, capability-aware conclusions and authorization-preserving handoffs.

Use the authenticated `quandora` MCP connection for Simulation account management,
monitoring and read-only real Live account inspection. Canonical `monitoring` and `simulation`
are non-executing; legacy `paper`/`live` modes are aliases for these simulated modes and never
mean real-money execution. Their historical `execution_enabled=false` and
`execution_status=not_configured` do not describe real Live accounts. Real Live is a separate account-oriented read-only MCP surface.

Route Strategy authoring/backtests to `$strategy-building`, Portfolio creation/sharing to
`$portfolio-building`, Portfolio backtest diagnosis to `$portfolio-analysis`, and completed single-Strategy diagnosis to `$strategy-analysis`.
A single Strategy starts through a one-component Portfolio. Carry the existing user request and
authorization through this handoff; do not reset the task or require redundant confirmations.

Use only the configured MCP connection. Never request secrets or bypass MCP with internal HTTP.
Let the host resolve server-qualified tool names; recover missing actions through the shared policy.
For named objects, follow [Name discovery](../../references/object-discovery.md) to resolve exact identities.

## Intent and Forward Analysis

For analysis-only requests, remain read-only. For explicit Simulation management, use the
matching account/run operation; a risk finding alone does not authorize a stop or account edit.
Use [Forward-test analysis](references/forward-test-analysis.md) to evaluate the frozen definition,
actual observation window, operational quality, net performance and deviation from research.
A historical OOS backtest is not forward evidence. New definitions start separate validation
segments. Share/publication management belongs to `$portfolio-building`.

## Canonical Tools

- `create_and_start_simulation_account`, `get_simulation_account_operation`,
  `continue_simulation_account_operation`: durable creation and recovery.
- `list_simulation_accounts`, `create_simulation_account`, `start_simulation_account_run`:
  account inventory and lower-level creation/start.
- `rename_simulation_account`, `archive_simulation_account`, `restore_simulation_account`.
- `pause_portfolio_trading_run`, `resume_portfolio_trading_run`, `stop_portfolio_trading_run`.
- `start_portfolio_trading_run`: compatibility start for an owned Portfolio; follow current schema.
- `list_live_accounts`, `get_live_account`, `list_live_account_runs`, `get_live_account_run`,
  `get_live_account_facts`: real Live reads only.
- `list_portfolio_trading_runs`, `get_portfolio_trading_run`: persisted lifecycle snapshots.
- `list_portfolio_trading_signals`: persisted signal targets and observations.
- `get_portfolio_net_snapshot`: authoritative Monitoring/Simulation net book and current positions.
- `list_portfolio_net_equity_points`, `list_portfolio_net_fills`,
  `list_portfolio_net_position_cycles`: available net equity, fills and position-cycle history.
- `list_portfolio_trading_position_snapshots`: retained legacy member observations only; never net finance.
- `list_portfolio_trading_equity_points`: persisted equity, balance, PnL, fees and funding.
- `get_portfolio_trading_equity_curve`: bounded return curve and whole-run UTC daily risk.
- Use `get_quandora_guidance` with `operation.paper_trade.submit` only to resolve a relevant
  schema or workflow uncertainty, not as a required probe before each operation.

Research creation and backtests belong to `$strategy-building` and `$portfolio-building`.
`get_portfolio_backtest` is a read-only prerequisite for resolving an automatic Paper association.

## Account ROI and individual Run performance

For account balance or cumulative account ROI, use `get_simulation_account_performance(account_id)`
or `get_live_account_performance(account_id)`. These also work when no Run is active.
For one execution, use `get_portfolio_trading_run_performance(portfolio_trading_run_id)` or
`get_live_account_run_performance(account_id, run_id)` with the exact trading execution ID.
Read [Account and Run metrics](references/account-run-metrics.md) before interpreting these fields.
The old Live `get_live_account_facts(section="performance")` is still Run-scoped, never Account ROI.
If a new tool is unavailable, follow connection recovery; report unavailable performance rather
than substituting legacy ROI, summing Runs or calculating from a first observed snapshot.

## Automatic Paper from a Backtest

When the task follows Portfolio research, read the exact `portfolio_run_id` with
`get_portfolio_backtest`. Use `run.automatic_paper.portfolio_trading_run_id` to read the existing
run with `get_portfolio_trading_run`; the Portfolio association is authoritative even if other
Paper runs exist for that Portfolio. Preserve provisioning `status` and `source_portfolio_run_id`.
Do not require a new capital choice or call start merely to observe this automatic run.

Raw Factor inputs remain governed by the Factor Plugin Contract before they reach Portfolio
Trading. This Skill must not copy the `binance_intraday` field registry, realign the D feature row
to D+1, shift it again, backfill a missing row, or treat the pre-00:02 UTC publication SLA as an
arrival guarantee. Trading consumes the frozen Portfolio/Strategy contract and reported runtime
observations. Paper validates every required history column and bar before Lean execution; missing
required data retries or fails the run according to the runtime deadline and does not silently
filter that symbol into a smaller universe. The 12 first-seven-day bucket exclusions are default
Factor recommendation guidance, not a Paper runtime fallback; `trade_vol_max_b` and
`trade_vol_max_s` are not in that exclusion set.

A null association or TradingRun ID means provisioning is absent or incomplete. Preserve
pending/retrying/failed states, use bounded reads, and report unresolved provisioning. It is not
permission to create a replacement. An explicit request for an additional run uses the start
workflow below with PB-managed virtual capital. Existing task authorization survives handoffs.

## Create, Start and Manage Simulation

Follow [Simulation management](references/simulation-management.md) for explicit creation,
start, rename, archive, restore, pause or resume requests. Preserve `portfolio.portfolio_id` for
owned sources. Internal command IDs are not public selectors. Reuse the same `client_request_id`
and recover the existing durable operation after an uncertain response; never create a replacement.
Account quotas, eligibility, grants and settlement remain server-owned.

## Real Live Is Read Only

Start from `list_live_accounts`, then `get_live_account(account_id=...)` for the selected account
and its current Run. Use `list_live_account_runs` for history and `get_live_account_run` or
`get_live_account_facts` with that account ID and, when needed, an exact historical `run_id`.
The server binds every Run to its account and owner. Facts sections are `positions`, `orders`,
`fills`, `performance`, and PB daily risk `statistics`; select the section needed to answer the user's question.

Preserve real status, `BLOCKED` reasons, nullable capital and provider/collection timestamps.
Accepted or starting is not running; stopping is not stopped. An empty list or missing value
is not evidence of zero positions or zero balance. Reads must not prepare, preflight, refresh
authorizations, start or stop a Run. Account creation, credentials, preparation, capital estimation,
start, stop, closing positions and all other Live changes are frontend-only. Never call cached
Live write tools or work around their removal. Explain the frontend action when the user asks
for a Live change, while continuing any authorized read-only inspection.

## Read Observations

Use `list_portfolio_trading_runs` for a bounded owner inventory. Canonical Trading lists support
`page_size`/`page_token`; do not send `query` or `filters` to these tools. Copy tokens byte-for-byte
with the same run and page size. An empty page does not prove an account has zero positions or PnL.

Choose only the relevant collection. Signals describe targets and deltas, not fills. Use the
net-ledger tools for current Monitoring/Simulation finance and positions. Preserve READY/WAITING/
INCOMPLETE and valuation timestamps; do not sum legacy member snapshots into a net account or
multiply ENTRY_NOTIONAL returns by leverage again. Legacy snapshots describe member observations. Equity points preserve returned decimal values,
cycle IDs and timestamps. Do not fabricate execution, merge observations from different cycles
into a single account snapshot, or compute current PnL from stale or missing data. These reads
use persisted observations and do not trigger account refreshes.

The Trading run response may not include components. Use the known immutable Portfolio handoff
for composition; never infer components from nearby records or invent a missing field.

## Return Curve and Daily Risk

Use `get_portfolio_trading_equity_curve` with the exact `portfolio_trading_run_id`
and one `lookback`: `7D`, `30D`, `90D`, `180D`, `1Y`, or `3Y`. Use `30D` when the
user asks for a recent curve without a period. Do not send raw-equity cursors or
owner/Share overrides. The returned `curve` binds its run and lookback.

`series[].value` is a return ratio: `0.10` means 10%, not 0.10 USDT. Preserve
`interval` and `total_points`; the series is bounded and may be sampled.
For raw balance, fees or funding observations, use `list_portfolio_trading_equity_points`.
Do not recompute whole-run risk from one page or the displayed curve.

The curve uses each observation's `as_of`, not its later `captured_at`, and excludes observations
before the Run's `created_at` or after its authoritative terminal time. A raw equity row can
therefore exist while the curve is empty, for example when the first scheduled cycle predates
the Run. Preserve both timestamps; do not relabel collection time as observation time or
manufacture a curve point. A newly created Run has no completed UTC day yet.

`daily_max_drawdown_pct` is a signed nonpositive percentage (`-25.00` means a 25%
decline). PB calculates it over the whole authorized Run using the last valid
observation of each completed UTC day (`utc_daily_close_v1`). It is independent of
the selected chart lookback. Preserve `daily_max_drawdown_peak_at`,
`daily_max_drawdown_trough_at`, `daily_observation_count`, and
`missing_daily_observation_count`. A null peak time can denote the initial-capital
peak. Missing capital or daily observations means unknown risk, not zero drawdown;
do not fill missing days. Run list/detail return the same risk fields when available.
Older RPC-only reads may omit the whole extension; do not invent it.

The curve uses existing owner and cutoff authorization and is unavailable when the
shared projection is unavailable. Preserve that result without provider/API fallback.
It does not imply frozen historical versions of mutable observations.

## Stop

For an authorized stop, show the exact run and that stopping is terminal, then call
`stop_portfolio_trading_run`. A repeated stop is idempotent. Reconcile with
`get_portfolio_trading_run` if needed. Pause/resume are separate Simulation operations.
This stop tool never authorizes stopping a real Live account.
Ask for approval only when the user has not already authorized stopping that run.

## Historical Observations

Use the current canonical Trading inventory and exact returned identities for any historical
records it exposes. Preserve nullable Portfolio IDs or capital and returned `runtime_source`;
do not invent migrated lineage or call removed historical tools. Unavailable historical details
stay unavailable; do not bypass MCP with a provider API or construct another run.

## Final Response

State the account/run family, exact identity, lifecycle, and observation freshness. For real
Live, describe only returned state and any freshness limits. Distinguish research metrics from observed
Trading values and historical Paper values.
Use the user's language while preserving tool names, schema fields, and returned identifiers.
