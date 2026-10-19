# Test historical incremental value

## Fix the comparison

Record the predeclared objective, core Strategy, members, capital weights and comparison window.
If evaluating an existing result without a prior plan, call the analysis exploratory. Compare
with each actual member and, for custom weights, an available same-member equal-initial-capital
control. Label any retrospective best member with the metric used to identify it; do not replace
the original baseline after seeing the result or compare only with a weak member/average.

Use [Portfolio evidence](evidence-contract.md) and the shared
[neutrality framework](../../../references/portfolio-neutrality.md). No valid common window or
cost convention means the affected comparison is unavailable. Do not fill dates or fabricate a
baseline. Selecting a control does not itself authorize submitting another Portfolio backtest.

## Four dimensions

- **Return and risk:** net annual return, volatility, Sharpe, drawdown, duration/recovery and
  available downside/tail behavior. Derived Sharpe difference and drawdown-magnitude improvement
  require comparable returned metrics. Check time concentration and available state/window evidence.
- **Diversification:** distinguish full-sample/rolling/downside correlation, overlapping drawdowns,
  exposure concentration and risk contribution. Joint statistics require aligned underlying
  evidence and a declared calculation; isolated curves/headlines are not a complete risk model.
- **Neutrality:** identify intended dollar/Beta/style/group constraints and observed drift. A Sharpe
  increase alone does not prove independent Alpha or improved neutrality. Residual-return claims
  require actual common-risk-model evidence; current exposure is not historical exposure.
- **Implementation:** compare available turnover, fees, funding, liquidity/capacity and execution
  assumptions. Potential opposing trades are not realized netting savings. Do not infer impact,
  borrowing or capacity evidence merely because the report template has those fields.

If a declared analysis supplies a diversification ratio, sum(w_i * sigma_i) / sigma_p measures
volatility diversification under those weight/covariance assumptions. It does not establish better
tail behavior, economic independence or future performance. Risk balance and correlation effective
dimension have the same evidence limitations described in the shared reference.

## Verdict

- **Historical evidence supports improvement:** goal-relevant net risk/return or drawdown improves,
  available window/state evidence is reasonably stable, complementary evidence supports the claim,
  and observed cost or concentration does not erase the benefit. State the historical scope.
- **Risk/return tradeoff:** name what improved and the return, risk, cost or concentration paid for it.
- **No demonstrated improvement:** comparable evidence shows no goal-relevant benefit or costs/
  concentration overwhelm it. Unavailable data alone is not proof of no benefit.
- **Insufficient evidence:** key comparability, coverage, holdings, cost or joint-risk evidence is
  missing. Still report independent observations that remain supported.

Do not call same-sample selection and evaluation OOS, or treat a short common window as durable
proof. Predefine validation when proposing a subsequent experiment.

## Member marginal value

Attribution explains historical contribution; it does not answer the counterfactual without that
member. A controlled leave-one-out comparison must state whether remaining initial capital is
renormalized, reduced or otherwise changed, and which conditions remain fixed. Use only supported
positive-weight Portfolio definitions; do not invent a cash sleeve or a zero-member Portfolio.
Keep exact definitions/Runs, interval and costs comparable. The observed delta is conditional on
that control and is not general causal proof.

Read an existing control if available. Otherwise propose the experiment or hand an already-
authorized one to `$portfolio-building`. Analysis must not create all possible subsets by default.

Return a concise comparison of available metrics, one main verdict, two or three decisive pieces
of evidence, the most important gaps and failure conditions. Do not pad the output with invented
metrics or demand a long report for a focused question.
