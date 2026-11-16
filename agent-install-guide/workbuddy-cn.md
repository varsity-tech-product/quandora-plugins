# Install and authenticate Quandora in WorkBuddy (中国版 and WorkBuddy AI)

Also read the [shared installation and recovery policy](https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/install-recovery.md). Apply it within this platform's supported scope; preserve the native authorization flow below.

Read this document completely, then install and authenticate Quandora for the user. Perform the installation yourself instead of displaying instructions. WorkBuddy itself owns Quandora's authorization: the user starts it with WorkBuddy's **Connect** button for the `quandora` MCP server and approves it on the browser page WorkBuddy opens. WorkBuddy does not open that page on its own.

This procedure supports a local Agent task in the macOS WorkBuddy application, either the China edition (`WorkBuddy`) or the international edition (`WorkBuddy AI`). It uses the Mac's system shell and WorkBuddy's own bundled runtime; it does not require or install Node.js, Python, Git, Homebrew, a standalone CodeBuddy CLI, or a local MCP server. Do not adapt it to CodeBuddy IDE, Windows, web, cloud, mobile, or a remote Agent.

## Handoff from an unsupported conversation

If the user is in a web/mobile chat rather than the supported local app, ask their
operating system if unknown. For macOS, direct them to install WorkBuddy (China edition:
https://www.codebuddy.cn/work/) or WorkBuddy AI from its official download page, sign in and
open a new local Agent task. Provide:

> Read https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/workbuddy-cn.md and install and connect Quandora. Check existing progress first. I will complete required approvals, sign-in and consent.

For Windows or other hosts, explain that this reviewed installer is macOS-only and offer
**Install from WorkBuddy plugin settings** below; do not adapt the bootstrap or install
substitute runtimes. Do not claim local checks ran from a web session.

The user's installation request authorizes one foreground invocation of the reviewed bootstrap below. Request WorkBuddy's normal approval for that invocation once, then continue. The only other user actions are clicking **Connect** for Quandora in WorkBuddy's MCP settings, browser sign-in, MFA, or the final Quandora authorization action when required, and starting one new local Agent task when asked.

The production trust anchors are:

- Marketplace repository and name: `varsity-tech-product/quandora-plugins`, `quandora`
- Plugin and scope: `quandora@quandora`, `user`
- MCP URL and OAuth resource: `https://mcp.quandora.ai/quant`
- OAuth authorization server: `https://mcp.quandora.ai`
- Protected verification tool: `get_factor_mining_status`

Never request, read, print, copy, or relay an OAuth token, authorization code, client secret, authorization URL, password, passkey, MFA code, or cookie. Do not create a separate MCP entry, replace a conflicting marketplace, edit a plugin cache, or change another plugin.

Do not run an OAuth flow yourself, read or write WorkBuddy's credential or connector stores, or load WorkBuddy application modules. WorkBuddy registers its own OAuth client, opens the browser, receives the `workbuddy://` (China edition) or `workbuddy-ai://` (WorkBuddy AI) callback and stores the grant for its `quandora` MCP server.

## Check existing progress first

If this task already lists Quandora's MCP tools, call `get_factor_mining_status` once without arguments.

- It succeeds: Quandora is installed and authorized. Tell the user and stop; do not run the bootstrap.
- The call fails with an authentication error: continue at **Authorize in WorkBuddy and verify**.
- Quandora's tools are not listed, or the call fails for another reason: run the bootstrap below. An installed Quandora that is not yet authorized may not list its tools; the bootstrap then reports `installed` without reinstalling.

## Run the reviewed bootstrap once

Invoke this complete block as one foreground shell tool call with a timeout of `600000` milliseconds. Do not run its lines as separate approvals, pipe a network response into a shell, add a TTY, retry in a loop, or use `--serve` or `--prewarm`.

```sh
umask 077
quandora_tmp_root="${TMPDIR:-/tmp}"
quandora_tmp_dir=$(/usr/bin/mktemp -d "${quandora_tmp_root%/}/quandora-workbuddy.XXXXXX") || exit 1
quandora_bootstrap="${quandora_tmp_dir}/workbuddy-cn-bootstrap-macos.sh"
quandora_cleanup() { /bin/rm -f "$quandora_bootstrap"; /bin/rmdir "$quandora_tmp_dir" 2>/dev/null || true; }
trap quandora_cleanup EXIT
/usr/bin/curl --proto '=https' --tlsv1.2 --location --fail --silent --show-error \
  --output "$quandora_bootstrap" \
  'https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/plugins/quandora/scripts/workbuddy-cn-bootstrap-macos.sh' || exit 1
quandora_bootstrap_sha=$(/usr/bin/shasum -a 256 "$quandora_bootstrap" | /usr/bin/awk '{print $1}')
[ "$quandora_bootstrap_sha" = '2b18e91e7a2306246b2fd1564ead4e7433866f96101c739a2eb21a055297d241' ] || { echo 'Quandora bootstrap integrity check failed.' >&2; exit 1; }
/bin/sh "$quandora_bootstrap"
```

The guide contains only this download-and-verify boundary. The hash-pinned repository bootstrap discovers and validates the signed WorkBuddy application, preferring the one that launched this Agent task, and its configuration directory without assuming a username, application location, config location, application version, CLI version, plugin version, processor architecture, port, session, or cache version. It then downloads the separately reviewed installer from the same public production repository, verifies its embedded SHA-256 value, and runs it with the selected WorkBuddy application's bundled runtime.

Plugin state changes go only through WorkBuddy's bundled public plugin manager with closed stdin, argument arrays, headless mode, and bounded processes. The installer does not authorize Quandora and loads no WorkBuddy application module. No credential file, connector store, standalone CLI state, or in-use plugin cache is read or modified.

## Installer result

Success is one final JSON object whose `status` is `installed`, `installed` and `enabled` are `true`, `plugin` is `quandora@quandora`, `scope` is `user`, `version` matches the validated marketplace and installed manifests, `edition` is `china` or `international`, `mcpServer` is `quandora`, `authorization` is `workbuddy_native`, and `protectedProbe` is `get_factor_mining_status`. It means the package is installed and WorkBuddy will list the `quandora` server in its MCP settings; it does not mean Quandora is authorized.

On `host_login_required`, ask the user to sign in to WorkBuddy, start a new local Agent task, and paste the same one-sentence request again. On `host_update_required`, direct the user to WorkBuddy's update action (China edition: **Personal Center → Check for Updates**), then restart WorkBuddy and retry in a new task; if the application is missing, install it from its official download page (China edition: `https://www.codebuddy.cn/work/`). If WorkBuddy is already up to date, use **Install from WorkBuddy plugin settings** instead of retrying. Do not install a standalone CLI or another runtime as a substitute.

On `host_layout_unsupported` or `unsupported_host`, use **Install from WorkBuddy plugin settings**; do not retry the bootstrap.

On `cli_unhealthy`, ask the user to close the failed task, restart WorkBuddy, and paste the same one-sentence request once in a new local Agent task. If it repeats, use **Install from WorkBuddy plugin settings**. Do not run a bare CLI, use Terminal as a fallback, or retry inside the failed task.

On any other failed result, report only its safe `message` and `remediation`, then stop. Do not expose subprocess output or retry source conflicts or integrity failures.

## Install from WorkBuddy plugin settings

This path depends on nothing inside the WorkBuddy application, so it still works when an update changes WorkBuddy's internal layout. Ask the user to open WorkBuddy's plugin settings, add the GitHub marketplace `varsity-tech-product/quandora-plugins`, and install `quandora` for their user. Do not write plugin files or WorkBuddy configuration yourself. Then continue at **Authorize in WorkBuddy and verify**.

## Authorize in WorkBuddy and verify

WorkBuddy starts Quandora's authorization only when the user clicks **Connect** for the server; its background connection checks never open the browser. Do not wait for a prompt. After `installed`, tell the user that Quandora is installed and ask them to:

1. Open **Experts · Skills · Connectors → Connectors → Custom MCP** (China edition: **连接器 → 自定义 MCP**). This opens WorkBuddy's MCP server management panel, which also lists MCP servers that come from plugins.
2. Find `quandora`, shown as coming from the plugin `quandora`, marked as needing authentication (需要认证). If it is not listed yet, quit and reopen WorkBuddy; WorkBuddy picks up a newly installed plugin's server when it refreshes plugins and at startup.
3. Click **Connect** (连接) next to it. WorkBuddy opens the Quandora page in the browser, where the user completes sign-in, MFA, and the final authorization action. The server is marked connected afterwards.

The chat input's **+ → Connectors** menu lists only WorkBuddy marketplace connectors; Quandora does not appear there. Do not operate the browser page, open an authorization URL yourself, add a custom MCP server, reinstall the plugin, or start a second attempt while one is open.

After the user finishes, ask them to start one new local Agent task and paste the same one-sentence request. That task resumes at **Check existing progress first**, where Quandora's tools are listed and `get_factor_mining_status` verifies the grant.

Success is a successful `get_factor_mining_status` call through WorkBuddy's own `quandora` server. Then tell the user that production Quandora is installed and authorized. If the call still fails with an authentication error after the user completed the browser step, report that WorkBuddy did not adopt the authorization and stop; do not reinstall, add a custom MCP server, or loop.
