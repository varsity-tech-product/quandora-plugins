---
name: strategy-building
description: Use when the user asks to list available or eligible Strategy factors, including “列出可用因子”, or create, revise, backtest, continue, rerun, retrieve, or export one cross-sectional Quandora Strategy using Official, Mine, or Shared factors, including an explicit base/pro optimizer StrategyVersion. Do not use for multi-Strategy Portfolio composition, Paper execution, or deep result diagnosis.
---

# Quandora Strategy Building

Bundled plugin version: 3.0-preview

This skill owns one Strategy: eligible-factor selection, ordinary Strategy submission, explicit
versioned/optimizer Strategy definitions, single-Strategy backtests, reruns, and ordinary Strategy
Result Bundle delivery through `quandora`.

An optimizer policy remains part of one StrategyVersion; it is not a multi-Strategy Portfolio.
Route two-or-more StrategyVersion composition and aggregate research to `$strategy-portfolio`,
simulated execution to `$paper-trading`, and deep diagnosis of completed evidence to
`$strategy-analysis`.

## Tools

Use only the minimum relevant subset:

- Capability and eligible factors: `get_strategy_capabilities`,
  `list_eligible_strategy_factors`, `get_eligible_strategy_factor`.
- Shared/external admission: `list_shared_strategy_factor_candidates`,
  `admit_shared_strategy_factor`, `import_strategy_factor`.
- Ordinary run lifecycle: `submit_adhoc_strategy_backtest`, `list_strategy_backtests`,
  `get_strategy_backtest`, `continue_strategy_backtest`, `rerun_strategy_backtest`.
- Ordinary Result Bundle: `create_strategy_result_bundle_download`,
  `read_strategy_result_bundle_chunk`.
- Versioned/optimizer definition: `create_strategy`, `revise_strategy`, `get_strategy`,
  `get_strategy_version`, `submit_strategy_backtest`.

Use `get_quandora_guidance` only for the exact approved workflow described in supporting material.
`get_paper_trade_source` is a read-only handoff used only to observe an explicit versioned source;
its primary workflow owner remains `$paper-trading`.

Server-qualified names such as `quandora__submit_adhoc_strategy_backtest` are canonical
display forms, not aliases. If a canonical action is unavailable, do not use a retired name or
alternate service.

## Load Supporting Material Selectively

- If authentication or tool exposure is blocked, load
  [Connection and Security](references/connection-and-security.md).
- For ordinary factor selection, submission, observation, or rerun, load
  [Ordinary Strategy Workflow](references/ordinary-strategy-workflow.md).
- Only for an explicit base/pro or versioned source, load
  [Versioned Optimizer Source](references/versioned-optimizer-source.md).
- Only after an ordinary terminal run/archive or an export request, load
  [Strategy Result Bundle Delivery](references/result-bundle-delivery.md).

Do not load optimizer/YAML or Result Bundle transport instructions for a bare factor-list request.

## Route First

- Bare “列出可用因子”, “available factors”, “eligible factors”, or “selectable factors” calls
  only `list_eligible_strategy_factors`, one bounded page, then stops.
- Requests for caller-owned Factor Mining families/history route to `$factor-mining`.
- One ordinary Strategy uses the ordinary workflow.
- An explicitly requested base/pro optimizer or immutable versioned source uses the versioned
  workflow.
- Two or more exact StrategyVersions with target weights route to `$strategy-portfolio`.
- “Optimize this result” as analysis routes to `$strategy-analysis`, not optimizer-source creation.

## Ordinary Strategy

Follow [Ordinary Strategy Workflow](references/ordinary-strategy-workflow.md):

1. read the current capability contract once;
2. verify exact selected Factors in the eligible inventory;
3. validate one canonical equal- or custom-weight payload;
4. show all effective choices and obtain explicit confirmation;
5. submit once and observe only the returned run;
6. treat terminal rerun as a separate explicitly confirmed mutation.

Do not create a Strategy Portfolio for a single Strategy. Do not call Paper start tools here.

## Versioned Optimizer Source

Follow [Versioned Optimizer Source](references/versioned-optimizer-source.md). Definition/revision
and backtest are separate mutations requiring separate confirmations. Optimizer policy is
capital-independent; run capital belongs to `submit_strategy_backtest`.

This path ends with bounded source lifecycle/eligibility evidence. A later Paper request hands the
exact eligible completed source to `$paper-trading`; no Paper mutation occurs here.

## Result Delivery

The ordinary Strategy main run must be terminal and archive state completed or partial before
bundle delivery. Follow
[Strategy Result Bundle Delivery](references/result-bundle-delivery.md).

The default completed local path is
`Quandora result/strategy/<strategy_slug>.zip`. Never save a Strategy ZIP in the Factor
directory or treat the exported ZIP as server-side analysis evidence.

## Safety

- Treat Strategy, StrategyVersion, StrategyRun, FM lineage, Paper source, and Portfolio handles as
  distinct opaque owner-scoped identifiers.
- An ambiguous mutation response is not permission to resubmit, revise, rerun, or switch payloads.
- `continue_strategy_backtest` re-drives only a known non-terminal run.
- `fmRetryable` is advisory. A failed immutable run may be rerun only after exact lineage checks,
  repetition-risk disclosure, and explicit confirmation.
- Never infer Paper authority from completed research or start Paper from this skill.
- Never expose credentials, policy secrets, provider identities, internal URLs, or raw downstream
  payloads.

## Final Response

State the submitted Strategy name, workflow type, main-run/archive state, safe diagnostics, and the
verified Result Bundle path when saved. If a run remains in progress, state that bundle delivery
was not started. If handing off, state clearly that no Portfolio or Paper mutation was performed.

Never expose run handles in a general summary, tickets, download URLs, credentials, base64, or
internal service metadata.
