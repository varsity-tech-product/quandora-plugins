# Select members and initial capital weights

Load for delegated selection or design, not for every exact composition request. Follow the
[shared evidence contract](../../../references/research-workflows.md) and
[neutrality framework](../../../references/portfolio-neutrality.md); the latter is required when a
candidate is a cross-sectional long/short or market-neutral Strategy.

## 1. Fix what the Portfolio must improve

Write the objective as a testable claim relative to the single Strategies, for example:

- lower drawdown without a material loss of return;
- higher net Sharpe at the same risk budget;
- less Factor, sector, symbol or liquidity concentration;
- less co-movement in stress periods and shorter drawdown recovery;
- more independent predictive sources, not more Strategies.

Use supplied constraints; choose missing settings from the research context and returned
candidates. Record why in `research_note.hypothesis` for a new direction or `change_summary`
otherwise. Predeclare the core Strategy and the comparison baselines before reading any Portfolio
result. A retrospective best member can be an additional labeled reference, not a replacement
chosen to make the result win. Never change the baseline, a member version or the window afterwards.

For user-selected members, evaluate all of them without silent replacement. For preference-based
selection, apply the preferences first. For delegated selection, discover a bounded authorized
candidate set, disclose the scope actually inspected, and choose only among candidates read with
comparable evidence. Do not claim a global optimum or automatically exhaust the user's inventory.

## 2. Freeze each candidate's evidence

Each candidate is an existing exact immutable Strategy evaluated on an exact StrategyRun. Before
reading any Portfolio result, freeze its `strategy_id`, the evaluated `strategy_run_id`, its
definition, data cutoff and comparison window. Prefer the Run whose window matches the Portfolio's
standard interval; label any difference. All comparisons use one window, frequency, cost
convention and valuation time.

Portfolio Building does not change members. Factors, universe, selection, long/short proportions,
rebalance, fees, leverage and backtest window define a candidate version; any change is another
version, never a search inside this workflow. When several versions compete and neither the user
nor a rule declared in advance identifies one, list them and stop that selection rather than
choosing by curve. A member that qualifies only after retuning, a new window or another Run is
excluded here; the retuning idea is a separate `$strategy-building` experiment.

## 3. Reuse Strategy Cards

Use `$strategy-analysis` and its
[Strategy logic card](../../strategy-analysis/references/strategy-logic-chain.md) for each relevant
candidate. Record with the same structure: identity, source, exact Run, frozen settings, window
and cutoff; data, universe, Factors, ranking, selection and rebalance; long, short, gross, net,
Beta and style exposure; return, volatility, Sharpe, drawdown and recovery; turnover, fees,
funding, capacity and liquidity; whether returns concentrate in a few periods, symbols or one
side; evidence gaps and failure conditions. Reuse matching evidence from the current task; do not
reimplement the single-Strategy diagnosis. The card judges only evidence the frozen version
already has; a parameter that might improve the curve is a research hypothesis outside this workflow.

## 4. Standalone validity comes first

Low correlation cannot rescue an invalid Strategy. A candidate needs:

- consistency between economic logic, data, tradable universe, Factors, ranking and rebalance;
- cross-sectional quantile, ranking monotonicity, out-of-sample or other evidence supporting its
  prediction logic;
- returns not driven mainly by one period, symbol, direction or abnormal fills;
- identifiable return after fees, funding and turnover;
- holdings and exposure that do not persistently drift from the definition;
- enough rebalances and market states to support a comparison.

Mark a candidate with thin evidence unverified; short-run low correlation does not admit it.
A failing candidate is excluded, never added as a hedge leg. An explicitly requested hedge is
evaluated against its declared risk function. Evidence gaps limit a confident recommendation;
they do not invent a backend eligibility gate for an explicitly requested legal composition.
Shared research visibility does not make a member reusable.

## 5. Judge complementarity in five layers

| Layer | Question | Key evidence |
| --- | --- | --- |
| Return source | Do they earn different kinds of money? | Economic hypothesis, Factor family, data source |
| Prediction | Do they rank alike at the same time? | Prediction-value and cross-sectional rank correlation, signal decay |
| Asset selection | Do they keep trading the same symbols? | Long-long overlap, short-short overlap, cross-side conflict |
| Risk exposure | Do they share one hidden bet? | Beta, style, sector, symbol, horizon, liquidity |
| Return path | Do they lose together in bad periods? | Rolling and downside correlation, drawdown overlap, recovery time |

Call members strongly complementary only when the return source or actual asset selection is
independent and stress periods show no persistent co-movement. Low full-sample return correlation
is only a first screen. Same-Factor parameter variants on the same universe and a similar
rebalance usually restate one bet, whatever their names. Report each unavailable layer as unavailable;
do not infer a correlation matrix from single-Strategy diagnostics.

## 6. Build around a core and its gap

1. Choose as core the Strategy with the clearest logic, most reliable net return and most complete
   evidence for the goal.
2. Name its main weakness: trend reversal, crowding, liquidity, sector concentration, short
   squeeze, exposure or another risk.
3. Add a standalone-valid second member with a different return source in that weak scenario.
4. A third to fifth member must bring a new independent predictive source or risk buffer.
5. Stop when a new member does not raise effective independence and only dilutes return or adds cost.

Do not admit members mechanically by historical Sharpe rank. A complementary design usually has
two to five members; more members do not mean better diversification. The legal product range is
one to five distinct exact Strategies, and a one-component Portfolio remains valid.

## 7. Equal initial capital is the recommendation

Every Portfolio you design or recommend gives each of its N members 1/N of initial capital,
frozen before reading any Portfolio result. Equal capital is the actual recommendation, not only a
benchmark. Never recommend maximum-Sharpe, minimum-variance, inverse-volatility, risk-parity,
target-volatility or other in-sample-optimized weights, and never generate several weight sets to
keep the best. Risk and exposure differences select members, explain the Portfolio or reject the
candidate set; they do not tune weights.

Record or create non-equal weights only when the user explicitly supplies them. Label them
user-specified, never an AI recommendation, keep them in a separate column from the equal-weight
recommendation, and compare them with the same members at equal weight. That comparison uses an
existing comparable result or an authorized additional experiment; naming the baseline does not
authorize creating it. If a product constraint makes equal weights impossible, state the conflict
and stop; do not derive substitute weights.

Equal capital does not mean equal risk contribution. Initial weights can drift with sleeve
performance and do not imply daily rebalancing or leverage. When members differ greatly in gross
exposure, volatility or correlation, report capital weights together with risk contribution where
the shared framework's evidence supports it. If equal capital concentrates risk contribution,
gross, Beta, Factor, symbol or liquidity exposure unacceptably:

1. check whether the member causing it brings an independent return source;
2. remove or replace a member without marginal value and weight the rest equally again;
3. if still unacceptable, conclude that the candidate set does not make a Portfolio.

Never change Strategy settings or member weights to hide concentration. When the member count
changes, weight the final members equally; do not inherit old weights. Express 1/N plainly;
precise decimals add false certainty. Consider costs, funding, capacity and rebalance timing
together with the member choice.

## 8. Final admission test and handoff

Each member answers four questions with evidence:

1. Why might it work on its own?
2. Which specific gap of the Portfolio does it fill?
3. Does its added return or risk buffer cover its added cost and complexity?
4. Does it qualify without retuning, a new window or another Run?

A member without evidence for any question is not a confident selection.

For design-only intent, return the objective and baselines, candidate Strategy Cards, standalone
screen, the five-layer complementarity matrix, selected and rejected members with reasons, equal
weights with risk contribution and concentration, evidence gaps and failure conditions, and a
validation plan. For authorized execution, freeze the exact Strategy identities, order and
weights, then follow Portfolio Building's canonical lifecycle. A run failure, missing evidence or
unaligned member windows never triggers an automatic member swap or resubmission. The backend
resolves actual source Runs at submission; recheck the returned source lineage and interval before
drawing a post-backtest conclusion, and send the completed PortfolioRun to `$portfolio-analysis`
for the incremental-value verdict.
