# Test historical incremental value

## Make the comparison valid

Judge whether a Portfolio beats its single Strategies only when all of these hold:

- the exact member Runs, member settings, capital weights and baselines were fixed before the
  Portfolio result was read;
- the Portfolio and its members share a common window, frequency, valuation time and return unit;
- fees, funding, leverage and gross exposure follow one convention;
- series align on common timestamps without filling returns that do not exist;
- the members are the versions the Portfolio actually used, not same-named other backtests;
- no member was retuned, rewindowed, swapped for another Run or picked from several versions
  after a weak result.

If evaluating an existing result without a prior plan, call the analysis exploratory. Missing key
curves, exposures or costs downgrade the affected conclusion to insufficient evidence. Use
[Portfolio evidence](evidence-contract.md) and the shared
[neutrality framework](../../../references/portfolio-neutrality.md). Do not fill dates or fabricate
a baseline. Selecting a control does not itself authorize submitting another Portfolio backtest.

## Fixed comparisons

Compare at least:

1. the equal-capital Portfolio with the predeclared core Strategy;
2. the equal-capital Portfolio with each actual member;
3. the equal-capital Portfolio with the best single member in the same window, naming the metric
   that defines "best";
4. when the user specified non-equal weights, that composition with the same members at equal
   capital, using an existing comparable result.

Never compare only with the member average, and never pick a weak member as the baseline after
seeing the result. Equal capital is the AI's recommendation; never generate several weight sets
and present the best in-sample one as the recommendation. User-specified weights stay labeled as
the user's constraint.

## Four dimensions

- **Return and risk:** annualized net return, volatility, Sharpe; maximum drawdown, drawdown
  duration and recovery; available downside volatility, tail loss and share of losing months;
  whether a few dates, symbols or members drive the result. Delta Sharpe = Sharpe(Portfolio) −
  Sharpe(baseline) and drawdown improvement = |max drawdown(baseline)| − |max drawdown(Portfolio)|
  require comparable returned metrics. Do not conclude from point estimates alone; check rolling
  windows, market states and stability where the evidence exists.
- **Diversification:** full-sample, rolling, downside and drawdown-period correlation between
  members; whether Factor, direction, sector, symbol and liquidity concentration fell; whether
  risk contribution concentrates in a few members; whether effective dimension rises with each
  added member; whether drawdowns are staggered. Joint statistics require aligned underlying
  evidence and a declared calculation; isolated curves or headlines are not a complete risk model.
- **Neutrality:** for cross-sectional long/short members, whether dollar, Beta, style and group
  neutrality improve on the single members; whether the raw improvement survives in residual
  returns after common risk Factors; whether long-long, short-short and cross-side overlap fall;
  whether gross exposure and risk contribution concentrate in a few members; whether stress
  periods worsen neutrality drift or residual correlation. A higher Sharpe that comes only from
  more gross exposure, hidden Beta or a common style is not an independent Alpha gain.
  Residual-return claims require actual common-risk-model evidence; current exposure is not
  historical exposure.
- **Implementation:** turnover, fees, funding, borrow difficulty, impact and capacity before and
  after combining. Separate theoretically offsetting trades, trades actually netted in execution,
  and duplicated trades that cannot net because rebalance times differ. Without execution
  evidence, netting savings are potential, not a realized gain. Do not infer impact, borrowing or
  capacity evidence merely because the report template has those fields.

If a declared analysis supplies a diversification ratio, sum(w_i * sigma_i) / sigma_p above one
shows volatility diversification under those weight and covariance assumptions. It does not
establish better return quality, tail behavior, economic independence or future performance.

## Verdict

- **Historical evidence supports improvement:** net risk-adjusted return or drawdown behavior
  clearly improves for the goal; the improvement broadly holds across windows and states;
  prediction, holdings or residual evidence shows real complementarity; costs do not erase the
  main improvement; no worse concentration or neutrality drift appears. State the historical scope.
- **Risk/return tradeoff:** risk falls while return also falls clearly, or return rises while
  drawdown, cost, leverage or concentration worsens. Name what improved and what was paid for it.
- **No demonstrated improvement:** return falls without better risk; Sharpe, drawdown and recovery
  show no stable improvement; low correlation comes from misaligned windows or short samples;
  members are essentially duplicates that still lose together in stress; or added cost cancels
  the diversification benefit. Unavailable data alone is not proof of no benefit.
- **Insufficient evidence:** the common window is too short, or returns, costs, exposures,
  holdings or valuation conventions cannot be aligned. Still report independent observations
  that remain supported.

Do not call same-sample selection and evaluation OOS, or treat a short common window as durable
proof. Predefine validation when proposing a subsequent experiment.

## Member marginal value

Attribution explains historical contribution; it does not answer what happens without that
member. The controlled test removes one member and gives the remaining members equal initial
capital again, keeping member Runs, settings, window and other rules unchanged, then compares the
complete equal-capital Portfolio with that reduced one. Use only supported positive-weight
Portfolio definitions; do not invent a cash sleeve or a zero-member Portfolio. The observed delta
is conditional on that control and is not general causal proof. Without such a control, report
only correlation, risk contribution, holdings overlap and alternative explanations.

Read an existing control if available. Otherwise propose the experiment or hand an already-
authorized one to `$portfolio-building`. Analysis must not create all possible subsets by default.

## Output

Fill the comparison with available metrics; leave unavailable cells marked unavailable:

| Item | Equal-capital Portfolio (recommendation) | Core Strategy | Best single member | Judgment |
| --- | ---: | ---: | ---: | --- |
| Annualized return | | | | |
| Annualized volatility | | | | |
| Net Sharpe | | | | |
| Maximum drawdown | | | | |
| Drawdown recovery | | | | |
| Risk contribution concentration | | | | |
| Neutrality drift | | | | |
| Turnover and cost | | | | |

When the user specified non-equal weights, add a "User-specified weights" column to the left of
the equal-capital column; never replace the equal-capital column with it.

After the table give one main verdict, the two or three decisive pieces of evidence, the most
important gaps and failure conditions. Scale the table to a focused question; do not pad it with
invented metrics.
