# Strategy Result Bundle Delivery

Load this reference only after an ordinary Strategy main run is terminal and archive state permits
bundle metadata, or when the user explicitly requests that Result Bundle.

Call `create_strategy_result_bundle_download` with the exact public PB Strategy run handle. Never
substitute an FM run/version identifier. Treat the immutable metadata and manifest as authoritative;
readable `available` and persisted readable `partial` snapshots may be delivered.

If the initial response is `pending` with `bundle_materializing`, wait at most ten seconds and make
one fresh metadata call without a revision. If a readable partial reports pending items, one
separate ten-second freshness refresh is allowed. These are not loops and never resubmit or
continue a terminal run.

Prefer the short-lived URL: consume it immediately and unchanged into a task-created `.partial`,
maintaining exact byte count and SHA-256. Only an actual transient HTTP failure permits one fresh
ticket and one URL retry. If transfer remains unavailable, use
`read_strategy_result_bundle_chunk` with the same public run and revision:

- start at offset 0 and request at most 262144 raw bytes;
- append decoded content before interpreting `terminal`;
- require exact offset progression and no more than `ceil(size_bytes / 262144)` calls;
- bind all responses to the same run, revision, filename, content type, size, and hash;
- a terminal response may carry final bytes and must have `next_offset: null`.

Verify exact size/hash, ZIP magic/openability, and safe relative entries before atomic rename.
Discard only the task-created unverified partial on failure.

Build `<strategy_slug>` from the submitted user-facing Strategy name: lowercase, collapse
non-alphanumeric runs to `_`, trim, and truncate to 48 characters; use `strategy` only when empty.
Never include backend identifiers or path separators. The default destination is
`Quandora result/strategy/<strategy_slug>.zip`.

Use a safe user-requested destination when supplied. Never overwrite unrelated bytes,
extract/rebuild/re-ZIP the archive, synthesize missing items, or create a second completed
`run_summary.json`. A pending run may have one redacted pending summary in the authoring workspace.

For partial delivery, state exact omissions and reasons. Never expose run IDs in a general summary,
revisions, tickets, URLs, credentials, base64, or internal storage metadata.
