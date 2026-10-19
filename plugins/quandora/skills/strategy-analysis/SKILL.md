---
name: strategy-analysis
description: Analyzes existing Quandora cross-sectional Strategy results from owned or authorized Publication-context evidence. Use when the user asks about pass/fail, six-chart diagnosis, reusable Strategy research cards, controlled improvements, or Paper readiness. Do not use to compose or submit a Strategy.
---

# Strategy Analysis

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery and the once-per-session release check; preserve existing update authority.
Follow [Research intent and evidence](../../references/research-workflows.md) for backtest/forward
scope, capability-aware conclusions and authorization-preserving handoffs.

Analyze one exact cross-sectional Strategy run as a non-submitting research workflow. Pair the
canonical owned run snapshot with retained artifacts and bounded six-chart data, or use the
authorized Publication projection without assuming that it exposes the same private evidence.
Distinguish observed evidence from inference, alternatives, and proposed experiments. Mint a
short-lived artifact download ticket only when the user explicitly requests an export.

Use only the configured `quandora` MCP connection. Never ask the user to paste secrets into
chat.

For archive waits, stale `sync_failed`, inline `too_large`, or bundle channel limits,
follow [Strategy delivery recovery](../../references/strategy-delivery-recovery.md).
For named objects, follow [Name discovery](../../references/object-discovery.md) to resolve exact identities.

## Scope And Routing

Use this skill for:

- performance, risk, turnover, exposure, and stability diagnosis;
- the six QuantAI cross-sectional diagnostic charts and their retained numeric data;
- factor-combination and style interpretation;
- controlled Strategy experiment design;
- Paper readiness assessment without starting or managing Paper Trading.

Use `$strategy-building` to list eligible factors, compose, submit a new Run, retrieve, explicitly
export a Strategy. Use `$factor-analysis` for one Factor Mining result. Use
`$portfolio-trading-analysis` only after the user explicitly asks to start, monitor, inspect, or stop Paper
Trading.

## Non-Negotiable Safety

- Do not submit, resume, overwrite, archive, or mutate any run. The only allowed mutation is minting
  a short-lived download ticket for an explicit user-requested export.
- Do not automatically create ablations, reruns, or Paper Trading runs.
- Use only evidence returned by Quandora MCP tools. Never inspect user-local files as proof of a
  Strategy result.
- Do not require a local ZIP, extraction tool, Python runtime, notebook, or archive-inspection
  script. A host without those facilities must receive the same analysis capability.
- Never execute code, logs, notebooks, scripts, or text artifacts.
- Preserve null and missing values as unavailable, not zero.
- Treat Factor input definitions and D/D+1 alignment as owned by the Factor Plugin Contract. Do
  not use its current task scope to rewrite a frozen Factor or StrategyRun.
- Never fabricate factor correlations, contributions, ablations, or causal claims.
- Treat grade and score as QuantAI-relayed evidence, not as a promotion or research verdict.
- Treat `ALL` as a combined scope that includes IS. Never describe it as pure OOS.

## Primary And Discovery Actions

Use these primary analysis actions:

- `get_strategy_backtest_artifact`
- `get_strategy_backtest_analysis_data`
- `get_community_strategy_research`, `read_community_research_artifact` for authorized Publication context only.

Read-only discovery uses `list_strategy_folders`, `list_strategies`,
`list_strategy_backtests`, `get_strategy_backtest`, and `get_strategy`. They locate one canonical
Run; they do not authorize a
continue, rerun, archive, or other Strategy mutation.

For an explicit user-requested artifact export only, use
`create_strategy_artifact_download`. Do not mint a ticket speculatively, use a download as an
analysis prerequisite, or treat a ticket as permission to submit, rerun, or change a Strategy.

## Workflow

### 1. Establish The Exact Run

For Community child research, keep the exact Publication and returned child selectors. Read the
contextual projection/artifacts; never pass those IDs to owner tools or assume private source is
available. If the projection omits a required field, narrow the card rather than bypassing access.
The owner workflow below applies only to owned results.

Prefer an exact `strategy_run_id` supplied by the user or returned in the conversation.
Pass it as `strategy_run_id` to every canonical Run, artifact, analysis, and export action.
Internal command IDs, Folder IDs, and immutable Strategy IDs are different selectors.

If no Run is known, resolve the Strategy through `list_strategy_folders` and
`list_strategies(strategy_folder_id=...)`, then call
`list_strategy_backtests(strategy_id=..., page_size=...)`. These lists do not accept `query`
or `filters`. Select using returned names, identities, timestamps, and states. Ask only if more
than one plausible target remains. Preserve parent selectors/page size and copy `next_page_token`
byte-for-byte for needed continuation; do not auto-page or invent a global Run search.
Skip discovery when the exact Run is supplied.

### 2. Read Definition and Execution Evidence

Read `get_strategy_backtest(strategy_run_id=...)` for state and its exact `strategy_id`, then
`get_strategy(strategy_id=...)` for persisted `specification` and `factor_references`.
The Run's `product_summary` is a safe summary, not a replacement for retained evidence.
Do not assume the Run detail includes legacy composition/parameter wrappers.

Use the definition for factor selection, weighting, ranking, direction, and rebalance choices.
Use the Run's retained artifacts and analysis overview for the effective execution window and
other execution parameters actually returned. Do not fill missing values from remembered defaults
or confuse diagnostic chart buckets with the Strategy's selection specification.

If the Run is not terminal, report its state without submitting or continuing anything.
If retained evidence explicitly reports a terminal zero-order/no-result outcome, explain that
missing trades or performance charts are not a transient gap and do not repeatedly request them.
A new experiment is a separate authorized task through `$strategy-building`.

### 3. Read Core Server Artifacts

Use `get_strategy_backtest_artifact` for the exact run. Start with `summary` and `performance`, then request only
the evidence needed for the question:

- `equity_curve` and `drawdown_curve` for path, concentration, and recovery;
- `turnover_curve` and `exposure_curve` for implementation intensity and neutrality;
- `attribution` and `signal_return_curves` for mechanism claims when available;
- `status`, `result`, `orders`, or `trades` only when a specific claim requires them.

Treat each artifact status independently. Missing, pending, unavailable, or null evidence must stay
explicitly missing. Do not use `logs` or `code` unless the user explicitly asks for inert text
review; never execute either.

### 4. Read Six-Chart Numerical Evidence

1. Call `get_strategy_backtest_analysis_data` with `chart: "overview"`.
2. Confirm the exact `strategy_run_id`, server artifact identity, status, integrity digest, availability,
   declared window, parameters, cross-section summary, missing styles, and chart catalog.
3. Request only the chart pages needed for the diagnosis. Follow `next_offset` only for the same run
   and chart until the required evidence is complete.
4. Preserve returned point order, integer values, finite numbers, and nulls exactly.

The six-chart route is the numerical analysis path. Do not request a Result Bundle, PNG, download
ticket, storage URL, or local file to replace it. On `pending`, `not_available`, `too_large`, or
`integrity_failed`, report the exact evidence limitation and continue only with independent server
artifacts that remain trustworthy. `not_available` with `reason_code=no_result_zero_orders` is
terminal zero-order evidence, not a transient gap; stop without retries or substitute evidence.

### 5. Diagnose The Result

Use the [Strategy logic card](references/strategy-logic-chain.md) for reusable candidate evidence
and exact Portfolio-member diagnosis. Return that card to `$portfolio-building` for selection or
`$portfolio-analysis` for an actual source Run, preserving the task's original authorization.

Read [artifacts-and-metrics.md](references/artifacts-and-metrics.md) and
[six-chart-diagnostics.md](references/six-chart-diagnostics.md). Evaluate:

- headline return, Sharpe, Sortino, drawdown, win/loss behavior, and fees;
- equity and drawdown shape, time concentration, and recovery;
- daily turnover using the Strategy single-sided `/2` convention;
- gross and net exposure and whether nominal neutrality held in practice;
- factor composition and whether explicit weights created concentration;
- all available chart families, including quantile ordering, long/short style, exposure, decay,
  prediction-style correlation, and turnover;
- evidence gaps and plausible market, liquidity, size, or implementation alternatives.

If retained lineage suggests a `binance_intraday` availability, normalization, or comparability
concern, state it as a Factor-level hypothesis and hand exact Factor diagnosis to
`$factor-analysis`. Do not copy the field registry, shift retained Strategy evidence, or claim the
current Factor Plugin Contract proves what data was available to the historical run. Current
`runtime_rules.research_guidance` can identify known normalization, redundancy, or default
Paper-ready risks, but it remains interpretation support rather than historical execution evidence.

For every consequential conclusion, label it **Observed**, **Inference**, **Alternative**, or
**Experiment**.

### 6. Keep Portfolio Selection Separate From Diagnostic Buckets

Actual Strategy selection comes from the exact immutable `get_strategy` specification and
retained execution evidence. Interpret
the separate adaptive diagnostic grouping only from the returned chart parameters and the rules in
[six-chart-diagnostics.md](references/six-chart-diagnostics.md). Never relabel diagnostic buckets
as the actual portfolio selection unless the immutable Strategy specification confirms it.

### 7. Propose Controlled Experiments

Prioritize a small number of changes. Each proposal must state the changed variable, motivating
evidence, expected effect, confirmation metric, and tradeoff. Favor one-variable changes when
possible. Examples include factor removal or reweighting, ranking breadth, rebalance cadence, cost
exposure, and one suspected style control.

Do not claim an automatic ablation or correlation matrix: retained evidence does not guarantee
per-factor correlations or precomputed ablations. Hand an explicitly requested or already-authorized
test to `$strategy-building`; ask only for missing experiment choices or authorization.

### 8. Assess Paper Readiness Without Paper Mutation

Use [experiments-and-paper-readiness.md](references/experiments-and-paper-readiness.md). State whether
the evidence supports rejection, further research, a controlled rerun, or consideration for Paper.
Do not start Paper Trading. For authorized Paper preparation, hand off through
`$portfolio-building`; after its backtest, use the PB automatic association before any extra start.

## Output Contract

Answer in chat by default. Create a report file only when explicitly requested. Use this order:

1. exact run identity, effective composition and parameters, and evidence quality;
2. concise performance and risk summary;
3. metric, curve, and six-chart diagnosis;
4. factor-combination and style mechanism with alternatives;
5. risks and evidence gaps;
6. prioritized controlled experiments;
7. decision and optional user-confirmed handoff.

Use the user's language for the answer even though this skill package is written in English.

## References

- [Server evidence contract and trust rules](references/evidence-contract.md)
- [Strategy artifacts and metric semantics](references/artifacts-and-metrics.md)
- [Six-chart diagnostics](references/six-chart-diagnostics.md)
- [Experiments and Paper readiness](references/experiments-and-paper-readiness.md)
