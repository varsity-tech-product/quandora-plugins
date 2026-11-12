---
name: portfolio-analysis
description: Analyzes an existing Quandora Portfolio backtest against its actual Strategy members and declared baselines. Use when the user asks about diversification, neutrality, risk contributions, drawdown, member value or historical portfolio improvement. Do not use to select and create a new Portfolio, share it, submit experiments or manage forward trading.
---

# Portfolio Analysis

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery and the once-per-session release check; preserve existing update authority. After a
failed mutating call, follow [Failed mutations](../../references/failed-mutations.md).
Use [Research intent and evidence](../../references/research-workflows.md) for scope, evidence
availability and handoffs, and [Name discovery](../../references/object-discovery.md) for names.
Follow [Research notebook](../../references/research-notebook.md) to read the hypothesis being
tested before diagnosing and to record the conclusion after an owned analysis.

This is read-only backtest diagnosis through the authenticated `quandora` MCP connection.
Route selection, creation, changed capital weights and sharing to `$portfolio-building`, exact
member diagnosis to `$strategy-analysis`, and forward evidence or account management to
`$portfolio-trading-analysis`. Carry the task's existing authorization to those owners without
adding confirmation at every handoff.

## Evidence tools

- `get_portfolio_backtest_result`: canonical aggregate result and safe failure.
- `get_portfolio_backtest`, `get_portfolio`: exact run, actual source lineage and immutable definition.
- `list_portfolio_families`, `get_portfolio_family`, `list_portfolios`, `list_portfolio_backtests`:
  bounded discovery only when the exact target is unknown.
- `get_strategy`, `get_strategy_backtest`, `get_strategy_backtest_artifact`,
  `get_strategy_backtest_analysis_data`: authorized owner member evidence through Strategy Analysis.
- `list_community_portfolio_runs`, `get_community_portfolio_research`, `get_community_strategy_research`,
  `get_community_factor_research`, `read_community_research_artifact`: Publication-context evidence.
- `get_portfolio_share`, `list_portfolio_share_runs`, `get_portfolio_share_research`,
  `get_portfolio_share_strategy_research`, `get_portfolio_share_factor_research`,
  `read_portfolio_share_research_artifact`: currently authorized Share evidence.
- `list_research_notes` with the analyzed Run's `portfolio_version` as `subject`: the tested
  hypothesis and targets, from the version-level notes and those whose `run_id` is that Run;
  `record_research_conclusion` on an owned `portfolio_run`, which the server files under its
  version with `run_id`: the only write, recording the verdict.
- `download_result_bundle` with `kind: "portfolio"` and the canonical PortfolioRun ID: optional explicit
  owner export only, never an analysis prerequisite. Shared and Community Portfolios have no
  Result Bundle export; analyze them through their contextual reads.

No submit, create-definition, share, start, stop or account-management operation belongs to this
analysis; recording its conclusion is not one. A download ticket for an explicit export is transport
permission only. Do not execute artifact code or require local files, archive extraction or a Python
runtime to answer.

## Establish the exact research snapshot

Use the supplied `portfolio_run_id`, or resolve the intended immutable `portfolio_id` and its
persisted history. PortfolioFamily/Run lists do not accept `query` or `filters`; do not invent
them. Preserve parent selectors, page size and continuation tokens byte-for-byte. Ambiguous
names or multiple plausible immutable versions require disambiguation, not a guess at latest.

Read the exact PortfolioRun and definition. Preserve actual `components[].strategy_run_id` values,
weights, resolved interval and result status. Do not substitute a better or newer member run.
For `preparing_sources` or `running`, report readiness without resubmitting. A terminal failure
is evidence: read the retained result/failure and do not silently repair or replace members.

For Publication/Share targets use the authorized contextual root and lineage. Owner reads do not
become valid merely because a third-party child ID is visible. If the projection lacks required
member evidence, narrow the conclusion instead of using an owner-tool or export workaround.

Read [Portfolio evidence](references/evidence-contract.md) for status, units and comparable reads.

## Evaluate the Portfolio

Use [Incremental value](references/incremental-value.md) for the actual result and
[Neutrality and complementarity](../../references/portfolio-neutrality.md) for cross-sectional
interpretation. Establish the user's objective and any predeclared baseline before interpreting
the outcome. If none was declared, label the comparison exploratory instead of implying it was
chosen in advance.

1. Check exact membership, exchange, window, frequency, costs, valuation and evidence coverage.
   Rank two Portfolio versions only on Runs with the same exchange and window; otherwise state the
   difference instead of ranking them.
2. Reuse actual source Strategy Cards through `$strategy-analysis`; avoid duplicate diagnosis.
3. Compare with the core Strategy, each actual member and an available same-member equal-capital
   baseline. A retrospective best member is additional context with its criterion stated.
4. Evaluate canonical return/risk, drawdown/recovery, concentration, supported complementary
   evidence and available costs. Neutrality and residual claims require their own evidence.
5. Explain unsupported cross-member prediction correlation, historical overlap, covariance or
   risk contribution as unavailable. Individual six-chart projections do not supply a joint matrix.
6. Give the strongest supported historical verdict and a bounded next experiment if useful.

Do not recompute authoritative metrics locally, fill missing series, average member risk or
invent benchmark prices. Simple deltas require comparable returned values and a labeled derived
comparison. A missing advanced metric does not invalidate independent ready evidence, but can
prevent a claim of independent Alpha or confirmed diversification.

An equal-weight control or leave-one-out experiment requires an existing result or authorized
execution by `$portfolio-building`. Specify the removed member, remaining weight/capital rule,
window and comparison metric. Historical attribution alone is not causal marginal value.

## Output

Never create, start, pause, resume or stop a Simulation account or run unless the user asked for
that exact operation. When research suggests one, list the exact Portfolio or run, proposed
operation and reason in the final report for a person to decide.

Use the user's language. Scale the response to the question and include:

- exact Portfolio/Run, source members, interval and evidence readiness;
- objective, baselines and comparable headline results;
- observed complementary behavior, concentration, neutrality and cost tradeoffs;
- one main verdict: **Historical evidence supports improvement**, **Risk/return tradeoff**,
  **No demonstrated improvement**, or **Insufficient evidence**;
- key supporting observations, limitations, failure conditions and a proposed next experiment.

For an owned Run, record the verdict and its main reason as the conclusion and the proposed
experiment as `next_steps`, in the user's language, also for analysis-only requests. Shared and
Publication evidence has no notebook entry.

Keep historical findings separate from forward-test readiness and observed Trading performance.
Do not claim global optimality, out-of-sample validation or a durable future advantage from a
selection/evaluation sample reused for optimization.
