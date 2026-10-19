# Reusable Strategy logic card

Build this card from the exact immutable Strategy and selected StrategyRun. It supports
single-Strategy diagnosis and Portfolio candidate evaluation; it is not a requirement to hydrate
every inventory row. Read only fields needed for the user's goal and preserve missing evidence.

| Dimension | Evidence and interpretation |
| --- | --- |
| Identity and scope | Exact Strategy/Run, ownership or sharing context, status, window, cutoff and IS/OOS/ALL label |
| Prediction thesis | Available economic mechanism, exact Factor lineage, input assumptions and alternative explanations |
| Trading definition | Actual universe, Factor weighting, ranking, selection, direction and rebalance from the immutable definition |
| Implementation | Retained execution parameters, long/short behavior, gross/net and available style/group exposures |
| Result | Canonical net return, risk, drawdown/recovery and time concentration; no filled or averaged missing metrics |
| Cost and feasibility | Available turnover, fees, funding, trading and liquidity evidence; capacity is unknown without evidence |
| Robustness | Supported quantile behavior, decay, state/window stability, observed failure conditions and missing evidence |

Follow the chain from hypothesis to Factor information, ranking, positions, net returns and risks.
Do not reverse-engineer a causal story from a high Sharpe. Diagnostic quantile buckets are not
the Strategy's actual selection rule. A Strategy's aggregate success does not prove every Factor
works or identify its marginal contribution without a suitable control.

Label consequential statements Observed, Inference, Alternative or Experiment. Propose a bounded
change with an expected effect, confirmation metric and tradeoff; hand already-authorized
execution to `$strategy-building` or input-level repair to `$factor-mining` through the appropriate
analysis. Do not submit from this read-only workflow.

For Portfolio selection, return the goal-relevant card, evidence readiness and exact lineage to
`$portfolio-building`. For an existing Portfolio result, evaluate the actual source StrategyRun
requested by `$portfolio-analysis`, not a newer or better run. Community child evidence remains
under the exact Publication/Share read selectors; never switch to owner tools for convenience.
