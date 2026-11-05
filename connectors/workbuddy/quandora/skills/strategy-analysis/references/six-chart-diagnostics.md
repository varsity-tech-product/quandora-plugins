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

`Q1` is the lowest prediction group and `QN` the highest. Diagnostic spread is
`(QN - Q1) / 2`. Read actual Strategy Top/Bottom selection only from `get_strategy_backtest.parameters.ranking`.

## Chart 1: Prediction Quantiles

- Look for ordered separation rather than only an extreme winning group.
- Compare the high and low tails and identify sign reversals.
- Small cross sections weaken apparent quantile smoothness.

## Chart 2: Long/Short Style

- Compare style levels of the diagnostic long and short groups.
- A spread can be a style proxy even when return looks strong.
- Interpret only styles present in `params.styles`; use `missing_styles` as an evidence gap.

## Chart 3: Style Exposure

- Inspect whether style exposure is persistent, episodic, or changes sign.
- A stable exposure can explain persistent performance but also reduce incremental alpha.
- Size currently means the logarithm of trailing 90 natural-day median positive quote volume. It is
  not open-interest notional.

## Chart 4: Prediction Decay

- Compare predictive correlation across the retained `decay_lags`.
- Fast decay suggests tighter rebalance requirements and higher cost sensitivity.
- Slow decay may support a longer cadence but can reflect a slow-moving style proxy.

## Chart 5: Prediction-Style Correlation

- Inspect sign, magnitude, stability, and missing periods for each style correlation.
- Correlation does not establish causality. Propose one controlled neutralization or stratification
  test when a style alternative is consequential.

## Chart 6: Daily Turnover

- Read the current Strategy single-sided `/2` convention.
- Relate spikes to exposure changes, rebalance cadence, or regime transitions.
- Use the retained EMA only as a smoother; do not replace the raw series with it.

## Retained Numeric Projection

The overview projection includes `available`, `schema_version`, `generated_at`, `window`, `params`,
`cross_section`, `missing_styles`, and a six-chart catalog. Each paged chart response contains an
`x` axis page, named numeric-or-null `series`, a `plot` order, legend, colors, and metadata. Dynamic
quantile names, style names, and EMA suffixes are provider data; do not hard-code a series set beyond
the trusted response.
