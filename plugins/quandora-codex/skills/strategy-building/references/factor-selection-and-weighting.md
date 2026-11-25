# Factor selection and signal weighting

Load this reference when the user delegates Factor choice or asks for a multi-Factor Strategy
design. When the user supplies exact Factors and settings, validate and execute that intent
without redoing the candidate study.

## 1. Fix the goal and candidate scope

Write the goal as a testable question, such as adding an independent predictive source, improving
ranking stability, or reducing concentration in data, style, liquidity or failure state.

- User-specified Factors: evaluate only those; never substitute silently.
- Delegated selection: build a bounded candidate set from `list_eligible_strategy_factors` and
  disclose the scope actually inspected.
- Do not walk the whole inventory, pick the best single backtest score, or claim a global optimum.

Bind every candidate to the exact admission record returned for it: `admission.factor_family_id`,
`admission.factor_id` and `admission.factor_run_id`. An official row also keeps its
`official_factor_id` for similarity reads.

## 2. Reuse Factor Cards

Read or reuse, through `$factor-analysis`, the Factor Card that matches each exact identity, run
and window. Record at least:

- identity, source, status, window and data cutoff;
- mechanism, inputs and their timing, direction, prediction horizon and applicable states;
- Health, rating, coverage, missingness and applicability;
- quantile and IC evidence, decay, stability, turnover and implementation cost;
- style, liquidity, crowding, redundancy, failure conditions and evidence gaps.

Compare only metrics with compatible conventions. Missing values, `null` and a Health check that
did not run stay unknown, never zero or passed. A style, causal mechanism or failure state the
card did not measure directly is an Inference, not an observed fact.

Do not change a formula, switch runs, change the window or create a Factor to improve a candidate.
Route improvement ideas to `$factor-mining`; they are not part of this composition.
Server admission decides product eligibility; the Factor Card decides the research case.

## 3. Measure Factor value correlation

For the bounded set that passes the standalone screen in section 4, read server-retained pairwise
evidence; never download raw signals and join them locally. Use `compare_factor_runs` for owned
pairs and `compare_with_official_factors` for pairs that involve an official Factor, covering
every pair as in [Research playbooks](../../../references/research-playbooks.md). Check that the
returned identities, window and order match the candidates.

Composition decisions use only the `value` statistic: the mean daily cross-sectional Spearman
correlation of the two Factor values. The same response carries `ic_curve` and `long_short`; do not
use them to select, exclude or call Factors complementary in this workflow.

For each pair keep the `value` mean and std, its `days` and `mean_common_symbols`, and its status.
These show whether two signals keep ranking the same symbols alike. With exactly one explicit
target, `monthly` adds a 24-month IS breakdown: check that sign and magnitude are stable. A low
full-window value with a few strongly aligned months is not stable complementarity.
`insufficient_overlap`, `source_unavailable`, `run_not_completed`, incomparable windows or a small
sample are evidence gaps, never zero correlation. All statistics cover the IS window only.

Interpret in this order:

1. Align each Factor's predicted direction and horizon from its card first. A high absolute value
   usually means redundant ranking. A strongly negative value can be a reversed duplicate, a
   conflicting mechanism or an opposite exposure; it is not automatically useful diversification.
2. Strong complementary evidence needs a low value correlation together with a different
   mechanism, data, style and failure state.
3. Value correlation cannot identify Size, liquidity, momentum, reversal, beta or volatility
   exposure. Those claims need Factor Card or direct server style evidence.

The playbook's reference cuts mark redundancy: at or above the same-signal cut two Factors repeat
one ranking, and the grouping cut keeps at most one Factor per cluster. Below the distinct cut a
pair is a candidate for complementarity, not proof of it. Do not invent another universal
threshold. Report actual values, samples and relative relations, and base each selection on
agreement across evidence types rather than one coefficient.

## 4. Build the composition from Factor Cards

First decide whether each candidate is valid on its own: its mechanism matches what it predicts,
its direction is explainable, important Health or coverage issues are explained, and quantile, IC,
decay or other evidence supports it. Mark thin evidence unverified; a low-correlation story alone
does not earn a place.

Then start from a core Factor and fill a marginal-contribution table for each candidate:

| Layer | Factor Card or pair evidence | Composition question |
| --- | --- | --- |
| Data quality and applicability | Health, coverage, missingness pattern, valid cross-section | Does it shrink or change the effective universe together with the others? |
| Mechanism and target | Mechanism, input timing, direction, horizon | Does it add an explainable new predictive source? |
| Prediction quality | Quantile monotonicity, IC, long and short legs, tail concentration | Does it shore up the core's weak side instead of repeating the same return leg? |
| Signal complementarity | Factor value cross-sectional Spearman | Do the rankings repeat? |
| Time behavior | Decay, lag-1 autocorrelation, stability, applicable states | Does the signal stay useful under one rebalance setting? |
| Style and implementation | Size, liquidity, momentum or reversal, beta, volatility, turnover, cost | Does it reduce exposure or implementation concentration? |
| Failure and path | Sub-windows, abnormal periods, drawdown, failure conditions | Would the Factors fail in the same regime? |

Build as core Factor → core gap → supplementary Factor. Each added Factor must bring a new
predictive source or risk function; stop when additions bring only repeated exposure and cost.
Different names or Families do not prove independence, and single-Factor marginal charts do not
replace pairwise correlation.

Decision rules:

- Exclude first: failed admission, an unexplained critical Health or coverage problem, an
  unexplainable direction or insufficient evidence. Low correlation cannot rescue an invalid Factor.
- A candidate fills at least one declared gap without adding a worse data, style, liquidity,
  turnover or failure concentration.
- Among highly redundant candidates keep the one with better evidence quality, stability and
  implementation; do not keep both to raise the count.
- Horizons may differ, but one predeclared `rebalance_bars` must reasonably carry them. A signal
  that has clearly decayed before the rebalance does not belong in that Strategy.
- Do not collapse the card into an undefined total score. Keep per-layer evidence and marginal
  reasons so that selections, exclusions and evidence gaps stay auditable.

Freeze the specification from the selected cards: `ranking` from quantile monotonicity, effective
cross-section and tail concentration; `strategy_type` from the direction and stability of the long
and short legs; `rebalance_bars` from horizon, decay, autocorrelation, turnover and cost. Set other
specification fields only when the live schema supports them, never by enumerating settings and
picking the best backtest curve.

## 5. Freeze weights and specification

Factor weights are signal weights, not asset weights or Portfolio capital weights.

- The AI's final recommendation always uses equal weights: omit `weighting` and the server
  derives them.
- Record or execute non-equal weights only when the user explicitly supplies them. Label them
  user-specified, never an AI recommendation, and show the equal-weight version of the same
  Factors beside them.
- User `weighting.weights` are finite positive numbers that sum exactly to 1, one per entry of the
  ordered `factor_references`.

Equal weights do not mean equal risk contribution. If equal weights concentrate mechanism, style,
liquidity or implementation risk too much, remove or replace the Factor without marginal value
and weight the rest equally. If that is still unacceptable, conclude that the candidate set does
not make a Strategy. Never optimize weights to hide concentration or redundant Factors.

A Factor's name does not decide its direction; the Strategy applies the direction QuantAI
evaluated. Never enumerate parameters or compositions and keep the best in-sample curve.

## 6. Output and handoff

A design states the goal, candidate scope, Factor Cards, the pairwise value-correlation table with
common samples and statuses, the core gap, marginal contributions, selection and exclusion
reasons, ordered Factors, the equal-weight recommendation, the Strategy specification, evidence
gaps and a validation plan. A design-only request stops here.

The validation plan preregisters, in the decision's `research_note`, one complete equal-weight
composition and a small number of controls with explicit hypotheses, such as the core Factor alone
or the composition without one suspected redundant Factor. A request for one exact Strategy covers
only that definition and its Run; preregistered controls run when the user's goal includes
validating the composition, as in the playbook's multi-factor order. Never iterate over
compositions, correlation cuts, weights or settings and keep the best in-sample result.

Once execution is authorized, freeze identities, order, weights and settings and continue with the
[Canonical Strategy Workflow](ordinary-strategy-workflow.md). After the backtest, hand the exact
`strategy_run_id` to `$strategy-analysis`; never assemble an authoritative Strategy result from
single-Factor metrics.
