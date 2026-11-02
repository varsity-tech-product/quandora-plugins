# Factor Plugin Authoring

Load this reference after the request has been routed to creation and the public task or custom
classification is known.

## Construction Contract

Call `get_factor_plugin_contract` before writing source: with the exact returned `task_id` for public
work, or with no selector for the global data-column contract for custom work. An existing step
session may use its exact `session_id`. Read it in two steps instead of whole (the full contract
is about 150,000 characters): first with `contract_view: "index"` to read the task, every field's
group, unit and description, and all runtime rules; then with `contract_view: "columns"` and
`columns` set to the exact chosen `data_column` names for their full entries and C# buffer
snippets. Treat those two responses together as the contract. Pass the returned `schema_version`
to `submit_factor_research` as `contract_version`. Never use a hand-built task payload.

The returned scoped contract is authoritative:

- use only `plugin_contract.allowed_data`;
- for public work, consume `plugin_contract.task_payload` as the final selected Task definition,
  including its description, hints, alpha source, research directions, feature hints, regimes,
  risks, and target behavior; if it materially differs from the selected Task, author for these
  returned semantics or select another Task from the research context and candidates. Record the
  choice and reason in `research_note.hypothesis` for a new direction or `change_summary` otherwise;
  never silently author a different thesis;
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

Before submitting custom research, obtain one complete successful `list_factor_mining_tasks`
response. Every row must be open, uniquely identified, bounded, and
contain the required category, allowed-data, and research-semantics fields. A malformed or empty
response is a contract mismatch.

Compare the thesis with all returned research semantics. Choose the exact category of the best
honest match, or the explicit `Other` fallback when no row fits. Never classify from task ID/title,
invent a category vocabulary, fabricate an `Other` row, or copy a public task ID into the custom
submission. Submit custom research with exactly `title`, `description`, `category`, `allowed_data`,
and the supported `fwd_period` selected by the user or returned workflow contract; do not insert a
remembered default. That `fwd_period` becomes the new version's default horizon; the horizon is a
run condition, not part of the version. To test an existing version at another horizon, use
`run_factor_version` as the primary Skill describes; never submit the same source as an
`improvement` to change only `fwd_period`.

Keep Task category and `FACTOR_TYPE` distinct but aligned: category is the product label;
`FACTOR_TYPE` is a unique mechanism-specific identifier, never a bare category. If the mechanism
changes category, submit it as new correctly classified custom research.

## Deduplication and Validation

`submit_factor_research` reads duplicate context and validates before uploading. Use the returned
duplicate risk as the verdict and similar factors as evidence. Report concrete mechanism overlap
and address it in the next decision; memory pressure alone is not a rejection gate.

Submit the exact complete inline `plugin_source`; never send a path. Do not import, execute, eval,
or shell-run generated factor code locally. `build_signal` must accept numeric/object-dtype inputs,
return an aligned float DataFrame, use no future data, and replace infinities.

A `failed_step` of `validate_plugin_source` means the source did not pass validation. Repair only
from safe structured diagnostics:
`schema_version`, `error_code`, `operation`, `dtype`, `expected`, `actual`, `field`,
`contract_key_path`, and `repair_hint`, then submit the complete corrected source again. A
`failed_step` of `get_plugin_contract` means the contract changed: read it again and re-author
against it. A retryable transport failure permits at most one identical bounded retry; never retry
an unchanged rejected source.
