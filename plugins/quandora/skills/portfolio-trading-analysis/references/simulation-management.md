# Simulation account and run management

Load only for an explicitly requested account or run operation. An analysis-only request is
read-only and does not authorize creating, pausing, stopping or retuning a run.

## Create, Start and Manage Simulation

For an explicit Simulation request, resolve exactly one owned immutable `portfolio_id`, currently
visible Community `publication_id`, or authorized `share_id`. Owned definitions return
`portfolio.portfolio_id`. Internal command IDs are not public selectors. Publication discovery belongs to
`$portfolio-building`. Supply account `name` and requested starting `leverage`; virtual capital,
quota, visibility, active-run and settlement rules remain PB-owned. Never copy a shared Portfolio
into Mine or use its owner ID to bypass the recipient grant.

Choose and retain a UUID `client_request_id` before the first
`create_and_start_simulation_account` call. Reuse it with identical inputs for the same intent.
If the response is lost, call `get_simulation_account_operation(client_request_id=...)`; this
works before an account or Run ID is known. Once known, use `operation_id` for subsequent reads
and `continue_simulation_account_operation` to resume the same operation when recovery is offered.
Do not create a fresh request ID, account or Run to recover a timeout or ambiguous response.

`preparing` and `outcome_unknown` remain unresolved. `accepted` means a Run was attached, not
that it is running. Read the exact returned `run_id` with `get_portfolio_trading_run` before
reporting execution state. Preserve nullable account/Run IDs, safe errors and timestamps.
A failed operation may retain a created account; expose its identity for management instead
of hiding it or creating a replacement automatically.

Use `rename_simulation_account`, `archive_simulation_account`, and
`restore_simulation_account` on exact visible account IDs. PB enforces archive eligibility and
restore quota. Archive does not stop, delete, reset or rewrite account history. Pause and resume
are available through the simulated run tools; resume rechecks plan and sharing eligibility.
Account reset, history deletion and active capital edits are not exposed.

For existing accounts, `start_simulation_account_run` accepts `account_id`, exactly one of the
three source selectors and leverage. Legacy start inputs do not authorize real Live execution.
Report PB-returned permission, quota, expiry or unsupported-state errors without bypassing them.
