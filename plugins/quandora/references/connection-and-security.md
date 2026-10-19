# Connection recovery and version diagnostics

Use this shared policy for every Quandora Skill when a real connection failure occurs
or an explicit version diagnostic is needed. Routine business tasks do not require a version probe.

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

## Diagnose versions on demand

Use `check_quandora_plugin_version` only for a requested version diagnostic or a plausible
package/server mismatch; never as a mandatory entry probe. Read the actual installed version
from host-provided installed-plugin metadata, or the `version` field of a manifest in the **same
installed package** that supplied this Skill. From a Skill directory, `../..` is the package root;
its `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and
`.codebuddy-plugin/plugin.json` carry the version. Kimi repository installations also have
`kimi.plugin.json` at the installed repository root. Prefer the current host's manifest; bundled
manifests must agree.

Never hardcode a release label in Skill instructions. Do not substitute memory, a cache-folder
name, the host application version, a remote manifest, or the server's latest version. If installed
metadata is missing, unreadable, or inconsistent, skip the check without guessing or claiming the
plugin is outdated; explain the limitation only if the user requested the diagnostic.

Pass the known value verbatim as `installed_version`, treating it as an opaque release label.
An unavailable or failed check must not block the business task or become a retry loop. A false
`update_available` needs no unsolicited notice. A true value means a label mismatch, not proof
that the installed package is older or unusable: briefly state the installed and recommended
versions in the user's language and continue the task. A version result is not evidence of expired
authentication and must not trigger installation, reload, or reauthorization on its own.
