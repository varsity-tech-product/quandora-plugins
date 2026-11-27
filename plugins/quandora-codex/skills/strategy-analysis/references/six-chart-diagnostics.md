# Six-Chart Diagnostics

Use `get_strategy_backtest_analysis_data` for retained six-chart numerical evidence. Start with `chart: "overview"`,
then request only the chart pages needed for the user's question. JSON null remains missing data.

## Adaptive Diagnostic Groups

Diagnostic grouping is separate from actual portfolio selection:

| Median daily cross-section | Quantiles | Minimum cross-section | Diagnostic top fraction |
| --- | ---: | ---: | ---: |
| at least 20 | 10 | 20 | 0.10 |
| 15 to 19 | 5 | 10 | 0.20 |
| 9 to 14 | 3 | 6 | 0.30 |
| below 9 | 2 | `max(2, min(4, median))` | 0.50 |

`Q1` is the lowest prediction group and `QN` the highest. Chart 1's return spread is
`(QN - Q1) / 2`. Read actual Strategy Top/Bottom selection from
`get_strategy` → `strategy.specification.ranking`, using the immutable `strategy_id` of the
selected Run. Factor composition comes from that Strategy's `factor_references` and
`specification.weighting`; chart parameters describe diagnostic groups, not the definition.

## Chart 1: Prediction Quantiles

- Look for ordered separation rather than only an extreme winning group.
- Compare the high and low tails and identify sign reversals.
- Small cross sections weaken apparent quantile smoothness.

## Chart 2: Style Long/Short Returns

- Each period, that day's diagnostic members are ranked by each style. Its return spread is
  half the difference between the highest and lowest style groups' mean forward returns. The
  plotted series is the running sum of these spreads.
- Check the underlying period returns for coverage. A flat cumulative line can include missing
  periods carried forward.
- Interpret only styles present in `params.styles`; use `missing_styles` as an evidence gap.

## Chart 3: Style Exposure

- The x-axis lists styles. Each bar summarizes the run window. For persistence or sign changes,
  use the dated `long_ts` and `short_ts` from the same run's `attribution` artifact when available.
- Identify the method from the retained chart title. "Equal-Weighted Basket Style Exposure"
  uses the backtest's selected long and short members. Each style is standardized across that
  date's market observations, averaged equally among valid members on each side, then averaged
  over that side's available dates. A positive short-side value means the short basket scores
  above the market average on that style.
- For this method, match chart `long`, `short`, and `long_short` to the card's `long_exposure`,
  `short_exposure`, and `long_short_exposure` by style key. Chart `beta_btc` maps to card
  `style_beta`. Use the published spread directly and preserve missing values on either side.
  The two views report one measurement. A discrepancy for the same run, window, and style
  should be reported with both values.
- "Mean Daily Style Exposure" charts summarize prediction-ranked tails using the
  basket-union-plus-BTC reference universe. Those summaries can differ from the card. If the
  retained evidence leaves the method unclear, report the chart's values with that limitation.
- For the updated basket calculation, raw Size is the log of the trailing 90-calendar-day median
  of positive daily quote volume plus open-interest notional (open interest × close). Days with
  missing open interest use quote volume alone. Use the declared convention for historical runs.

## Chart 4: Quantile Return Autocorrelation

- Compare the autocorrelation of the low-quantile, high-quantile, and long/short period returns
  across the retained `decay_lags`. This measures persistence of the return series. Assessing
  signal predictive power at longer horizons requires separate evidence.

## Chart 5: Prediction-Style Correlation

- Inspect sign, magnitude, stability, and missing periods for each style correlation.
- Correlation does not establish causality. Propose one controlled neutralization or stratification
  test when a style alternative is consequential.

## Chart 6: Daily Turnover

- Apply the returned or declared Strategy turnover convention; the standard retained projection is
  single-sided `/2`.
- Relate spikes to exposure changes, rebalance cadence, or regime transitions.
- Use the retained EMA only as a smoother; do not replace the raw series with it.

## Retained Numeric Projection

The overview projection includes `available`, `schema_version`, `generated_at`, `window`, `params`,
`cross_section`, `missing_styles`, and a six-chart catalog. Each paged chart response contains an
`x` axis page, named numeric-or-null `series`, a `plot` order, legend, colors, and metadata. Dynamic
quantile names, style names, and EMA suffixes are provider data; do not hard-code a series set beyond
the trusted response.
