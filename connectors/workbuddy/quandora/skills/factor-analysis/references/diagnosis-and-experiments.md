# Factor Diagnosis And Experiments

Start with evidence, then explain mechanisms. Avoid reverse-engineering a story from a grade.

## Diagnostic Questions

1. Did the Factor Card Health Check run, and which recorded gates passed or failed?
2. Is the factor's intended applicability consistent with the Health Check coverage basis?
3. Does `cs_fail_reasons` identify a Health, prediction, stability, or other rating gate?
4. Is the return spread monotonic across groups or concentrated in one tail?
5. Do both long and short legs contribute, or does one leg carry the result?
6. Is performance broadly distributed across time or concentrated in a short episode?
7. Does drawdown coincide with market, volatility, liquidity, or coverage changes visible in the
   evidence?
8. Is turnover consistent with the intended economic horizon?
9. Are missingness and cross-sectional size sufficient for the reported statistics?
10. Could the signal be a proxy for size, liquidity, momentum, value, or market exposure?

## Evidence Ladder

- **Observed:** quote exact trusted metrics, chart patterns, and manifest status.
- **Inference:** state the mechanism that could connect those observations.
- **Alternative:** name at least one plausible competing explanation for consequential claims.
- **Experiment:** define the smallest controlled test that distinguishes them.

Use causal language only when the supplied evidence supports causality. Backtest association alone
does not establish a causal mechanism.

## Health And Rating Patterns

### Final F With Strong Sharpe Or Grade Score

A hard gate can fail even when a continuous performance metric is strong. Read the available
`health_check`, `cs_success`, and `cs_fail_reasons`; list the recorded value, comparator, and
threshold for each relevant failure. Do not require unavailable internal check fields and do not
reverse-engineer the failure from the final grade.

### High Null Ratio Or Low Health Coverage

Possible causes include source-field availability, warm-up, invalid denominators, pipeline gaps,
or intentional filters and abstention. Inspect inert source and declared applicability. Compare the
target universe with effective cross-sectional breadth over time when that evidence exists. Do not
remove a meaningful filter merely to pass Health; first determine whether the factor definition and
the current Health basis express the same research domain.

### Health Passed But Final Grade Failed

Data quality passed its recorded contract, but prediction strength, persistence, CS performance, or
another exposed gate may still have failed. Use `cs_fail_reasons` and present distance from any
recorded boundary without describing a near-threshold failure as catastrophic.

### Health Missing Or Null

The check was not run or its outcome is unknown. Read `message` or other safe diagnostics when
available, report the evidence gap, and never treat the state as either a Health pass or proof of a
specific runtime error.

## Controlled Experiment Templates

- **Turnover control:** apply one smoothing or rebalance change; expect lower turnover and define the
  maximum acceptable loss in spread or Sharpe.
- **Tail robustness:** change only the selection breadth; expect the same direction with less tail
  concentration if the mechanism is broad.
- **Direction test:** invert only the factor direction; expect degradation if the claimed direction
  is real.
- **Coverage test:** tighten only the data-validity threshold; expect stability if missingness is not
  driving the result.
- **Applicability-contract test:** keep the factor formula fixed and propose evaluating Health on a
  predefined applicable universe while also reporting effective cross-sectional breadth. This is a
  research proposal, not an action available to this read-only skill.
- **Source-availability decomposition:** keep the formula fixed and split missingness by field
  availability period and asset coverage; expect gaps to concentrate at explainable data boundaries
  if the source is responsible.
- **Style control:** neutralize or stratify one suspected style; expect residual spread if the factor
  has incremental content.
- **Window stability:** rerun the same definition on a distinct declared window when the product
  workflow supports it. Do not call current external-agent evidence OOS.

For each proposal, state the independent variable, expected change, confirmation metric, and
tradeoff. Prefer two or three high-information tests over a long optimization list.

## Decision Language

- **Reject:** evidence contradicts the mechanism or integrity is unreliable.
- **Investigate:** important evidence is missing or alternatives remain unresolved.
- **Revise:** a specific mechanism-level change is justified.
- **Hand off:** evidence is adequate for a user-confirmed Strategy experiment, not for automatic
  promotion.
