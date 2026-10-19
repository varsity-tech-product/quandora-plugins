# Codex native authorization recovery

Use this procedure after the [shared connection policy](connection-and-security.md)
establishes missing permissions for the requested workflow or terminal authorization failure.
If permissions are already present, recover discovery or report server exposure instead.
The Agent initiates recovery within the requested task and the host's permissions.
Do not ask the user to paste a recovery prompt or run the command when the Agent can run it.
Only the user approves additional access through browser consent or a required host approval.

## Select an available recovery capability

Prefer a supported native reauthorization action for the existing Quandora connector when
the host actually exposes one. Use the installed connector identity returned by the host;
do not invent an action name or guess plugin IDs in a loop.

`plugin_not_found` from a plugin-management lookup is not an authorization denial and does
not prove that the configured MCP connection is absent. If this lookup fails, or the host
offers no reauthorization action, check the permitted local CLI route below before declaring
recovery unavailable. A restriction on automating the desktop UI does not by itself forbid
an independently permitted official CLI command.

Respect a security denial; never try another execution path to bypass it. If policy blocks
the authorization operation or local execution, preserve that boundary. An unavailable
management capability and an explicit security rejection are different outcomes.

## Verify the existing local connection

This route requires permitted local command execution and the same desktop host and configuration context.
Use the official executable bundled with or used by the active desktop application, as
identified by host metadata or the supported installation. For a local CLI/TUI task, reuse
that task's executable and configuration. Do not assume a global `codex` executable shares the desktop configuration.
Do not switch user, host, home/config directory or profile to find a working login.

Use the same resolved executable for these checks and the login:

```text
codex --version
codex mcp login --help
codex mcp get quandora --json
```

Inspect only the connection name, enabled flag, transport type and URL; do not print the
full configuration, headers or credential fields. Require the existing `quandora` connection
to be enabled, use remote Streamable HTTP, and point exactly to `https://mcp.quandora.ai/quant`.
If the connection is missing or differs, report that conflict and preserve it. Do not create
a duplicate MCP entry, rewrite configuration, install another CLI, or reinstall the plugin.
If the executable/context cannot be established, report this as an unverified local route.

## Start once and observe the result

For a verified connection with a diagnosed need for authorization, the Agent starts one foreground native OAuth flow:

```text
codex mcp login quandora
```

The command omits `--scopes` so the production Auth server can prepare its current consent set.
If a supported host instead supplies explicit scopes, follow the shared policy: preserve
explicit restrictions and request only the additional permissions needed for the task.
Do not send an empty scope or reuse an explicitly stale set as a repair.

Tell the user to complete the browser sign-in, MFA or consent that the host opens; keep
authorization URLs and callback codes out of summaries and saved logs. Observe the native
command until it exits. Do not operate consent for the user, start concurrent logins,
or claim that starting the command means authorization succeeded. Respect cancellation.

## Verify and resume

After a successful callback, use supported MCP discovery and authenticated status diagnostics
to confirm that the new authorization is in use. Do not repeat login when the callback succeeds but the grant remains unchanged.
Report the host's failure to adopt the grant and keep recovery pending.

If server diagnostics include the required tools but the current task does not, use an
available host discovery refresh. Only when this host requires a new task or restart to
reload the catalog should the user perform that action; preserve completed authorization.
Never invent a discovery command or report cached old diagnostics as the post-login result.

Verify the requested reads: Strategy discovery uses `list_strategy_folders` then
`list_strategies` for a returned folder; Portfolio discovery uses `list_portfolio_folders`
then `list_portfolios` for a returned folder. Empty authorized folders are valid results.
For an authorized creation workflow, also verify that its write tools are discoverable.
Do not use a fixed tool count as acceptance; explicit restricted grants can be valid.
Do not create a Portfolio or submit a backtest as a recovery probe. Resume the original
task only after its required tools and relevant read are verified.

If neither the native action nor the permitted same-host CLI is available, name the concrete
missing capability. Give the existing connector's verified host authorization entry when
available and ask the user only for that unavoidable action. Do not invent a settings path,
require a second troubleshooting prompt, or treat the limitation as a Quandora outage.
