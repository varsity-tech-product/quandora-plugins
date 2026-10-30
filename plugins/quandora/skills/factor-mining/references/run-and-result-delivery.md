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

## Provider Acceptance Is A Separate Axis

FM durable acceptance is not proof that the provider accepted or executed the backtest.
When present, preserve `run.provider_submit_state` separately from backtest lifecycle status.
`reserved`/`submitting` are pre-acceptance states; `accepted` does not mean completed.
`outcome_unknown` with `next_action: reconciliation_required` means stop and retain the exact
run/trace for coordination. Do not call continue, upload again, infer failure, claim performance,
or download artifacts for that uncertain receipt. A generic retryable flag cannot override this.
Absent provider state is unavailable evidence, not inferred acceptance.

## Bounded Observation

Use `continue_factor_backtest` only for an exact known non-terminal run and at most four times in one
request. It re-drives backend work; it is not a status read. If still running, stop, report that the
run can be continued later, and do not request Result Bundle metadata.

## Result Bundle

An existing reversed Factor's run follows this same delivery workflow.
Only a terminal run may enter delivery. Call `download_result_bundle` with `kind: "factor"` and `id` set to the exact
terminal `job_id`. Treat the returned immutable metadata and manifest as authoritative; readable
`available` and persisted readable `partial` snapshots can be downloaded.

FM schedules the first ZIP after a new terminal run reaches finalized artifact readiness;
completion and ZIP publication can be observed at different times. Historical runs may still
have no retained ZIP. `not_available` means no verified ZIP is currently deliverable through
this request. A partial snapshot without a verified download descriptor is not downloadable. Do not relabel missing bytes as pending or re-run the backtest to create them.

If the first response is `pending` with `bundle_materializing`, wait at most ten seconds and make
one fresh metadata call without a snapshot revision. This is a bounded read, not a polling loop,
and never resubmits or continues the completed run. A current Factor `partial` snapshot has
terminal omissions (`unavailable` or `failed`) with reasons; it is not a pending build. Do not
refresh it just because it is partial. Projection recovery belongs to FM and reuses the persisted
ZIP for that exact Run and snapshot; a consumer metadata read does not rebuild it.

Download and verify through [Unified Result Bundle Download](../../../references/result-bundle-download.md).

The canonical local destination is
`Quandora result/factor/<factor_slug>.zip`. Derive the slug only from the exact accepted
matching `FACTOR_TYPE` literals for authored factors. For a reversed factor, use its server-returned
Factor type or the safe returned bundle filename when no type is exposed; do not request source
just to name an export. Never silently fall back to a generic `factor` slug. Use a
user-requested safe destination when supplied. Never overwrite unrelated bytes, extract/rebuild the
archive, synthesize entries, or create a second completed `run_summary.json`.

If the selected snapshot is partial, use the returned metadata `items` to explain the exact
omissions and reasons before download, then verify them against the manifest inside the verified
ZIP. During a rolling deployment, an empty metadata `items` array is not evidence of completeness;
use the verified ZIP manifest for that older response.
Do not infer that a partial snapshot is still being generated. Include the
public job handle only when needed for continuation, recovery, export, or handoff. Never include
revisions, tickets, URLs, or base64 in the final summary.
