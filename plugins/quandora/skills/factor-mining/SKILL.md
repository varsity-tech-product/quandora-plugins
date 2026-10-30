---
name: factor-mining
description: Creates, validates, backtests, continues, retrieves, or summarizes one Quandora Factor and reads owned Factor families or history. Use when the user asks for Factor Mining authoring or reuse. Do not use for the Strategy eligible-factor pool or deep result diagnosis.
---

# Quandora Factor Mining

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery and the once-per-session release check; preserve existing update authority.
Follow [Research intent and evidence](../../references/research-workflows.md) for backtest/forward
scope, capability-aware conclusions and authorization-preserving handoffs.

This skill owns Factor Mining research creation, caller-owned Factor family/history reads, Factor
backtests, and Factor Result Bundle delivery through the authenticated `quandora`
connection.

Route bare available/eligible/selectable Factor requests to `$strategy-building`; it calls only
`list_eligible_strategy_factors`. Route deep diagnosis, comparison, or optimization of an existing
Factor result to `$factor-analysis`. Do not create or submit a factor merely because analysis found
an improvement.
For named objects, follow [Name discovery](../../references/object-discovery.md) to resolve exact identities.

## Tools

Use only the minimum relevant subset:

- Entry and discovery: `get_factor_mining_status`, `list_factor_mining_tasks`.
- Reusable Factor reads: `list_owned_factor_families`, `get_factor_family_history`.
- Authoring: `get_factor_plugin_contract`, `create_factor_task_session`,
  `create_custom_factor_session`, `validate_factor_plugin`, `get_factor_dedup_context`.
- Run lifecycle: `submit_factor_backtest`, `continue_factor_backtest`.
- Existing reversal relationships (read only): `get_factor_reversal`.
- Result delivery: `download_result_bundle` with `kind: "factor"` and the terminal job ID.
- Approved semantics/diagnostics: `get_quandora_guidance`,
  `check_quandora_plugin_version`.

Tool names in this Skill are canonical actions on the configured `quandora` MCP
dependency. Let the host resolve its required server-qualified form. If an action is absent, do not
invent an alias or use another service path.

Use `check_quandora_plugin_version` only for a requested version diagnostic or a plausible
package/server mismatch; never as a mandatory entry probe.

## Load Supporting Material Selectively

- After routing to new Factor construction, load
  [Factor Plugin Authoring](references/plugin-authoring.md).
- After obtaining the scoped contract for source construction, load
  [86-Field Research Contract Consumption](references/binance-intraday-contract.md). It explains
  how to consume the live per-field semantics and reviewed cross-field guidance without copying
  either registry into the Skill.
- After submission, continuation, or an export request, load
  [Factor Run and Result Delivery](references/run-and-result-delivery.md).

Do not load Result Bundle transport rules for a list/history-only request.

## Route First

- Bare requests for available, eligible, or selectable factors in the Strategy factor pool exit
  to `$strategy-building` without calling a Factor Mining status or inventory action.
- Caller-owned Factor Mining families, branches, versions, history, or prior Factor runs remain
  here.
- New public-task or custom-factor work remains here.

For a normal creation workflow, call `get_factor_mining_status` once after routing. Do not call it
for a completed list/history-only request when the relevant read is already available.

## Reuse and History

Call `list_owned_factor_families` for caller-owned reusable Factor families; it is not the Strategy
eligible pool. Use a supplied name or keyword as `query` and exact public status, availability, or
task identity as `filters`; omit them only for a browse request. Show one bounded page and never
hydrate every row. A failed list is not an empty inventory and does not authorize a history
fallback.

Ask the user to select one exact returned `factor_id`, then call `get_factor_family_history`.
Default to `summary`; request only the needed `branches`, `versions`, or `runs` view. Preserve
opaque IDs and page tokens exactly. Never substitute a job, run, plugin, session, Strategy
admission, or cached identifier. History is read-only and does not authorize source editing or
resubmission. A continuation keeps the same query, filters, archive mode, and page size and copies
the returned opaque page token byte-for-byte.

When controlled history/result semantics are needed, use `get_quandora_guidance` only with the
known guide `operation.factor.history.read` or `operation.result.read` and only supported sections.
Use `metric.backtest.grade` only for its capability semantics. Guidance never creates a tool input
or mutation authority.

## Create and Backtest

For public work, call `list_factor_mining_tasks`, show only exact returned task name and category,
and keep `task_id` internal. Ask the user to select by name or temporary ordinal unless they
explicitly delegated the choice. Internally, treat the selected public Task's returned research
fields as one live research thesis for mechanism, feature, regime, risk, and target-behavior
choices; do not reduce construction to name/category or copy those fields into this Skill. Create
the session with the exact selected task.

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

## Reversal Requests

QuantAI evaluates every Factor in the direction that made money in-sample, so a reversed Factor's
card would match the original apart from the sign of IC, and Strategies use that evaluated direction
automatically; reversal is retired, so never call a reversal command, even one the server still
lists or the user authorizes. Submit a hand-negated plugin only as a genuinely new idea through the
ordinary authoring workflow. `get_factor_reversal` with the immutable Factor ID only reads a
relationship created earlier.

## Continue and Deliver

`continue_factor_backtest` re-drives one exact known non-terminal run; it is not a read-only fetch.
Use the bounded continuation and Result Bundle rules in
[Factor Run and Result Delivery](references/run-and-result-delivery.md).

The canonical completed local output is
`Quandora result/factor/<factor_slug>.zip`. For authored factors, derive the slug from
the exact accepted matching `FACTOR_TYPE` literals. For an existing reversed Factor, use the exact
server-returned Factor type from history; if absent, use the safe returned bundle filename.
When naming the export, never silently fall back to a generic `factor` slug.
Never save the Factor ZIP in a Strategy directory.

## Final Response

State the Factor name, safe run state, safe failure diagnostics if applicable, bundle state, and the
exact verified local ZIP path when saved. For a partial snapshot, state the exact omissions and
their reasons. If the host cannot write, say that no verified ZIP was saved.

Never expose task IDs in public task lists. Include a job/run handle only when it supports the
requested continuation, recovery, export, or handoff. Never include tickets, download URLs,
base64, or full plugin source in a general summary.

Use the user's language for the answer while preserving tool names, schema fields, and returned
identifiers exactly.

## Library Favorites

For Factor/Strategy stars and folder-independent metadata, follow
[Library Favorites](../../references/library-favorites.md).
