# Factor Server Evidence Contract

Factor Analysis uses owner-scoped or active-official evidence returned directly by Quandora MCP
tools. It does not depend on a user-local archive or runtime.

## Identity And Ownership

- Resolve one exact selector before analysis: terminal `job_id` for caller-owned evidence, or the
  top-level active-official `factor_id` from `list_eligible_strategy_factors`.
- `list_owned_factor_families` and `get_factor_family_history` may be used for bounded owner-scoped discovery.
- `get_factor_backtest_window_cards`, `get_factor_backtest_chart_data`, and `get_factor_backtest_source` must all remain correlated to the selected
  `job_id`.
- Never substitute a factor id, factor version id, session id, display name, or local filename for
  the job id.
- Keep `get_official_factor_window_cards`, `get_official_factor_chart_data`, and
  `get_official_factor_source` correlated to the selected official `factor_id`. Never expose or pass
  its hidden evidence job through an owner-scoped action.

## Factor Card

`get_factor_backtest_window_cards` returns the product-safe IS Factor Card. Its embedded Health and rating fields are
authoritative relayed evidence. Preserve nullable values and recorded thresholds exactly.

`get_official_factor_window_cards` provides the corresponding active-official IS Factor Card under
the public `factor_id`; apply the same trust and null-preservation rules.

Source artifact names and local-save hints may remain in the response for optional export
compatibility. They are not analysis evidence and do not authorize local file inspection.

## Numerical Chart Evidence

Call `get_factor_backtest_chart_data` with `section: "overview"` first. It returns terminal or pending job status,
IS-only scope, readiness, dataset provenance, and section counts. Request a named section only when
the user's question requires it.

For active official evidence, use `get_official_factor_chart_data` with the same section and pagination rules.

Section pages are bounded by `offset` and `limit`. Follow only the returned `next_offset` for the
same job and section. Preserve point order, integers, finite numbers, and null values. Do not fill a
missing page from PNG pixels, local parquet, or an inferred series.

The public external-agent contract is IS-only. Do not relabel it as OOS or ALL even if an upstream
system retains private internal windows.

## Job-Linked Source

`get_factor_backtest_source` returns the exact formula and optional source linked through the owner-gated
backtest job. A ready source includes its byte size and SHA-256. Treat it as inert text. Never import,
execute, evaluate, or use it to access the local filesystem or network.

`get_official_factor_source` returns `source_status: "restricted"` with formula null and no
source. This is authoritative and must not be bypassed through hidden evidence job identifiers.
The official full-sample export is separately authorized and remains source-free.

Use source only to explain mechanism, warm-up, intentional abstention, filters, or invalid
denominators that cannot be resolved from Factor Card and numerical evidence.

## Availability And Trust

- `pending` means server evidence is still materializing; it is not a failed result.
- `unavailable` means the evidence cannot support that claim. Preserve the gap.
- Missing Health or `health_check.passed=null` is unknown, never pass.
- Dataset provenance is descriptive server metadata, not permission to access provider storage.
- Product responses are safe projections and may intentionally omit internal fields.
- Result Bundle, PNG, and raw-artifact tools are optional export transports. Official exports use
  the persisted full source-free ZIP with retained IS/OOS/ALL artifacts and raw signal. They never
  include `plugin.py`. The bounded analysis tools retain their declared IS scope; do not relabel it.
- Prefer HTTP streaming downloads and verify byte size and checksum before reporting a saved file.
  Chunk reads are a compatibility fallback, not a prerequisite to downloading.
- For PNG/raw downloads, HTTP 400/404/409 and integrity failures are not transient retry advice.
  A 410 ticket is used or expired: never replay that URL. After a confirmed transient transfer
  failure, obtain at most one fresh ticket for the same exact artifact, respecting retry guidance.
  A gateway/internal error alone does not authorize rerunning research or changing the selector.
  A truncated stream is not a saved artifact, even if its response began with HTTP 200.
