# Controlled Experiments And Paper Readiness

Optimization proposals are research hypotheses, not automatic actions.

## Experiment Design

For each proposed test, state:

1. the single changed variable or tightly bounded change set;
2. the observed evidence motivating it;
3. the mechanism and at least one alternative explanation;
4. the expected direction of change;
5. the metric or chart that confirms or rejects the hypothesis;
6. the principal tradeoff.

Useful controlled tests include:

- remove or down-weight one factor only when evidence identifies a plausible concentration problem;
- compare equal weights with one explicit weight change;
- change ranking breadth while keeping composition and fees fixed;
- change rebalance cadence while measuring turnover, costs, and decay;
- rerun with one suspected style control;
- change one fee assumption to assess implementation fragility.

Current server evidence does not guarantee per-factor correlations or automatic ablations. Propose them
as future controlled runs rather than reporting nonexistent results.

## Paper Readiness Questions

- Is server evidence integrity trustworthy and is the exact run configuration known?
- Is performance distributed across time rather than concentrated in one short episode?
- Is drawdown depth and recovery acceptable for the intended risk budget?
- Are turnover and modeled costs plausible?
- Is nominal neutrality supported by realized exposure evidence?
- Are major style, size, liquidity, and market alternatives understood or queued for testing?
- Are important artifacts missing or null?
- Does the evidence include a distinct validation scope, or only IS/ALL evidence that includes IS?

## Decisions

- **Reject:** integrity or results contradict the intended mechanism.
- **Research:** important alternatives or evidence gaps remain.
- **Controlled rerun:** one or more falsifiable changes should be tested through `$strategy-building`.
- **Consider Paper:** evidence is sufficient for user review, but actual Paper start remains a
  separate explicit action through `$paper-trading`.

Never start, stop, or monitor Paper Trading from this skill. Never present Paper readiness as a
guarantee of live performance.
