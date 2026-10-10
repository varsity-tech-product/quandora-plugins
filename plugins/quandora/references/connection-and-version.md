# Connection and installed-version policy

Use this policy for every Quandora skill. Version notices and connection recovery
are separate from the user's business task.

## Resolve the installed version

On first entry into any Quandora skill in a conversation, check at most once,
before its business entry point. Reuse the recorded outcome across all skills;
a failed, unavailable, or skipped check must not become a retry loop.

Obtain the actual installed plugin version from host-provided installed-plugin
metadata. If unavailable, read the `version` field of a manifest in the **same
installed package** that supplied the current skill. From a skill directory,
`../..` is the Quandora package root; its `.codex-plugin/plugin.json`,
`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, or
`.codebuddy-plugin/plugin.json` carries the package version. For a Kimi repository
installation, `kimi.plugin.json` at the installed repository root also carries it.
Prefer the current host's manifest. These bundled manifests must agree.

Never copy a release label into a skill or this policy. Never substitute memory,
a cache-folder name, the host application version, a remote manifest, or the
server's latest version for the installed version. If installed metadata is
missing, unreadable, or inconsistent, skip the check silently and continue the
user's task; do not guess or claim the plugin is outdated.

If `qd_plugin_ver` is available and the installed version is known, pass that
value verbatim as `installed_version`. Treat it as an opaque release label;
do not parse, order, or normalize it.

- `update_available=false`: continue silently.
- `update_available=true`: briefly state the installed version and the service's
  recommended version in the user's language, make clear the current task can
  continue, then immediately continue it. This is a label mismatch, not proof
  that the installed package is older or unusable.
- Missing, disabled, invisible, or failed tool: continue without a version notice.
  Do not retry the version check elsewhere in the conversation. Handle an actual
  connection failure using the recovery rules below.

Never install, update, reload, or reauthorize solely because of a version result.
Do not ask the user to run technical commands or display token lifetimes,
expiry explanations, or copyable connection-refresh prompts. A version result
is not evidence that authentication has expired. The check does not change
business action counts, pagination, confirmation, or idempotency requirements.

## Recover the connection automatically

OAuth and credentials remain host-managed. When a real connection/authentication
failure occurs, let the host complete automatic token refresh first. Use its
supported reconnect or tool-discovery recovery when needed, within the existing
host permissions. The Agent performs these steps and resumes the original task;
do not delegate routine recovery to the user or ask them to interpret tokens.

After the host reports successful recovery, retry an affected read once. For a
mutation with an uncertain outcome, first check the existing operation/status;
reuse its original idempotency key if a retry is supported. Never resubmit a
backtest or start/stop trading with a new key merely because a response was lost.

Only when the host reports a terminal authorization failure or explicitly
requires fresh consent should the Agent initiate the supported host-native
OAuth flow. Ask the user only to complete the unavoidable browser sign-in,
MFA, consent, or host approval; never ask them to run a refresh command. Resume
and verify the original workflow afterward. Respect cancellation and security
denials; do not start concurrent authorization flows or repeat failed recovery.
If no supported recovery capability exists, explain the concrete connection
blocker without inventing commands or claiming success.

Do not reinstall a working plugin for an authentication or discovery failure.
Never inspect, print, copy, store, or request credential values, token stores,
authorization codes, PKCE verifiers, or pasted secrets. Do not bypass MCP using
raw HTTP, private service APIs, or an improvised credential-refresh script.
