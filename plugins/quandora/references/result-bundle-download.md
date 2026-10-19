# Unified Result Bundle Download

Use `download_result_bundle` for every complete Result Bundle export. Pass only `kind` and
the exact canonical `id` already selected by the user's task:

| kind | id |
| --- | --- |
| `factor` | Terminal Factor job ID |
| `official_factor` | Active official Factor ID |
| `strategy` | StrategyRun ID |
| `portfolio` | Owner PortfolioRun ID |
| `portfolio_share` | Authorized Portfolio Share ID |

Preserve the owning Skill's readiness and bounded metadata observation rules. Only
`available` or readable `partial` metadata with a returned URL is downloadable. Pending,
unavailable, integrity failure and authorization denial remain distinct outcomes.

The tool returns a resource link and the same short-lived `download_url`, exact `size_bytes`,
SHA-256 and manifest metadata. Use the host's supported HTTP/file capability to stream that
unchanged URL into a task-created `.partial` file. The URL supports files larger than 10 MiB;
do not choose or orchestrate per-kind ticket and base64 chunk tools.

After a transient interruption, make at most two transfer retries. Resume the same URL with
`Range: bytes=<verified local byte count>-` and `If-Range` set to the original strong ETag.
Append only a 206 response whose Content-Range starts at that exact byte count. A 200 means
restart the task-created partial from zero. After expiry, call the same tool once for a new URL;
resume only if the returned size and SHA-256 still match. Never append different snapshots.
Stop on authorization or integrity failure. Do not bypass host download or network restrictions.

Before declaring success, verify the entire local file's exact size and SHA-256, ZIP magic and
openability, safe relative archive entries, and manifest omissions. Atomically rename only the
verified file to the owning Skill's safe destination. Do not execute, rebuild or repackage archive
contents, overwrite unrelated files, or expose the capability URL in messages or logs.

If the host cannot fetch HTTP files, report that specific limitation and the verified bundle
readiness. A returned link is not evidence that bytes were downloaded. Never claim a saved file
without a real local artifact. Structured analysis remains available without downloading a ZIP.
