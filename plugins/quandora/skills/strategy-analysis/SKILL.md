---
name: strategy-analysis
description: Analyze, diagnose, compare, and propose controlled improvements for existing Quandora cross-sectional Strategy results from owner-scoped server-persisted evidence. Use when a user asks why a Strategy worked or failed, wants six-chart diagnostics, requests factor-combination optimization ideas, or asks whether a completed backtest is ready for Paper Trading. Do not use to compose or submit a Strategy; route those requests to strategy-building.
---

# Strategy Analysis

Analyze one exact cross-sectional Strategy run as a read-only research workflow. Pair Product
Backend's canonical run snapshot with owner-scoped retained artifacts and bounded six-chart data.
Distinguish observed evidence from inference, alternatives, and proposed experiments.

OAuth and all credentials are handled by the host. The host MCP client handles automatic token refresh. Never inspect,
print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access
tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

## Plugin Version and Connection

Before the first business action, read and follow the shared
[connection and version policy](../../references/connection-and-version.md).
Use it for automatic connection recovery throughout the workflow.

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

- Remain read-only. Do not submit, resume, save, overwrite, archive, or mutate any run.
- Do not automatically create ablations, reruns, or Paper Trading runs.
- Use only authorized evidence returned by Quandora MCP tools: owner-scoped Strategy results
  and the explicit source-free official Factor performance path. Never inspect user-local files as
  proof of a Strategy result.
- Do not require a local ZIP, extraction tool, Python runtime, notebook, or archive-inspection
  script. A host without those facilities must receive the same analysis capability.
- Never execute code, logs, notebooks, scripts, or text artifacts.
- Preserve null and missing values as unavailable, not zero.
- Treat Factor input definitions and D/D+1 alignment as owned by the Factor Plugin Contract. Do
  not use its current task scope to rewrite a frozen Factor or StrategyRun.
- Never fabricate factor correlations, contributions, ablations, or causal claims.
- Treat grade and score as QuantAI-relayed evidence, not as a promotion or research verdict.
- Treat `ALL` as a combined scope that includes IS. Never describe it as pure OOS.

## Workflow

### 1. Establish The Exact Run

Prefer an exact `run_id` supplied by the user or already returned in the conversation. When no
exact run id is supplied:

1. Call `sb_list_runs` once with `{}`. It returns the owner's newest-first page with default
   `limit: 10` and `offset: 0`.
2. Use returned identity, name, timestamps, status, and optional summary only to select a run.
3. If more than one plausible run remains, ask the user to choose. Do not guess.
4. Do not auto-page. Request another page only for an explicit older-run request that the first page
   cannot satisfy.

If an exact run id is supplied, skip discovery.

### 2. Read Canonical Composition And Parameters

Call `sb_get_run` with the exact `run_id`. Treat its canonical `composition` and `parameters` as the
authority for factor ids or weights, ranking, strategy type, window, capital, fees, rebalance bars,
and attribution.

If ranking was omitted at submission, the current Strategy default is neutral Top/Bottom 20%:
`ranking: {mode: "percent", value: 20}` with `strategy_type: "neutral"`. Report the effective
snapshot returned by `sb_get_run`; do not infer parameters from chart labels.

If the run is not terminal, report the current state. Do not call `sb_resume_run` from this
read-only skill and do not substitute local files.

### 3. Read Core Server Artifacts

Use `sb_get_artifact` for the exact run. Start with `summary` and `performance`, then request only
the evidence needed for the question:

- `equity_curve` and `drawdown_curve` for path, concentration, and recovery;
- `turnover_curve` and `exposure_curve` for implementation intensity and neutrality;
- `attribution` and `signal_return_curves` for mechanism claims when available;
- `status`, `result`, `orders`, or `trades` only when a specific claim requires them.

Treat each artifact status independently. Missing, pending, unavailable, or null evidence must stay
explicitly missing. Do not use `logs` or `code` unless the user explicitly asks for inert text
review; never execute either.

### Oversized Trade Files

If `sb_get_artifact` returns `too_large` for `trades`, call `sb_file_ticket` with
that exact `run_id` and `artifact: "trades"`. Present the returned `download_url`
as a clickable download link, with its expiry/single-use limitation. Do not consume
the link to test it before handing it to the user. If it expires or was consumed,
request a fresh ticket when the user needs it. Do not retry the same oversized
inline read or rerun the backtest. Preserve non-ready download statuses honestly.

This delivers the existing file to the user; it does not mean the Agent has read
its contents. Do not claim per-trade, symbol or monthly contribution findings from
a download ticket alone. Do not require local scripts or automatically download
and execute analysis code. This fallback is for the trade file, not six-chart evidence.

### Official Factors In A Strategy

Use returned composition/eligible-factor metadata to identify an official Factor;
do not infer official status from `not_found`. If `fm_official_read` is available,
call it with the exact known `factor_id` for performance. It reuses the authorized
official detail service and never returns plugin source. Preserve snapshot
completeness and the published window labels; do not relabel p1/p2/p3 as IS/OOS.
Compare returned version/backtest identity with the Strategy's recorded lineage.
`evidence_scope: current_official_detail` alone does not prove a historical match.
If identity is missing or different, describe it as current official performance
and keep historical-version evidence explicitly unavailable. Never use source,
ordinary Factor bundles, or guessed job IDs to work around access restrictions.
If the tool is absent during rollout, report that capability gap without repeating
owner-scoped calls. Private and shared Factor access rules are unchanged.

### 4. Read Six-Chart Numerical Evidence

1. Call `sb_analysis_data` with `chart: "overview"`.
2. Confirm the exact `run_id`, server artifact identity, status, integrity digest, availability,
   declared window, parameters, cross-section summary, missing styles, and chart catalog.
3. Request only the chart pages needed for the diagnosis. Follow `next_offset` only for the same run
   and chart until the required evidence is complete.
4. Preserve returned point order, integer values, finite numbers, and nulls exactly.

The six-chart route is the numerical analysis path. Do not request a Result Bundle, PNG, download
ticket, storage URL, or local file to replace it. On `pending`, `not_available`, `too_large`, or
`integrity_failed`, report the exact evidence limitation and continue only with independent server
artifacts that remain trustworthy.

### 5. Diagnose The Result

When interpreting Strategy costs, call `qd_get_guidance` with
`guide_id: "operation.strategy.result.read"` and
`sections: ["funding_net_cash_flow", "strategy_cost_metrics"]`. Read the approved
Guide alongside the exact run's returned summary metrics. If Guidance or result
reads fail, state the limitation; do not guess missing values or bypass MCP.

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

Actual Strategy selection comes only from `sb_get_run.parameters.ranking`. Six-chart diagnostics use
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
