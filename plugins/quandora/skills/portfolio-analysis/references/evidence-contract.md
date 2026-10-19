# Portfolio evidence and comparable results

Read `get_portfolio_backtest` for one exact persisted run, including its actual source StrategyRuns,
and `get_portfolio` for the immutable composition. `get_portfolio_backtest_result` owns the
aggregate result: `pending` is not ready; `unavailable` is failure evidence; only `ready` is a
readable aggregate. Preserve nullable evidence and safe returned error fields.

Canonical summary fields include `net_profit_pct`, `annual_return_pct`, `annual_std`, `sharpe`,
`sortino`, `max_drawdown_pct`, `start_equity`, `end_equity`, and available fees/funding. The curve
uses `equity_curve.points[].t` and `equity_curve.points[].value` for time and normalized equity.
Percentage-suffixed metrics use percentage units; `annual_std` is annualized standard deviation.
Apply each declared convention, including drawdown sign, rather than copying Trading conventions.
Portfolio normalized research capital is not an executed account balance.

Research benchmark evidence comes from the same result: `benchmark_symbol`, `benchmark_readiness`,
`benchmark_curve`, `benchmark_return`, `tracking_error`, and `information_ratio`. BTCUSDT research
benchmark identity is separate from `trading_benchmark_symbol`. `benchmark_return` is a ratio
and the benchmark curve is normalized equity. Keep benchmark readiness independent of aggregate
readiness; never fetch replacement prices or present missing metrics as zero.

Initial capital weights do not imply periodically restored sleeve weights. Actual member source
Runs and their initial-cash normalization are authoritative. Do not average member Sharpe or
drawdown to construct Portfolio metrics, infer joint statistics from headline numbers, or use
theoretical fixed-weight arithmetic as the realized Portfolio result.

Only compare full-run member metrics when their interval, frequency, valuation, units, cost and
exposure assumptions are actually comparable with the Portfolio interval. A source can extend
beyond the Portfolio's aligned interval. Without a supported same-window projection, do not use
its full-run summary as a like-for-like control. State that the comparison is unavailable.
Clipped curves alone do not establish clipped fees or funding, and missing costs remain missing.

For owner member evidence follow the exact `components[].strategy_run_id` returned by the
PortfolioRun into Strategy Analysis. Preserve `preparation_strategy_run_id` and preparation
status separately; an unresolved source is not permission to substitute that Strategy's latest
run. The legacy Paper source selector `source_strategy_run_id` is a different tool contract.
For Community use the exact Publication root and returned child identities for each contextual
read, and copy artifact names, offsets and digest from the response. For Shares preserve their
current read authorization and returned source-free evidence. Never copy third-party objects into
Mine, fetch restricted source, or use local exports to evade a read projection's limits.

For explicit owner export, call `download_result_bundle` with `kind: "portfolio"` and `id`
set to the exact immutable PortfolioRun. Follow
[Unified Result Bundle Download](../../../references/result-bundle-download.md).
Do not assemble authoritative research from an export or print short-lived download URLs.
Exports are optional transport.
