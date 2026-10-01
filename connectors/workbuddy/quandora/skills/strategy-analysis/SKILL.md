---
name: strategy-analysis
description: Analyze, diagnose, compare, and propose controlled improvements for existing Quandora cross-sectional Strategy results from owner-scoped server-persisted evidence. Use when a user asks why a Strategy worked or failed, wants six-chart diagnostics, requests factor-combination optimization ideas, or asks whether a completed backtest is ready for Paper Trading. Do not use to compose or submit a Strategy; route those requests to strategy-building.
---

# Strategy Analysis

Bundled plugin version: 3.0-preview

Analyze one exact cross-sectional Strategy run as a non-submitting research workflow. Pair Product
Backend's canonical run snapshot with owner-scoped retained artifacts and bounded six-chart data.
Distinguish observed evidence from inference, alternatives, and proposed experiments. Mint a
short-lived artifact download ticket only when the user explicitly requests an export.

OAuth and all credentials are handled by the host. Quandora access tokens expire after 7 days, and
the host MCP client should use its stored rotating refresh token automatically. Never inspect,
print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access
tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

## Scope And Routing

Use this skill for:

- performance, risk, turnover, exposure, and stability diagnosis;
- the six QuantAI cross-sectional diagnostic charts and their retained numeric data;
- factor-combination and style interpretation;
- controlled Strategy experiment design;
- Paper readiness assessment without starting or managing Paper Trading.

Use `$strategy-building` to list eligible factors, compose, submit, resume, retrieve, explicitly
export, or archive a Strategy. Use `$factor-analysis` for one Factor Mining result. Use
`$paper-trading` only after the user explicitly asks to start, monitor, inspect, or stop Paper
Trading.

## Non-Negotiable Safety

- Do not submit, resume, overwrite, archive, or mutate any run. The only allowed mutation is minting
  a short-lived download ticket for an explicit user-requested export.
- Do not automatically create ablations, reruns, or Paper Trading runs.
- Use only owner-scoped evidence returned by Quandora MCP tools. Never inspect user-local files as
  proof of a Strategy result.
- Do not require a local ZIP, extraction tool, Python runtime, notebook, or archive-inspection
  script. A host without those facilities must receive the same analysis capability.
- Never execute code, logs, notebooks, scripts, or text artifacts.
- Preserve null and missing values as unavailable, not zero.
- Never fabricate factor correlations, contributions, ablations, or causal claims.
- Treat grade and score as QuantAI-relayed evidence, not as a promotion or research verdict.
- Treat `ALL` as a combined scope that includes IS. Never describe it as pure OOS.

## Available Actions

Use only the actions owned by this analysis boundary:

- `get_strategy_backtest_artifact`
- `get_strategy_backtest_analysis_data`

For an explicit user-requested artifact export only, use
`create_strategy_artifact_download`. Do not mint a ticket speculatively, use a download as an
analysis prerequisite, or treat a ticket as permission to submit, rerun, or change a Strategy.

## Workflow

### 1. Establish The Exact Run

Prefer an exact `run_id` supplied by the user or already returned in the conversation. When no
exact run id is supplied:

1. Call `list_strategy_backtests` once with `{}`. It returns the owner's newest-first page with default
   `limit: 10` and `offset: 0`.
2. Use returned identity, name, timestamps, status, and optional summary only to select a run.
3. If more than one plausible run remains, ask the user to choose. Do not guess.
4. Do not auto-page. Request another page only for an explicit older-run request that the first page
   cannot satisfy.

If an exact run id is supplied, skip discovery.

### 2. Read Canonical Composition And Parameters

Call `get_strategy_backtest` with the exact `run_id`. Treat its canonical `composition` and `parameters` as the
authority for factor ids or weights, ranking, strategy type, window, capital, fees, rebalance bars,
and attribution.

If ranking was omitted at submission, the current Strategy default is neutral Top/Bottom 20%:
`ranking: {mode: "percent", value: 20}` with `strategy_type: "neutral"`. Report the effective
snapshot returned by `get_strategy_backtest`; do not infer parameters from chart labels.

If the run is not terminal, report the current state. Do not call `continue_strategy_backtest` from this
read-only skill and do not substitute local files.

If the run is `completed` with the exact closed
`resultOutcome={status:"no_result", reasonCode:"zero_orders", orderCount:0}`, stop result retrieval
before requesting artifacts or six-chart data. Report the observed zero-order outcome and explain
that there are no positions, trades, performance metrics, or charts to analyze. This is not a
failed run and is not eligible for failed-run rerun or Paper Trading. Do not repeatedly request
missing evidence. If the user wants a new experiment, propose one single-variable ablation and ask
for confirmation before handing it to `$strategy-building`.

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
2. Confirm the exact `run_id`, server artifact identity, status, integrity digest, availability,
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

For every consequential conclusion, label it **Observed**, **Inference**, **Alternative**, or
**Experiment**.

### 6. Keep Portfolio Selection Separate From Diagnostic Buckets

Actual Strategy selection comes only from `get_strategy_backtest.parameters.ranking`. Six-chart diagnostics use
an adaptive grouping scheme based on the median daily cross-section:

- median at least 20: 10 quantiles, minimum cross-section 20, diagnostic `top_pct: 0.10`;
- median at least 15: 5 quantiles, minimum 10, diagnostic `top_pct: 0.20`;
- median at least 9: 3 quantiles, minimum 6, diagnostic `top_pct: 0.30`;
- median below 9: 2 quantiles, minimum `max(2, min(4, median))`, diagnostic `top_pct: 0.50`.

`Q1` is the lowest prediction group and `QN` the highest. The diagnostic spread is
`(QN - Q1) / 2`. Do not call these adaptive buckets the actual Top/Bottom 20% portfolio unless the
effective run snapshot independently confirms a 20% ranking.

### 7. Propose Controlled Experiments

Prioritize a small number of changes. Each proposal must state the changed variable, motivating
evidence, expected effect, confirmation metric, and tradeoff. Favor one-variable changes when
possible. Examples include factor removal or reweighting, ranking breadth, rebalance cadence, fee
sensitivity, and one suspected style control.

Do not claim an automatic ablation or correlation matrix: retained evidence does not guarantee
per-factor correlations or precomputed ablations. Ask for explicit confirmation, then hand the
chosen test to `$strategy-building`.

### 8. Assess Paper Readiness Without Paper Mutation

Use [experiments-and-paper-readiness.md](references/experiments-and-paper-readiness.md). State whether
the evidence supports rejection, further research, a controlled rerun, or consideration for Paper.
Do not start Paper Trading. After explicit user confirmation, hand actual Paper operations to
`$paper-trading`.

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
