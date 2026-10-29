# Quandora

This package contains eight user-facing Skills and one authenticated production MCP connection.
Use it for production research and Simulation workflows. Real Live evidence is read-only through MCP.

## Skills and responsibility

| Skill | Owns | Routes elsewhere |
| --- | --- | --- |
| `account-connection` | Explicit login, reauthorization, account switching and current identity | Research and Trading operations |
| `factor-mining` | Hypothesis, Factor source/validation, authorized backtests, history and export | Deep Factor diagnosis |
| `factor-analysis` | Existing Factor evidence, validity and controlled experiment design | Authoring and submission |
| `strategy-building` | Eligible Factors, immutable Strategy definitions and requested backtests | Deep diagnosis and multi-Strategy composition |
| `strategy-analysis` | Existing Strategy results and reusable logic cards | Definition changes and backtest submission |
| `portfolio-building` | Candidate selection, initial capital weights, immutable Portfolios, backtests, discovery/favorites and sharing | Deep Portfolio diagnosis and Trading management |
| `portfolio-analysis` | Actual-member Portfolio backtest comparisons and incremental-value diagnosis | Selection/creation, sharing and forward evidence |
| `portfolio-trading-analysis` | Simulation account/run management and Simulation/real Live forward analysis | Backtest authoring and all real Live writes |

Alongside account management, six Skills cover backtests and one covers forward tests. The
[research intent and evidence contract](references/research-workflows.md) defines request modes,
capability-aware analysis and handoffs. Design-only requests do not create resources. Exact supplied
members/weights are not silently optimized. Analysis suggestions do not authorize experiments;
already-authorized work continues through the owning builder without repeated confirmation.

Each Skill uses only relevant tools and preserves opaque identities and pagination. Portfolio
research accepts one to five distinct immutable Strategies with equal or explicit positive initial
capital weights. Capital allocation is not continuous rebalancing. Definitions and Runs remain
separate, and actual source StrategyRuns and aligned windows govern comparisons. Missing advanced
joint-risk evidence limits conclusions rather than generating invented correlations or contributions.

Portfolio backtests use `submit_portfolio_backtest` on the exact immutable definition, following
its current exchange/schema contract. FM prepares missing or stale sources; PB returns persisted
state and authoritative research. Preserve the automatic association returned by
`get_portfolio_backtest` in `run.automatic_paper`; pending/absent association does not authorize
an extra start. Portfolio Trading Analysis observes that exact association and owns explicitly
requested Simulation operations. Legacy simulated `live` aliases do not describe real Live accounts.
Real Live uses separate account-oriented read tools; its writes remain frontend-only.

## Connection

Supported hosts load the plugin's `quandora` remote HTTP MCP declaration. Complete the
host-native browser authorization flow for initial setup; reload tools only when the host requires it.
Do not create a local MCP server or paste credentials.

For incidental failures, the Agent lets the host refresh the connection automatically first, then uses supported reconnect
or tool discovery and resumes the task. User interaction is limited to unavoidable sign-in or
consent after terminal authorization failure, a host consent requirement, or an explicit user
request to connect, reauthorize or switch accounts. Use [Quandora Account](skills/account-connection/SKILL.md)
for these requests; verify the active identity after login. Do not
reinstall a working plugin, display token lifetimes, or ask users to run refresh commands.
Check the release once per session using actual installed package metadata, then follow the
[host update guide](references/plugin-update.md) within existing update authority.
See [Connection and Security](references/connection-and-security.md) for bounded retries, uncertain
mutation recovery, and host-native fallbacks. Never request secrets or bypass MCP with internal HTTP.

### Claude Desktop Code authorization bridge

The plugin intentionally ships these two host-support assets:

```text
scripts/claude-mcp-login-macos.sh
scripts/claude-mcp-login-windows.ps1
```

They support the authorization step of the one-click Claude Desktop Code Agent installation flow,
where redirected command input/output cannot host the official interactive `claude mcp login`
prompt. Both launch only `plugin:quandora:quandora` in a native interactive
terminal, keep OAuth output out of status files, and require manual browser identity and consent.
They are not general shell utilities, local MCP servers, or credential helpers. Interactive Claude
Code users should use the direct host command instead.

## Search and pagination

Factor discovery actions accept supported `query` and `filters` fields. Canonical Strategy and
PortfolioFamily/Run lists use parent identities and pagination, without query/filter arguments. Continuation requests
must preserve the same query, filters, archive mode, and page size while copying the returned
opaque page token byte-for-byte.

## Result files

All complete Result Bundle exports use `download_result_bundle(kind, id)`. Follow
[Unified Result Bundle Download](references/result-bundle-download.md) for the canonical
selectors, retryable HTTP links, resume and integrity verification. Large ZIPs do not use
MCP base64 chunks; the host needs an HTTP/file download capability.

When local file writes are supported, verified Factor and Strategy bundles use these default
workspace-relative destinations:

```text
Quandora result/factor/<factor_slug>.zip
Quandora result/strategy/<strategy_slug>.zip
```

The validated Factor source's exact non-empty lowercase snake_case `FACTOR_TYPE` determines the
factor slug; it never silently falls back to a generic `factor` slug. The user-facing submitted
Strategy name determines the Strategy slug. The verified archive remains intact, and returned
metadata and manifests are authoritative for readiness, contents, omissions, and integrity.

## Safety boundary

- OAuth and credentials are host-managed and must never be requested, printed, copied, or stored.
- Carry explicit authorization across ordinary calls and Skill handoffs; ask only for missing
  consequential choices or authority.
- An ambiguous response is not proof of failure and does not authorize a changed replacement.
- Simulation lifecycle and real Live read-only inspection are separate; all Live changes are frontend-only.
- User-facing answers follow the user's language while preserving tool names and schema fields
  exactly.

Community discovery supports authorized contextual research and separate Portfolio favorites.
Sharing supports public or specified-user grants with required UTC dates, active-grant extensions
and concurrency-checked intro edits. Current grant/channel constraints are server-owned; shared
child visibility does not create Mine ownership or execution eligibility. Factor/Strategy stars
remain independent of LibraryFolder placement.

Simulation creation/start uses a recoverable operation with the same request identity on retries.
PB owns capital, quotas, grants and lifecycle rules. Net-ledger evidence owns account finance;
legacy member observations must not be summed into an authoritative net account. Real Live reads
preserve observation freshness and the bounded recent scope of orders/fills.

Named-object discovery uses `search_quandora_objects`; exact identities, current/historical source
filters and authorization remain authoritative. Strategy backtest intent uses a fresh
`client_request_id` per requested Run and the same identity only for unchanged retries.

## Production host installation support

Production also retains the reviewed WorkBuddy support scripts:

- `scripts/workbuddy-cn-bootstrap-macos.sh`
- `scripts/workbuddy-cn-install-macos.js`
- `scripts/workbuddy-cn-oauth-macos.js`
- `scripts/workbuddy-mcp-login-macos.sh`
- `scripts/workbuddy-mcp-login-windows.ps1`

Use the [production installation guides](../../agent-install-guide/workbuddy-cn.md) for their supported scope and integrity checks.
