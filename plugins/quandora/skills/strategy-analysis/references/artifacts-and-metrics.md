# Strategy Artifacts And Metric Semantics

Apply each artifact's declared schema and window. Missing or null values remain unavailable.

## Primary Evidence

- `get_strategy_backtest` provides Run state and its exact immutable `strategy_id`.
- `get_strategy` provides `strategy.specification` and ordered `strategy.factor_references`
  for the frozen definition; retained artifacts provide effective execution parameters.
- `get_strategy_backtest_artifact` with `summary` and `performance` provides headline result metrics.
- Equity and drawdown curves show path dependence, concentration, and recovery.
- Turnover and exposure curves show implementation intensity and neutrality through time.
- Attribution and signal-return curves can support mechanism claims only when actually included.
- Orders and trades are execution evidence, not substitutes for the canonical run snapshot.

Artifacts and analysis data return weekly level curves by default (monthly beyond two years);
returns, turnover and other per-period series stay daily. Request `resolution: "daily"` only when a
daily detail decides a claim, and `format: "columnar"` for tables. Request analysis-data pages of
at most 200 points; a 500-point daily decile page is about 70,000 characters.

For an owned Run, read the tested hypothesis and targets with `list_research_notes` using the
Run's `strategy_version` (its `strategy_id`) as `subject`. It returns the version's own notes and
the notes about each of its Runs, which carry `run_id`; use the version-level notes and those whose
`run_id` is the analyzed Run. End with `record_research_conclusion` on that `strategy_run`; the
server files it under the version with `run_id`. Publication evidence has no notebook entry.

## Return And Drawdown

- Compare return, Sharpe, Sortino, drawdown, and fees over the same declared period.
- Rank two Strategy versions only on Runs with the same exchange and window. When they differ,
  state the difference instead of ranking them.
- Treat a signed negative drawdown as a loss from peak; name the sign convention when reporting it.
- A high return with concentrated time contribution or slow drawdown recovery is less robust than
  an evenly distributed path with the same headline return.
- Funding cash flow, when present, is signed received-minus-paid and remains separate from total
  fees. Do not apply it to equity a second time.

## Strategy Turnover

- Strategy daily turnover is single-sided: `sum(abs(delta weight)) / 2`.
- Factor cross-sectional turnover uses a different convention without `/2`. Name the convention
  before comparing the two.
- Interpret turnover with rebalance bars, modeled fees, signal persistence, and realized breadth.

## Composition

- Read selected Factors from `strategy.factor_references` returned by `get_strategy`: each names the
  Family `factor_family_id`, the immutable Factor `factor_id` and its evidence run `factor_run_id`.
- Read weighting from `strategy.specification.weighting`: `mode: equal` means equal Factor
  weighting; `mode: custom` uses the returned `weights` in Factor-reference order.
- Read actual Top/Bottom selection from `strategy.specification.ranking`, and direction and
  rebalance choices from that same immutable specification. Missing fields stay unknown.
- Do not expect a Run-level `composition` or `parameters.ranking` wrapper.
- The factor list alone does not prove each factor's marginal contribution.
- Do not infer correlations, ablations, or standalone factor quality from Strategy-level returns.

## Scope Labels

- `IS` means in-sample.
- `OOS` means a separately declared out-of-sample scope.
- `ALL` combines available scopes and includes IS; it is not pure OOS.
- Always report the exact artifact label and window rather than upgrading the scope in prose.
