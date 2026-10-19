# Select members and initial capital weights

Load for delegated selection or design, not for every exact composition request. Follow the
[shared evidence contract](../../../references/research-workflows.md) and
[neutrality framework](../../../references/portfolio-neutrality.md).

## Fix the question and candidate scope

Translate the objective into an assessable comparison: improve net risk-adjusted return, reduce
drawdown/recovery time, reduce a named concentration, or improve behavior in specified states.
Use supplied constraints; ask only for a material missing preference that changes the choice.
Predeclare the core Strategy and a same-member equal-initial-capital baseline. A retrospective
best member can be an additional labeled reference, not a replacement chosen to make results win.

For user-selected members, evaluate those members without silently replacing them. For delegated
selection, discover a bounded authorized candidate set and disclose the scope actually inspected.
Do not claim a global optimum or automatically exhaust the user's entire inventory.

## Reuse Strategy Cards

Use `$strategy-analysis` and its
[Strategy logic card](../../strategy-analysis/references/strategy-logic-chain.md) for each relevant
candidate: immutable identity, actual research Run/window, mechanism, definition, exposure,
return/risk, cost, concentration, missing evidence and failure conditions. Reuse matching evidence
from the current task; do not independently reimplement the single-Strategy diagnosis.

An Alpha candidate needs evidence for its own logic and net implementation, not merely low
correlation. Distinguish rejected candidates from unverified ones. Evidence gaps limit confident
recommendation; they do not invent a new backend eligibility gate for an explicitly requested
legal composition. An explicitly requested hedge is evaluated against its declared risk function,
not solely standalone profitability. Shared research visibility does not make a member reusable.

## Build around a specific risk gap

1. Select a credible core whose evidence is most complete for the goal.
2. Identify its principal weakness: exposure, state dependence, drawdown, crowding or implementation.
3. Add an independently credible member that addresses that weakness.
4. Add further members only when each contributes an explainable new source or risk function.
5. Stop when added complexity and costs are not justified; five members are not a target.

Use the shared mechanism/prediction/holdings/exposure/outcome framework. Report unavailable
pairwise evidence explicitly. Do not infer a correlation matrix from single-Strategy diagnostics
or label same-Factor parameter variants independent solely because their names differ.

## Allocate initial capital

The legal range is one to five distinct exact Strategies; a one-component Portfolio remains valid.
Equal initial capital is the default research baseline, not a claim of equal risk contribution.
Custom weights follow explicit user intent or an explained risk budget backed by comparable
windows, exposure and cost evidence. Preserve exact provided weights; do not silently optimize.

Do not default to in-sample maximum-Sharpe optimization. Inverse volatility or risk balance, when
data and calculation support exist, are research candidates to compare with equal capital.
State any user-specified concentration limits; do not invent arbitrary universal thresholds.
Initial weights can drift with sleeve performance and do not imply daily rebalancing or leverage.

Record selection/evaluation windows and overfitting limits. A custom-versus-equal comparison
requires an existing comparable result or an authorized additional experiment; merely selecting
a baseline does not authorize creating it. The backend resolves actual source Runs at submission;
recheck the returned source lineage and interval before drawing a post-backtest conclusion.

## Handoff

For design-only intent, return proposed members, initial weights, reasons, rejected/unverified
alternatives, evidence gaps and a validation plan. For authorized execution, freeze the exact
Strategy identities, order and positive decimal weights, then follow Portfolio Building's
canonical lifecycle. Send the actual completed PortfolioRun to `$portfolio-analysis` when a
research verdict is requested. Keep automatic monitoring separate from research validation.
