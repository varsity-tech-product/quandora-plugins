# Strategy delivery recovery

Execution completion, archive readiness, and download channel limits are separate facts.
A `partial` archive does not mean the economic backtest failed or every requested member
is permanently unavailable. Read trustworthy ready members independently.

When `sb_get_artifact` provides `delivery`, follow its closed recovery facts:

- `scheduled` / `running` and `archive_recovering`: valid server-side work, not an MCP
  connection failure. Wait using a host-native timer for `retry_after_seconds`, then
  re-read the same artifact and exact public Run identity; do not resume or resubmit.
- `stopped`: report the safe reason; do not repeatedly wait for that member.
- `unknown`, or legacy `sync_failed` without recovery facts: do not infer permanent loss
  or claim recovery is scheduled. Read `sb_get_run` once, then use bounded spaced
  artifact observations if the user's task still needs that evidence. Do not infer
  readiness merely from overall completed/partial state.
- `integrity_failed`, authorization errors and transport errors retain their actual
  meanings. Do not relabel them as ordinary archive waiting.

Across one ongoing task, recovery observation is bounded to at most 30 follow-up calls
and 15 minutes of elapsed waiting in total, shared across needed members. Space calls
by at least 30 seconds and respect any longer server hint. Never tight-loop or reset
this budget for each member. Stop earlier on readiness, final failure, host interruption
or a smaller host budget. Continue independent useful work while evidence is pending.
At the bound, preserve the exact public Run and latest safe state for later continuation;
report the actual pending/unknown evidence, not a fabricated MCP failure. Do not create
background automation or promise the host will keep a /goal alive. Existing bounded
bundle download/recheck rules still apply to export; this is not permission to keep
minting tickets or to rebuild a partial ZIP from individual files.

For requested complete-file/result delivery, prefer `sb_bundle_ticket` and the existing
verified URL-first export workflow. For metric/style/attribution analysis use the
appropriate structured artifact or `sb_analysis_data`; a ZIP does not replace the
six-chart numerical evidence boundary. Mint downloads only within an authorized export.

An inline `too_large` is a limit of that read channel, not missing data or an MCP outage.
Do not repeat the same inline read or rerun the backtest. If the user wants the full
result file, route to Strategy Building's bundle export; preserve existing supported
single-file download behavior for a specific trade-file request. Verify the bundle
manifest contains the requested member; a readable partial may still omit it.
A bundle manifest describes its immutable selected snapshot. Its historical missing or
failed member entries are not a fresh recovery observation. Read the current run/artifact
for recovery facts; a later current snapshot can include healed members without changing
an older ZIP. Do not claim the agent read contents from a ticket alone.

The 10 MiB / 40-call `sb_bundle_chunk` fallback cap applies only to MCP chunks. Larger
ZIPs can still use the normal returned download URL. If that URL fails after its allowed
retry and the ZIP exceeds the fallback cap, report a download-channel limitation and
that the bundle is ready when metadata proves it. Do not attempt an oversized chunk
fallback, claim the file does not exist, or claim download succeeded. Smaller fallback
ZIPs retain exact revision, offset, size, digest and terminal-chunk verification.
