# Factor Metric Semantics

Apply the artifact's own schema and labels first. Use these rules when the matching metric is
present; never synthesize a missing value.

## Factor Health And Applicability

`health_check` is an embedded Factor Card data-quality section, not a prediction score or a
standalone analysis capability. Read the complete available block before interpreting performance:

- `passed`, `message`, and `failed_metrics` describe the recorded outcome;
- `metrics` contains the observed values;
- `thresholds` contains the gates used for that exact result;
- `window` declares the calculation period;
- `coverage_basis` identifies the coverage denominator convention.

Apply only the thresholds preserved in the artifact. Do not invent fallback thresholds or recompute
Health from a projected card. The current common metrics mean:

- `null_ratio`: NaN cells divided by active cells;
- `zero_ratio`: exact-zero cells divided by active cells;
- `coverage_ratio`: valid cells divided by active cells at each timestamp, then averaged over
  timestamps with active cells; zero values still count as covered;
- `outlier_ratio_3sigma`: values more than three cross-sectional standard deviations from the mean,
  divided by valid cells and averaged over calculable timestamps.

Interpret the exact basis from the artifact and applicable contract. Under an `active_universe`
basis, a symbol can remain active between its first and last valid values, so intentional NaNs from
an intermediate liquidity or applicability filter can still reduce Health coverage.

Treat absent Health or `passed=null` as not run or unknown evidence, never as pass. Continue other
analysis, but state the evidence gap. Compare Health results only when window, active-universe
definition, missing-value handling, and thresholds match.

Do not substitute `coverage_mean` for `health_check.metrics.coverage_ratio`. The former may use a
different universe denominator or time aggregation. Report both with their exact labels when both
are present.

## Return And Drawdown

- Cross-sectional net return is the portfolio return after the artifact's modeled fees and costs.
- `cs_return` is annualized as `365 * mean(net_r)` under the current calculation contract.
- `cs_max_drawdown` is a signed negative drawdown computed from log NAV. A more negative value is a
  deeper drawdown; do not silently convert it to a positive magnitude.
- Compare Sharpe, return, and drawdown over the same declared window. Do not mix metrics from
  different scopes or windows.

## Turnover

- Factor cross-sectional turnover is `mean(sum(abs(delta weight)))`.
- It is not divided by two. Do not compare the number directly with Strategy daily turnover without
  naming the convention difference.
- High turnover is evidence of implementation pressure, not proof that realized performance will
  fail. Test fee sensitivity and signal smoothing as controlled experiments.

## Signal Persistence

- `factor_autocorr_lag1` is the lag-one Pearson correlation of the daily cross-sectional
  equal-weight signal mean.
- Fewer than ten valid days produces null, not zero.
- High persistence can support lower turnover but can also indicate slow-moving style exposure.
  Interpret it with the charts and factor mechanism.

## Cross-Sectional Evidence

- Group ordering and spread matter more than a single headline score.
- Monotonic group returns support an ordering mechanism. A result driven only by one extreme group
  is more fragile.
- Inspect long and short legs separately. A neutral spread may be dominated by only one side.
- Small or irregular daily cross sections reduce confidence in quantile and correlation evidence.

## Grade And Score

- Grade or score is QuantAI-relayed evidence.
- It is not a promotion decision, research approval, or guarantee of robustness.
- Keep `grade_score` separate from the final `grade`: a continuous score does not override a hard
  gate, and a final F does not prove that Sharpe, IC, or `grade_score` was poor.
- Trace `health_check` to `cs_success` and `cs_fail_reasons`, then to `status` and `grade`. State that
  Health caused the grade only when an authoritative artifact field, such as `cs_fail_reasons`,
  confirms that propagation.
- A passed Health Check establishes data-quality eligibility under its recorded contract; it does
  not guarantee that prediction, stability, or other rating gates passed.
- Explain the underlying metrics and evidence gaps instead of treating the grade as the conclusion.
