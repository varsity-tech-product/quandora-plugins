# Strategy Result Bundle Delivery

Load this reference only after a canonical StrategyRun is terminal and archive state permits
bundle metadata, or when the user explicitly requests that Result Bundle.

Call `download_result_bundle` with `kind: "strategy"` and `id` set to the exact `strategy_run_id`. Never
substitute a Folder, definition, or internal command identifier. Treat the immutable metadata and manifest as
authoritative; readable `available` and persisted readable `partial` snapshots may be delivered.

If the initial response is `pending` with `bundle_materializing`, wait at most ten seconds and make
one fresh metadata call without a revision. If a readable partial reports pending items, one
separate ten-second freshness refresh is allowed. These are not loops and never resubmit or
mutate a terminal Run.

Download and verify through [Unified Result Bundle Download](../../../references/result-bundle-download.md).

Build `<strategy_slug>` from the submitted user-facing Strategy name: lowercase, collapse
non-alphanumeric runs to `_`, trim, and truncate to 48 characters; use `strategy` only when empty.
Never include backend identifiers or path separators. The default destination is
`Quandora result/strategy/<strategy_slug>.zip`.

Use a safe user-requested destination when supplied. Never overwrite unrelated bytes,
extract/rebuild/re-ZIP the archive, synthesize missing items, or create a second completed
`run_summary.json`. A pending run may have one redacted pending summary in the authoring workspace.

For partial delivery, state exact omissions and reasons. Include the public run handle only when
needed for recovery, export, or handoff. Never include revisions, tickets, URLs, or base64 in the
final summary.
