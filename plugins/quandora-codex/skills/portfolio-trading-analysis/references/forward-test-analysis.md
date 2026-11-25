# Analyze an actual forward test

Use for Simulation or real Live analysis, not for an account-management-only request. Follow
[Research intent and evidence](../../../references/research-workflows.md). The workflow is
read-only; proposing a risk response does not authorize changing weights, starting another run,
pausing, stopping or closing anything.

## Identity and observation contract

Establish the account family, exact account/Trading Run, frozen Portfolio and available research
source identity, start time and observation cutoff. Legacy simulated mode aliases are not real
Live accounts. Changes to a definition or newly tuned versions form separate validation segments;
do not concatenate selected successful segments into one forward track record.

Historical OOS remains a backtest. Forward evidence must have actually occurred after the selected
definition was frozen and the run began. Preserve `as_of`, collection timestamps, readiness and
record coverage. Report how much history exists, including incomplete days, missing observations
and the available number of rebalance/execution events. Do not invent a minimum universal horizon.

## Net finance and execution

For balance and return, first follow [Account and Run metrics](account-run-metrics.md).
Use the canonical Account performance tool for cumulative account equity change/ROI,
and the exact Run performance tool for execution ROI, net PnL and NAV. The net ledger
below describes the selected Run's book, not cumulative account performance.

For Monitoring/Simulation use `get_portfolio_net_snapshot` for the authoritative current net book,
`list_portfolio_net_equity_points` for available net-equity coverage,
`list_portfolio_net_fills` for net fills and `list_portfolio_net_position_cycles` for cycles.
Preserve READY/WAITING/INCOMPLETE, exact decimal values and frozen-book valuation times. Do not
sum legacy member snapshots into account finance or apply leverage again to ENTRY_NOTIONAL returns.

For real Live use `get_live_account_facts` sections appropriate to the question, bound to the
exact owned account and selected run. Orders and fills are bounded recent records, not a full
historical export. Do not infer total fees, turnover or a complete trade distribution from them.

Distinguish signal targets, orders, fills, open/partially closed positions and settled cycles.
Partial closes do not mean a position is fully closed. Preserve net execution and cycle identities;
do not double count reversal fills or mix observations from different cycles into one snapshot.
Signal-versus-fill, latency, slippage or rejection analysis requires synchronized reference and
execution evidence. Without both, report the narrower observed state and missing evidence.

Use authoritative performance for PnL and return. Distinguish realized/unrealized values, fees and
funding, capital and any external flows. Balance changes alone do not prove investment return;
do not deduct costs again when the returned net figure includes them. State Simulation's modeled
execution assumptions and distinguish them from actual Live evidence.

## Diagnose risk and research divergence

1. **Operational quality:** lifecycle, data freshness, signals/targets, orders, fills and provider
   failures. Accepted is not running, stopping is not stopped, and empty is not necessarily zero.
2. **Observed risk/return:** use canonical net equity and available risk fields, long/short and
   gross/net exposure, concentration, costs and drawdown. Whole-run risk is not recomputed from
   a sampled display curve, a partial page or a different valuation convention.
3. **Research divergence:** separate market-state changes, possible signal decay, implementation
   costs and operational faults. Compare numeric results only with a supported same-window,
   comparable-definition/capital/exposure/cost control. No matching control means a qualified
   discussion of expectations and observed risk, not an invented backtest replay.
4. **Confidence:** distinguish short-run noise from persistent evidence. Recent profitability does
   not confirm long-term validity; recent losses do not alone establish failure.

Use Observed, Inference, Alternative and Experiment for consequential claims. Hand a requested
backtest diagnosis to `$portfolio-analysis`; authorized changes go through `$portfolio-building`
or the corresponding Strategy/Factor workflow, creating new immutable definitions as required.
No analysis-triggered rerun, retuning or account operation is implicit.

Return account/run identity and freshness, supported performance/risk, observed execution issues,
plausible explanations with gaps, and the smallest useful next investigation. A request to monitor
later requires an actually authorized scheduling mechanism; a current read does not establish
continuous monitoring or promise a future notification.
