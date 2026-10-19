# Factor Plugin Authoring

Load this reference after the request has been routed to creation and the appropriate session or
task selector exists.

## Construction Contract

Call `get_factor_plugin_contract` before writing source. For custom work, call it once with `{}` to
obtain the global data-column contract, create the custom session, then call it with only that
session's exact `session_id`. Public tasks may use one exact returned `task_id` or the created
session. Never use a hand-built task payload.

The returned scoped contract is authoritative:

- use only `plugin_contract.allowed_data`;
- for public work, consume `plugin_contract.task_payload` as the final selected Task definition,
  including its description, hints, alpha source, research directions, feature hints, regimes,
  risks, and target behavior; if it materially differs from the Task the user selected, stop and
  present the changed semantics instead of silently authoring a different thesis;
- use each `data_columns[].python_kwarg` for `build_signal`;
- use each returned C# expression only where `bar` is visible;
- consume returned source, meaning, unit, comparability, normalization, missing-value, caution,
  and upstream-version metadata instead of maintaining a local field dictionary;
- consume `runtime_rules.research_guidance` for cross-field normalization, missing-data rolling,
  smoothing, redundancy, Task relevance, and default Paper-ready constraints;
- copy extra-buffer field/enqueue/dequeue/to-array snippets byte-for-byte;
- obey runtime globals, reserved identifiers, leak rules, and required `FACTOR_SECTIONS`;
- when section values must be literals, keep the top-level `FACTOR_TYPE` and
  `FACTOR_SECTIONS["__FACTOR_TYPE__"]` as identical lowercase snake_case string literals.

Contract-generated identifiers have precedence over general naming. Factor-owned fields use the
returned prefix/style; new compute locals use descriptive `factor...` names. Never infer bar
fields, casts, runtime expressions, supported columns, or Task research text from memory. Do not
cache or duplicate the nine public Task definitions in this reference.

Read [86-Field Research Contract Consumption](binance-intraday-contract.md) for the selected
fields and research policy. If any selected column reports `data_source: "binance_intraday"`,
also consume `runtime_rules.data_availability.binance_intraday` directly; do not recreate its
temporal rules, shift a correctly aligned row again, or expose the provider's internal
data-directory selector.

## Custom Classification

Before `create_custom_factor_session`, obtain one complete successful
`list_factor_mining_tasks` response. Every row must be open, uniquely identified, bounded, and
contain the required category, allowed-data, and research-semantics fields. A malformed or empty
response is a contract mismatch.

Compare the thesis with all returned research semantics. Choose the exact category of the best
honest match, or the explicit `Other` fallback when no row fits. Never classify from task ID/title,
invent a category vocabulary, fabricate an `Other` row, or copy a public task ID into the custom
session. Create the session with exactly `title`, `description`, `category`, `allowed_data`, and
the supported `fwd_period` selected by the user or returned workflow contract; do not insert a
remembered default.

Keep Task category and `FACTOR_TYPE` distinct but aligned: category is the product label;
`FACTOR_TYPE` is a unique mechanism-specific identifier, never a bare category. If the mechanism
changes category, create a new correctly classified custom session and repeat the contract and
validation flow.

## Deduplication and Validation

After session creation call `get_factor_dedup_context` once for task memory. After a concrete draft,
call it again with the same session, full source, concise description/formula, and a bounded limit.
Use `draft_duplicate_risk` as the verdict and `similar_factors` as evidence. Revise concrete
mechanism overlap; memory pressure alone is not a rejection gate.

Submit the exact complete inline `plugin_source`; never send a path. Do not import, execute, eval,
or shell-run generated factor code locally. `build_signal` must accept numeric/object-dtype inputs,
return an aligned float DataFrame, use no future data, and replace infinities.

Validate after every source change. Repair only from safe structured diagnostics:
`schema_version`, `error_code`, `operation`, `dtype`, `expected`, `actual`, `field`,
`contract_key_path`, and `repair_hint`. A retryable read/validation transport failure permits at
most one identical bounded retry; never retry an unchanged rejected source.

Before `submit_factor_backtest`, show the thesis, exact source/session context, horizon, and safe
submission summary, then obtain explicit confirmation. Submit only `session_id` and the exact
source that passed validation; the session already binds the horizon.
