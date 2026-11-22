# Factor Run and Result Delivery

Load this reference after a Factor backtest is submitted, when an existing non-terminal run must be
continued, or when the user requests the Result Bundle.

## Mutation Recovery

`retryable` describes availability; `recovery_action` controls mutation behavior:

- `repair_and_revalidate`: repair allowlisted diagnostics and validate the complete source again.
- `create_same_kind_session_after_input_change`: create a new public/custom session of the same
  kind with a new invocation identity.
- `retry_same_pending_request`: replay at most once with the exact pending handle, bound request,
  persisted idempotency identity, and unchanged validated source.
- `resume_known_run`: use only `continue_factor_backtest` on the exact returned run.
- `stop_and_report_trace`: stop and report only the safe trace.
- `repair_then_create_same_kind_session`: repair, revalidate, then create the same kind of session
  before one ordinary upload.

Never infer mutation authority from a generic retry flag. Never upload again when a known run says
resume.

## Bounded Observation

Use `continue_factor_backtest` only for an exact known non-terminal run and at most four times in one
request. It re-drives backend work; it is not a status read. If still running, stop, report that the
run can be continued later, and do not request Result Bundle metadata.

## Result Bundle

Only a terminal run may enter delivery. Call `create_factor_result_bundle_download` with the exact
terminal `job_id`. Treat the returned immutable metadata and manifest as authoritative; readable
`available` and persisted readable `partial` snapshots can be downloaded.

If the first response is `pending` with `bundle_materializing`, wait at most ten seconds and make
one fresh metadata call without a snapshot revision. If a readable partial reports pending items,
one separate ten-second freshness refresh is allowed. Neither bound is a polling loop, and neither
resubmits or continues the completed run.

Prefer the returned short-lived URL: consume it immediately and unchanged into a task-created
`.partial`, checking byte count and SHA-256 while streaming. One fresh-ticket retry is allowed only
after an actual transient HTTP failure. If URL transfer remains unavailable, call
`read_factor_result_bundle_chunk` with the same job and revision:

- start at offset 0 and request at most 262144 raw bytes;
- append decoded bytes before interpreting `terminal`;
- require exact offset progression and at most `ceil(size_bytes / 262144)` calls;
- bind every response to the same selector, revision, filename, content type, size, and hash;
- a terminal response may contain the final non-empty bytes and must have `next_offset: null`.

Verify exact size/hash, ZIP magic/openability, and safe relative entries before atomic rename. On
failure, discard only the task-created unverified partial.

The canonical local destination is
`Quandora result/factor/<factor_slug>.zip`. Derive the slug only from the exact accepted
matching `FACTOR_TYPE` literals; never silently fall back to a generic `factor` slug. Use a
user-requested safe destination when supplied. Never overwrite unrelated bytes, extract/rebuild the
archive, synthesize entries, or create a second completed `run_summary.json`.

If the selected snapshot is partial, report its exact omissions and pending reasons. Never expose
job IDs, revisions, tickets, URLs, credentials, base64, or internal storage metadata in the final
summary.
