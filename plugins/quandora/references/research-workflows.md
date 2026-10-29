# Research intent and evidence

Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, Portfolio Building and
Portfolio Analysis work on backtests. Portfolio Trading Analysis owns forward-test management
and analysis. A Factor supplies a prediction; a Strategy turns admitted Factors into trading
rules; a Portfolio allocates initial capital between exact Strategies.

A Family (FactorFamily, StrategyFamily, PortfolioFamily) is the immutable lineage tree that holds
each version of one idea. A LibraryFolder is only the user's classification of finished works;
moving a work between LibraryFolders never changes its Family.

## Select the workflow by intent

| User intent | Owner | Action boundary |
| --- | --- | --- |
| Author, validate or backtest a Factor | `$factor-mining` | Use the scoped input contract and authorized submission |
| Diagnose an existing Factor | `$factor-analysis` | Read exact evidence; propose experiments without submitting |
| Select eligible Factors, create or backtest a Strategy | `$strategy-building` | Preserve immutable definitions and explicit backtest intent |
| Diagnose a Strategy or produce its research card | `$strategy-analysis` | Read exact evidence; distinguish signal and implementation issues |
| Select Strategies, allocate capital, build, share or favorite a Portfolio | `$portfolio-building` | Separate design-only, composition, backtest and sharing intent |
| Compare a Portfolio backtest with its actual members | `$portfolio-analysis` | Read existing evidence; no automatic ablation or rerun |
| Manage Simulation accounts/runs or analyze forward evidence | `$portfolio-trading-analysis` | Analysis-only is read-only; explicit Simulation management uses supported writes; real Live is read-only |

An analysis request does not authorize a new backtest, reversal, account, sharing grant or Trading
change. Carry already-authorized experiment scope through a handoff to the relevant builder;
do not ask again merely because the Skill changes. An optimization request uses a bounded set of
controlled experiments and does not justify indefinite search. Never silently change supplied
members, weights, data, dates or objectives. Explain a real admission failure without replacing
the rejected inputs.

For design-only requests, stop at the proposed definition and validation plan. For exact supplied
members and weights, preserve that intent; an incomplete research card narrows conclusions but
does not invent an additional product admission gate. Bare lists use one bounded page, not a
full research workflow. Scale the answer and evidence reads to the question.

## Preserve evidence across handoffs

Carry the user goal and authorized actions together with:

- exact Family, immutable definition, research Run and account/Trading Run identities as applicable;
- actual Factor and Strategy lineage, owner/Official/Publication/Share context and read selectors;
- observation window, data cutoff, sampling frequency, valuation time and evidence readiness;
- units, net/gross returns, fees/funding, initial-capital allocation and exposure conventions;
- observed facts, inferences, alternatives, missing evidence and the proposed controlled change.

Do not resolve an immutable object by display name or replace the actual source Run with its
latest, nearby or better-performing run. Use [Name discovery](object-discovery.md) when needed.
Shared child research remains in its returned access context; visibility is not ownership or
permission to compose those children into Mine. Do not bypass a grant with owner tools.

`IS`, `OOS` and `ALL` retain their returned meanings; ALL includes IS. Only analyze windows the
public evidence actually exposes. Historical OOS is still a backtest. Forward evidence starts
after the selected definition was frozen and the actual run began; a historical replay does not
become forward evidence. Changed definitions or newly tuned versions require a separate segment.

Use the evidence ladder: **Observed**, **Inference**, **Alternative**, **Experiment**. Missing,
pending or null evidence is unavailable, never zero. Do not infer causality from a backtest or
equate a provider grade with a research verdict. Do not fetch substitute prices or reconstruct
authoritative product metrics. Simple differences between comparable returned metrics may be
reported as derived comparisons, with the sources and units stated.

## Capability-aware analysis

| Claim | Required evidence | Available read path | If insufficient |
| --- | --- | --- | --- |
| Factor validity and decay | Exact authorized Factor Card, Health and numeric charts | Factor Analysis owner/official reads | Report the exposed scope and missing sections |
| Strategy logic and implementation | Frozen specification, factor references, execution window, retained artifacts and six-chart data | Strategy Analysis reads | Limit each claim to its ready artifacts |
| Portfolio result and member comparison | Exact PortfolioRun, actual source StrategyRuns, aligned windows and canonical metrics/curves | `get_portfolio_backtest`, `get_portfolio_backtest_result`, authorized member research | Report aggregate results independently; no invented same-window comparison |
| Cross-Strategy prediction/rank correlation | Synchronized predictions on common dates/assets and a declared calculation | No dedicated guaranteed public projection | Report unavailable; individual decile charts are not raw joint predictions |
| Historical overlap or cross-side conflict | Synchronized signed holdings and normalization for each member | Retained artifacts only when they actually contain the needed history | Do not infer historical holdings from trade lists or current positions |
| Residual correlation, covariance or risk contribution | Common risk factors, complete comparable series, model/window and weight convention | No dedicated guaranteed public projection | Do not manufacture a matrix, regression or optimizer output |
| Forward finance and execution | Exact account/run, authoritative net book, actual observation times and record coverage | Portfolio Trading Analysis net-ledger or real Live reads | Preserve WAITING/INCOMPLETE/null and distinguish recent records from full history |

Read only the artifacts needed for a consequential claim. Ready headline results can still be
useful when advanced evidence is absent. An unavailable metric does not grant authority to
submit a new experiment or to require a local runtime, ZIP, notebook or export.

Predeclare the objective, baseline and validation window before optimizing. If selection and
evaluation reuse the same sample, label the result in-sample exploratory evidence. Do not claim
out-of-sample improvement or global optimality from that comparison.

Use the user's language. Preserve exact schema names and identities where they aid verification;
do not force every answer into a full report or create files unless requested.
