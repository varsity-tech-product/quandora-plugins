# Strategy Artifacts And Metric Semantics

Apply each artifact's declared schema and window. Missing or null values remain unavailable.

## Primary Evidence

- `sb_get_run` provides canonical composition and effective parameters.
- `sb_get_artifact` with `summary` and `performance` provides headline result metrics.
- Equity and drawdown curves show path dependence, concentration, and recovery.
- Turnover and exposure curves show implementation intensity and neutrality through time.
- Attribution and signal-return curves can support mechanism claims only when actually included.
- Orders and trades are execution evidence, not substitutes for the canonical run snapshot.

## Return And Drawdown

- Compare return, Sharpe, Sortino, drawdown, and fees over the same declared period.
- Treat a signed negative drawdown as a loss from peak; name the sign convention when reporting it.
- A high return with concentrated time contribution or slow drawdown recovery is less robust than
  an evenly distributed path with the same headline return.

## Strategy Costs

Consult the approved `operation.strategy.result.read` Guide when interpreting
costs. Use the exact run's canonical `summary.metrics` values; do not assume the
MCP result contains the three derived display fields below.

- Raw `funding_net_cash_flow` is funding received minus funding paid: positive
  means income, negative means payment.
- Raw `total_fees` is transaction/execution fees only, not the combined total.

The current frontend displays these derived amounts in USDT:

| Display metric | Derivation |
| --- | --- |
| Funding fee | `funding_fee = -funding_net_cash_flow` |
| Transaction fee | `transaction_fee = total_fees` |
| Total fee | `total_fee = total_fees - funding_net_cash_flow` |

For these display costs, positive means expense and negative means income.
Combined total fee can legitimately be negative when funding income exceeds
transaction fees. Never take an absolute value to hide that sign.

| Raw funding cash flow | Raw transaction fees | Funding fee | Transaction fee | Total fee |
| --- | --- | --- | --- | --- |
| 30 | 100 | -30 | 100 | 70 |
| -30 | 100 | 30 | 100 | 130 |
| 0 | 100 | 0 | 100 | 100 |
| 150 | 100 | -150 | 100 | -50 |
| Missing/null | 100 | Unavailable | 100 | Unavailable |
| 30 | Missing/null | -30 | Unavailable | Unavailable |

Preserve exact numeric zero. Derive a component only from its present finite
numeric source. Missing, null or non-finite values stay unavailable; the total
requires both finite sources. Do not invent returned fields or change the
canonical raw values.

Repaired/new QuantAI Strategy backtests already settle funding and execution
costs into equity, returns and dependent metrics. These amounts explain costs;
do not deduct them again. Historical results are not backfilled. A historical
funding field alone does not prove settlement into equity; do not "repair" old
results by adding/subtracting one amount, because settlement affects subsequent
capital and position sizes. A rerun requires separate user authorization.

This is the Strategy backtest contract. Paper funding signs and accounting have
their own contract; do not transfer these formulas to Paper automatically. If
Guidance or result evidence is unavailable, report the gap without guessing or
bypassing MCP. This analysis remains read-only: no submission, rerun, Paper
start or equity adjustment.

## Strategy Turnover

- Strategy daily turnover is single-sided: `sum(abs(delta weight)) / 2`.
- Factor cross-sectional turnover uses a different convention without `/2`. Name the convention
  before comparing the two.
- Interpret turnover with rebalance bars, modeled fees, signal persistence, and realized breadth.

## Composition

- `composition.mode: ids` means equal weighting across selected factor identities.
- `composition.mode: weights` means explicit positive factor weights from the canonical snapshot.
- The factor list alone does not prove each factor's marginal contribution.
- Do not infer correlations, ablations, or standalone factor quality from Strategy-level returns.

## Scope Labels

- `IS` means in-sample.
- `OOS` means a separately declared out-of-sample scope.
- `ALL` combines available scopes and includes IS; it is not pure OOS.
- Always report the exact artifact label and window rather than upgrading the scope in prose.
