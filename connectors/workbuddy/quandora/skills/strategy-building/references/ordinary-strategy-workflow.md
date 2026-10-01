# Ordinary Strategy Workflow

Load this reference after routing to a single ordinary cross-sectional Strategy.

## Capabilities and Factor Selection

For a bare available-factor request, call only `list_eligible_strategy_factors`: one page of 10 by
default, or one explicitly requested page from 1 through 100. Do not auto-page or call Factor
Mining inventory/status.

For composition, call `get_strategy_capabilities` once. Its `contract` is the request boundary and
`product_defaults` explains omission behavior. The canonical
`submit_adhoc_strategy_backtest` caller fields are `name`, exactly one of `factor_ids` or
`factor_weights`, `ranking`, `strategy_type`, dates, cash, fee rates, `rebalance_bars`, and
`attribution`. Stop on any contract/schema mismatch; never send semantic, response-only,
local-only, universe, or idempotency fields.

Every selected Factor must be returned by `list_eligible_strategy_factors`. Display returned ID,
name, Task category, rating/grade status, Source, and CS Sharpe when present. Classify Source only
from `source_kind` and `shared`: Official, Mine, Shared, or Unavailable. Ratings do not determine
eligibility; Grade F remains selectable when returned as eligible.

Use `get_eligible_strategy_factor` only for a requested exact Factor or a small stated shortlist.
Ask the user to select unless they explicitly delegated selection.

For Shared candidates, call `list_shared_strategy_factor_candidates`. Before
`admit_shared_strategy_factor`, show and confirm the exact candidate, FactorVersion, and root-level
Factor backtest evidence. Then require the admitted Factor to appear in the eligible inventory.

An agent-mined/authored Factor follows the eligible inventory and is never re-imported. The
`import_strategy_factor` branch is allowed only for a complete external `plugin.py` supplied by the
user, explicitly requested for import, and supported by the current host schema. It requires a real
current-owner session and the approved import guidance; never invent lifecycle identifiers.

## Payload and Confirmation

For equal weights use distinct `factor_ids`; for custom weights use distinct positive finite
entries totaling 1 within the contract tolerance. Validate finite numeric values, ranking,
direction, dates, cash, fees, and rebalance bounds against the current contract. Preserve explicit
choices and omit optional fields the user did not choose.

Choose the submitted name from a valid user name or the exact selected Factor themes and effective
configuration. Before `submit_adhoc_strategy_backtest`, show the complete safe name, factors or
weights, ranking, direction, dates, capital, fees, rebalance, and attribution, then obtain explicit
confirmation.

Call the mutation once. Store only returned `result.run.id` as the Strategy run handle.
`result.run.strategyId`, Factor IDs, rating provenance, and FM identifiers are not substitutes.
An ambiguous response without a handle does not authorize resubmission.

## Observation and Failure

The submit response is the first snapshot. For a non-terminal run, wait 30 seconds and call
`continue_strategy_backtest` at most twelve times. It re-drives work; do not interleave
`get_strategy_backtest`. If still running, report it and stop before archive/bundle work.

After terminal status, observe archive state with the same run using at most five
`get_strategy_backtest` calls separated by 30 seconds. Request a Result Bundle only after archive
state is completed or partial.

`resultOutcome={status:"no_result",reasonCode:"zero_orders",orderCount:0}` is successful execution
with no orders and no performance/Paper eligibility. Do not continue or rerun it to manufacture
evidence.

For a failed terminal run, safe diagnostics and `fmRetryable` are advisory. A compile/Lean failure
or false/absent retryability means repetition risk, not a prohibition. Use
`rerun_strategy_backtest` only after the user requests a rerun, the exact failed source has FM run
and immutable StrategyVersion lineage, the repetition risk is shown, and a separate explicit
confirmation is obtained. Call it once; never resume the failed source or rebuild a new payload.
