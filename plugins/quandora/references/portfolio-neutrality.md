# Complementarity and cross-sectional neutrality

Use this method for candidate selection and existing Portfolio diagnosis. It consumes ready,
authorized evidence; it does not add data access or product constraints. Start with the
[research evidence contract](research-workflows.md#capability-aware-analysis).

## Distinguish the constraints

Dollar neutrality concerns long/short notional. Beta neutrality concerns market sensitivity.
Style and group neutrality concern the named risk exposures and groups. Balanced notional does
not prove balanced risk, and an inception constraint does not prove neutrality during stress.
Record the intended constraint, tolerance when supplied, and observed drift without inventing one.

A Portfolio combines independently formed Strategy sleeves. Combining raw Factor scores into a
new ranking belongs to Strategy Building and changes the selection rule. Do not conflate these
operations. Opposing sleeve targets do not prove executed order netting or saved fees. Research
aggregation and forward net-ledger finance have different contracts; use actual execution evidence
before claiming realized netting benefits.

## Evaluate complementary evidence

1. **Mechanism:** compare data, universe, Factor family, direction, transformations, selection,
   rebalance cadence and expected failure states. Parameter neighbors can repeat one risk source.
2. **Prediction:** synchronized values or cross-sectional ranks can support Spearman comparisons
   on common dates/assets, decay and overlap. Separate marginal charts cannot establish joint
   signal correlation. Different universes and missing dates must be disclosed.
3. **Holdings:** distinguish long-long overlap, short-short overlap and long-short conflict using
   synchronized signed holdings. Net exposure alone can hide gross, liquidity and cost concentration.
4. **Exposure:** compare market, style and group exposure and its drift. Residual correlations
   require the same stated risk model, factor series, fit window and available residual evidence;
   do not substitute an informal story for a regression.
5. **Implementation:** inspect common rebalance times, turnover peaks, funding and liquidity risks
   only where the evidence supports them. Potential offsets are not realized cost savings.
6. **Outcomes:** prefer common-window return paths, rolling/downside/stress correlations,
   overlapping drawdowns and recovery over a single full-sample statistic. Report sample coverage.

Low historical return correlation alone supports only an initial diversification hypothesis.
Explain whether independent mechanisms, holdings or residual evidence support a stronger claim.
Do not call every separately named member an independent Alpha source.

## Weight and statistical semantics

The product allocates initial capital, not a periodically rebalanced fixed-weight portfolio.
Sleeve equity shares can drift. For a specified weight vector w and covariance matrix Sigma,
sigma_p = sqrt(w' Sigma w) and RC_i = w_i (Sigma w)_i / sigma_p describe that stated risk model.
Do not present initial-weight estimates as realized full-run risk contributions. Zero portfolio
variance, unavailable series or an unspecified convention makes the estimate unavailable.

If supplied by a declared, reproducible analysis, inverse concentration of absolute normalized
risk contributions measures risk balance; correlation-matrix eigenvalue effective dimension
measures correlation structure. Neither proves the count of independent economic sources.
Signed contributions can be negative, and short samples or shifting regimes limit stability.
Do not derive these quantities from rounded headline Sharpe or volatility values.

Positive constant scaling does not change correlation: corr(aX, bY) = corr(X, Y) for a,b > 0.
Different volatility levels alone therefore cannot explain low correlation. Inspect time-varying
exposure, distinct common-risk loadings, noise, timestamp alignment or data gaps instead.

The intuition IR ~ IC * sqrt(BR) does not make breadth equal to asset count times rebalance count.
Cross-asset dependence, overlapping holdings and persistent predictions reduce effective breadth.
Do not use this relation as a product performance forecast.

State the neutrality actually evidenced, the source of complementarity, the likely shared failure
state, and whether evidence supports independent Alpha or only observed historical risk reduction.
