# Connection recovery and version diagnostics

Use this shared policy for every Quandora Skill when a real connection failure occurs
and for the first-use release check. A release check never blocks ordinary business work.

## Recover automatically

Use only the configured `quandora` MCP connection. OAuth and credentials remain
host-managed. Let the host complete automatic token refresh first, then use its supported
reconnect or tool-discovery recovery within existing permissions. The Agent handles routine
recovery and resumes the original task without asking the user to interpret tokens or run commands.
Do not start concurrent authorization flows or repeat failed recovery indefinitely.

After successful recovery, retry an affected read once. If a mutation's outcome is uncertain,
first inspect the existing operation/status and reuse the original idempotency key only when the
canonical action supports retry. Never create a replacement backtest or Trading run, or repeat a
start/stop with a new key, merely because a response was lost.

Only when the host reports terminal authorization failure or explicitly requires fresh consent
should the Agent initiate the supported host-native OAuth flow. Ask the user only to complete
unavoidable browser sign-in, MFA, consent, or host approval. Respect cancellation and security
denials. Resume and verify the original workflow afterward. If the host provides no supported
recovery capability, explain the concrete connection blocker without inventing commands or
claiming success. Do not reinstall a working plugin for authentication or discovery failures.

Do not display token lifetimes, expiry explanations, or copyable connection-refresh prompts.
Never inspect, print, copy, store, or request credential values, token stores, authorization codes,
PKCE verifiers, or pasted secrets. Never bypass MCP with private service APIs, raw internal HTTP,
or an improvised credential-refresh script.

## Connected, but workflow tools are missing

A successful version check or `get_factor_mining_status` proves only that particular
read works. It does not prove that the connection exposes the tools needed for the
user's workflow. A current plugin package cannot add permissions to an existing OAuth grant.

Before declaring a workflow unavailable, use the host's supported tool search/discovery
and complete any discovery pagination. Compare the resulting catalog with the relevant
Skill's required tools. For Portfolio creation this includes `list_strategy_folders`,
`list_strategies`, `create_portfolio` and `submit_portfolio_backtest`. Do not call a mutation
merely to check availability.

If only a subset is missing, distinguish three cases: incomplete host discovery,
an older authorization missing workflow scopes, or a server-side surface restriction.
Use explicit host authorization diagnostics when available; missing tool names alone
do not establish which case applies. An update notice saying the package is current
does not resolve any of these cases.

Try supported discovery/reconnect recovery once within the existing grant. If the host
reports missing scopes or requires new consent, use the existing connector's native
authorization flow below and let the user approve any additional permissions. Never
silently broaden a grant. If this host exposes no recovery action, state which workflow
tools remain absent and that the existing Quandora connector needs authorization/discovery
recovery; do not stop at a generic "tools unavailable" message or recommend reinstalling.

After recovery, rediscover the required tools and verify a relevant authorized read
before resuming the user's task. Do not report Portfolio creation as ready solely because
the version check or Factor status succeeds. Keep unavailable client checks explicit.

## Host-native authorization fallback

These paths are for the Agent only after automatic recovery cannot restore authorization; they
are not boilerplate instructions to display to the user. Use only capabilities actually available
in the current host, and involve the user only for unavoidable interaction:

- Codex CLI/TUI: `codex mcp login quandora`.
- Codex Desktop: authorize the existing plugin-provided Quandora connector.
- Kimi Code: `/mcp-config login plugin-quandora:quandora`.
- Claude Code: authenticate `quandora` through `/mcp`.
- Claude Desktop: authorize the existing `quandora` connector at
  `https://mcp.quandora.ai/quant`; do not create a duplicate connector.
- CodeBuddy/WorkBuddy: reconnect the existing plugin-managed Remote MCP server and finish
  host-native browser authorization if required.

Use a new chat or host restart only if the host requires it to reload authorized tools; do not
claim a reload is necessary for every failure. The package's two documented Claude Desktop Code
launchers are authorization-only, not business-workflow tools.

The sole direct HTTP exception is consumption of an unmodified, opaque, short-lived
Result Bundle URL returned by `download_result_bundle`. It may be retried or resumed until
expiry using the same URL. Never construct, alter, persist, log, or summarize that URL.
Follow [Unified Result Bundle Download](result-bundle-download.md). This is not permission
to call internal APIs or obtain credentials outside the host-managed connection.

## Check releases once per session

On first Quandora use in each session, read actual installed metadata from the **same installed package**
that supplied this Skill. Call `check_quandora_plugin_version` once; reuse the result across all Skill
handoffs. If installed metadata is unavailable, report unknown without guessing. Follow the reviewed
[host update guide](plugin-update.md) for the legacy query fallback, explicit
pins, update authority, marketplace refresh and host-specific installation/reload steps.

A failed check is nonblocking. Do not repeat notices for the same recommended release in the session.
Respect existing update authorization; a research request alone does not authorize installation.
Never automatically downgrade or switch release channels. Preserve explicit version pins.

The actual installed version comes from host metadata or this package's host manifest, never from
memory, the cache folder name, a remote manifest or the server recommendation. Do not hardcode labels.
Version advice never establishes business compatibility or expired OAuth. Do not reinstall for an
OAuth failure. Installation is not proof that the current session loaded the updated Skills.
