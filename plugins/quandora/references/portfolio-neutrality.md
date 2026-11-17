# Complementarity and cross-sectional neutrality

Use this method for candidate selection and existing Portfolio diagnosis. It consumes ready,
authorized evidence; it does not add data access or product constraints. Start with the
[research evidence contract](research-workflows.md#capability-aware-analysis): each layer below
says what to check, and that contract says what to report when the evidence is unavailable.

## Distinguish the constraints

Cross-sectional neutrality is a set of different constraints, not one label:

- **Dollar neutral:** long and short notional offset, so net exposure is near zero.
- **Beta neutral:** first-order sensitivity to market returns is near zero.
- **Style neutral:** exposure to size, value, momentum, volatility, liquidity and similar
  systematic Factors is controlled.
- **Group neutral:** longs and shorts are paired within sectors, symbol groups or other groups.
- **Dynamic neutral:** the constraints hold through the holding period and stress, not only at
  entry.
- **Risk neutral:** the risk contributions of the two sides or of the members are controlled,
  not only their notional.

Balanced notional does not prove Beta neutrality, let alone style, group or tail neutrality.
For each constraint record what is constrained, the tolerance when supplied, and the observed
drift without inventing one.

## Members versus signals

A Portfolio combines independently formed Strategy sleeves. Combining raw Factor scores into a
new ranking belongs to Strategy Building and changes the selection rule. Each member is a frozen
exact Strategy and StrategyRun; Portfolio Building does not change its Factors, universe,
neutralization, selection, long/short proportions, rebalance or window, and does not pick among
parameter versions by curve.

- Member combination keeps each member's universe, normalization, group neutralization and
  rebalance cadence.
- Signal combination changes the cross-sectional ranking, selection boundaries, turnover and
  long/short pairing.
- Opposing sleeve targets do not prove executed order netting or saved fees. Research
  aggregation and forward net-ledger finance have different contracts; use actual execution
  evidence before claiming realized netting benefits.
- Without unified scoring and execution evidence, do not describe a member Portfolio as a new
  joint cross-sectional model.

## Evaluate complementary evidence

1. **Definition and mechanism:** compare raw data and update frequency, universe and liquidity
   thresholds, Factor direction, transformations, neutralization and missing-value handling,
   ranking, buckets, long/short proportions, holding period and rebalance cadence, and why each
   signal should keep working across market states. The same universe, core Factor and similar
   ranking rule usually mean shared model risk even when historical return correlation is low.
2. **Prediction:** on common dates and common tradable symbols, prefer the per-period Spearman
   correlation of predictions or ranks, and inspect its distribution and change over time rather
   than one full-sample mean. Also check long/short quantile monotonicity, IC mean, stability and
   decay, rank autocorrelation and signal half-life, whether the correlation concentrates in
   particular sectors or states, and whether it changes after neutralization. Separate marginal
   charts cannot establish joint signal correlation. Disclose different universes and missing dates.
3. **Holdings:** for each rebalance, compare long-long overlap, short-short overlap, long-short
   conflict, cosine similarity of active weights, and concentration by symbol, sector, liquidity
   tier and trade timing, using synchronized signed holdings. Net exposure alone hides
   duplication: identical long and short holdings can cancel in equity while still consuming
   gross exposure, funding and turnover, and cross-side conflicts can cancel expected return while
   adding cost.
4. **Exposure:** explain each member's return with common risk Factors,
   r_k,t = alpha_k + beta_k' f_t + e_k,t, where f_t covers at least the market, common styles and
   the sector or symbol risks relevant to the universe. Compare raw return correlation, the
   similarity and drift of the exposure vectors, residual correlation, and exposure changes and
   residual co-movement in stress. Residual claims require the same stated risk model, factor
   series, fit window and available residual evidence; do not substitute an informal story for a
   regression.
5. **Implementation:** compare rebalance synchronization, turnover peaks, capacity, impact,
   funding, borrow constraints and signal decay where the evidence supports them. Members sharing
   a universe and rebalancing on the same day can compete for the same liquidity in stress, which
   daily equity curves rarely reveal. Potential offsets are not realized cost savings.
6. **Outcomes:** analyze full-sample and rolling correlation; up, down and high-volatility states;
   the Portfolio's own drawdown windows; downside correlation, tail loss, drawdown overlap and
   recovery; and contributions from net return, residual return and each side. The main risk for
   cross-sectional members is independence in normal times and alignment in stress, so stress and
   drawdown evidence outranks a single full-sample coefficient. Report sample coverage.

If raw returns correlate little but residuals correlate highly, the apparent complementarity may
come only from different common-Factor loadings. If raw returns correlate highly but residuals do
not, the members may share a manageable common risk while keeping independent selection skill.
Low historical return correlation alone supports only an initial diversification hypothesis.
Explain whether independent mechanisms, holdings or residual evidence support a stronger claim.
Do not call every separately named member an independent Alpha source.

## Real and false diversification

Real complementarity meets most of these: different economic hypotheses and signal sources; low
cross-sectional rank correlation not caused by universe mismatch; explainable long, short and
cross-side relations; low residual correlation after common Factors; drawdowns in different states
or with different recovery mechanisms; added cost below the added independent return and risk
buffer.

Common false diversification:

- **Same Factor, different parameters:** several Strategies that are neighboring versions of one
  ranking.
- **Net exposure illusion:** zero dollar exposure with large Beta, style or sector exposure.
- **Scale illusion:** different gross exposure or volatility changes each member's share of
  Portfolio risk, not their correlation; low raw with high residual correlation points to
  different common-Factor loadings instead.
- **Offset illusion:** a smooth aggregate return while both sides repeat trades and costs rise.
- **Timing illusion:** different data gaps or valuation times create low correlation.
- **Sample-split illusion:** each member did well only in a different short window, with no
  complementarity across the full common window.
- **Liquidity co-movement:** different holdings in normal times, but the members exit the same
  liquidity tier together in stress.

## Construction principles

1. Identify and control market, style and group exposure on a common convention first.
2. Then judge independence from predictions, holdings and residual returns.
3. Keep at least two explainable independent Alpha sources in a multi-member design.
4. Give members equal initial capital and report gross exposure and risk contribution; if the
   concentration is unacceptable, remove or replace members and weight the rest equally instead
   of optimizing weights.
5. Validate on the full sample, a recent window and stress periods separately.
6. Without a long enough common sample, do not set arbitrary correlation or Sharpe thresholds.
7. Do not add a member that neither raises effective breadth nor fixes a named risk gap.

## Weight and statistical semantics

The product allocates initial capital, not a periodically rebalanced fixed-weight portfolio.
Sleeve equity shares can drift. For a specified weight vector w and covariance matrix Sigma,
sigma_p = sqrt(w' Sigma w) and RC_i = w_i (Sigma w)_i / sigma_p describe that stated risk model.
Do not present initial-weight estimates as realized full-run risk contributions. Zero portfolio
variance, unavailable series or an unspecified convention makes the estimate unavailable.

If supplied by a declared, reproducible analysis, inverse concentration of absolute normalized
risk contributions, 1 / sum(p_i^2), measures risk balance: the closer to the member count, the
more even the risk. Correlation-matrix eigenvalue effective dimension,
(sum lambda_j)^2 / sum(lambda_j^2), measures correlation structure. Neither proves the count of
independent economic sources. Signed contributions can be negative, and short samples or shifting
regimes limit stability. Do not derive these quantities from rounded headline Sharpe or volatility.

Positive constant scaling does not change correlation: corr(aX, bY) = corr(X, Y) for a,b > 0.
Different volatility levels alone therefore cannot explain low correlation. Inspect time-varying
exposure, distinct common-risk loadings, noise, timestamp alignment or data gaps instead.

The intuition IR ~ IC * sqrt(BR) is research intuition only. BR counts independent effective
decisions, not asset count times rebalance count: cross-asset dependence, overlapping holdings and
persistent predictions reduce effective breadth. Do not use it as a product performance forecast.

## Required conclusions

State, for the actual members and evidence:

- which kind of neutrality each member targets and whether it actually held;
- whether independence comes from signals, holdings or risk exposure;
- whether raw and residual correlation agree;
- what the long, short and cross-side relations are;
- in which state the Portfolio is most likely to lose neutrality and co-move;
- whether the evidence supports added independent Alpha or only lower historical volatility.
