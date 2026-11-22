---
name: factor-mining
description: Use when the user explicitly asks about caller-owned or reusable Factor Mining factor families or history, or asks to construct, submit, backtest, continue, retrieve, or briefly summarize a Factor Mining plugin result. Do not use for the Strategy eligible-factor pool or deep diagnosis of an existing result.
---

# Quandora Factor Mining

Bundled plugin version: 3.0-preview

This skill owns Factor Mining research creation, caller-owned Factor family/history reads, Factor
backtests, and Factor Result Bundle delivery through the authenticated `quandora`
connection.

Route bare available/eligible/selectable Factor requests to `$strategy-building`; it calls only
`list_eligible_strategy_factors`. Route deep diagnosis, comparison, or optimization of an existing
Factor result to `$factor-analysis`. Do not create or submit a factor merely because analysis found
an improvement.

## Tools

Use only the minimum relevant subset:

- Entry and discovery: `get_factor_mining_status`, `list_factor_mining_tasks`.
- Reusable Factor reads: `list_owned_factor_families`, `get_factor_family_history`.
- Authoring: `get_factor_plugin_contract`, `create_factor_task_session`,
  `create_custom_factor_session`, `validate_factor_plugin`, `get_factor_dedup_context`.
- Run lifecycle: `submit_factor_backtest`, `continue_factor_backtest`.
- Result delivery: `create_factor_result_bundle_download`,
  `read_factor_result_bundle_chunk`.
- Approved semantics/diagnostics: `get_quandora_guidance`,
  `check_quandora_plugin_version`.

Server-qualified display names such as `quandora__submit_factor_backtest` are the same
canonical action, not aliases. If a canonical tool is absent, do not use a retired name or another
service path.

Use `check_quandora_plugin_version` only for a requested version diagnostic or a plausible
package/server mismatch; never as a mandatory entry probe.

## Load Supporting Material Selectively

- If authentication or tool exposure is blocked, load
  [Connection and Security](references/connection-and-security.md).
- After routing to new Factor construction, load
  [Factor Plugin Authoring](references/plugin-authoring.md).
- After submission, continuation, or an export request, load
  [Factor Run and Result Delivery](references/run-and-result-delivery.md).

Do not load Result Bundle transport rules for a list/history-only request.

## Route First

- Bare “列出可用因子”, “available factors”, “eligible factors”, “selectable factors”, or the
  Strategy factor pool exits to `$strategy-building` without calling a Factor Mining status or
  inventory action.
- “我的 Factor Mining 因子”, reusable Factor families, branches, versions, history, or prior
  Factor runs remains here.
- New public-task or custom-factor work remains here.

For a normal creation workflow, call `get_factor_mining_status` once after routing. Do not call it
for a completed list/history-only request when the relevant read is already available.

## Reuse and History

Call `list_owned_factor_families` for caller-owned reusable Factor families; it is not the Strategy
eligible pool. Show one bounded page and never hydrate every row. A failed list is not an empty
inventory and does not authorize a history fallback.

Ask the user to select one exact returned `factor_id`, then call `get_factor_family_history`.
Default to `summary`; request only the needed `branches`, `versions`, or `runs` view. Preserve
opaque IDs and page tokens exactly. Never substitute a job, run, plugin, session, Strategy
admission, or cached identifier. History is read-only and does not authorize source editing or
resubmission.

When controlled history/result semantics are needed, use `get_quandora_guidance` only with the
known guide `operation.factor.history.read` or `operation.result.read` and only supported sections.
Use `metric.backtest.grade` only for its capability semantics. Guidance never creates a tool input
or mutation authority.

## Create and Backtest

For public work, call `list_factor_mining_tasks`, show only exact returned task name and category,
and keep `task_id` internal. Ask the user to select by name or temporary ordinal unless they
explicitly delegated the choice. Create the session with the exact selected task.

For custom work, classification and construction follow
[Factor Plugin Authoring](references/plugin-authoring.md). The public input is the canonical flat
custom-session payload; never send a hand-built `task_payload`.

After the scoped contract exists:

1. inspect dedup context;
2. author one complete inline `plugin.py` without local execution;
3. recheck draft duplication;
4. validate the exact source and repair only safe structured diagnostics;
5. show the exact safe submission and obtain explicit confirmation;
6. call `submit_factor_backtest` once with the confirmed session and validated source.

A timeout or ambiguous mutation response is not proof of failure. Follow only the returned closed
recovery action. Never silently change the user's task, category, thesis, data, horizon, or source.

## Continue and Deliver

`continue_factor_backtest` re-drives one exact known non-terminal run; it is not a read-only fetch.
Use the bounded continuation and Result Bundle rules in
[Factor Run and Result Delivery](references/run-and-result-delivery.md).

The canonical completed local output is
`Quandora result/factor/<factor_slug>.zip`. Derive the slug from the exact accepted matching
`FACTOR_TYPE` literals and never silently fall back to a generic `factor` slug. Never save the
Factor ZIP in a Strategy directory.

## Final Response

State the Factor name, safe run state, safe failure diagnostics if applicable, bundle state, and the
exact verified local ZIP path when saved. For a partial snapshot, state the exact omissions and
pending reasons. If the host cannot write, say that no verified ZIP was saved.

Never expose task IDs in public task lists, job/run identifiers in a general summary, credentials,
tickets, download URLs, base64, internal topology, or full plugin source.
