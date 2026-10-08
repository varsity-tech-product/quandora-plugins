# Install and authenticate Quandora in WorkBuddy 中国版

Also read the [shared installation and recovery policy](https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/install-recovery.md). Apply it within this platform's supported scope; preserve the native authorization flow below.

Read this document completely, then install and authenticate Quandora for the user. Perform the work instead of displaying instructions or sending the user through WorkBuddy's plugin UI.

This procedure supports a local Agent task in the macOS WorkBuddy China application. It uses the Mac's system shell and WorkBuddy's own bundled runtime; it does not require or install Node.js, Python, Git, Homebrew, a standalone CodeBuddy CLI, or a local MCP server. Do not adapt it to WorkBuddy AI international, CodeBuddy IDE, Windows, web, cloud, mobile, or a remote Agent.

## Handoff from an unsupported conversation

If the user is in a web/mobile chat rather than the supported local app, ask their
operating system if unknown. For macOS, direct them to https://www.codebuddy.cn/work/
to install WorkBuddy China, sign in and open a new local Agent task. Provide:

> Read https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/workbuddy-cn.md and install and connect Quandora. Check existing progress first. I will complete required approvals, sign-in and consent.

For Windows or other unsupported hosts, explain that this reviewed installer is
macOS-only; do not adapt the bootstrap or install substitute runtimes. Do not
claim local checks ran from a web session.

The user's installation request authorizes one foreground invocation of the reviewed bootstrap below. Request WorkBuddy's normal approval for that invocation once, then continue. The only other user action is browser sign-in, MFA, or the final Quandora authorization action when required.

The production trust anchors are:

- Marketplace repository and name: `varsity-tech-product/quandora-plugins`, `quandora`
- Plugin and scope: `quandora@quandora`, `user`
- MCP URL and OAuth resource: `https://mcp.quandora.ai/quant`
- OAuth authorization server: `https://mcp.quandora.ai`
- Protected verification tool: `fm_status`

Never request, read, print, copy, or relay an OAuth token, authorization code, client secret, authorization URL, password, passkey, MFA code, or cookie. Do not create a separate MCP entry, replace a conflicting marketplace, edit a plugin cache, or change another plugin.

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
[ "$quandora_bootstrap_sha" = '055deeb23f06769d6876ad0bef965b3c08784953284932487b7f56535f44f05f' ] || { echo 'Quandora bootstrap integrity check failed.' >&2; exit 1; }
/bin/sh "$quandora_bootstrap"
```

The guide contains only this download-and-verify boundary. The hash-pinned repository bootstrap discovers and validates the signed WorkBuddy China application and active account configuration without assuming a username, application location, config location, application version, CLI version, plugin version, processor architecture, port, session, or cache version. It then downloads the separately reviewed installer components from the same public production repository, verifies their embedded SHA-256 values, and runs them with the selected WorkBuddy application's bundled runtime.

Plugin state changes go only through WorkBuddy's bundled public plugin manager with closed stdin, argument arrays, headless mode, and bounded processes. OAuth uses WorkBuddy's account-scoped encrypted connector store and an ephemeral loopback callback. No credential file, unrelated connector, standalone CLI state, or in-use plugin cache is modified.

## User action and completion

Only when the installer emits `{"status":"progress","step":"browser_opened"}`, tell the user that the Quandora browser page is open and wait while they complete sign-in, MFA, and the final authorization action. Do not operate that page or start a second attempt. If stored authorization passes the protected probe, no browser event is emitted and no browser action is required.

Success is one final JSON object whose `status` is `completed`, `installed`, `enabled`, and `authenticated` are `true`, `plugin` is `quandora@quandora`, `scope` is `user`, `version` matches the validated marketplace and installed manifests, `protectedProbe` is `fm_status`, and `toolCount` is a positive integer.

On `host_login_required`, ask the user to sign in to WorkBuddy, start a new local Agent task, and paste the same one-sentence request again. On `host_update_required`, direct the user to WorkBuddy **Personal Center → Check for Updates**, then restart WorkBuddy and retry in a new task; if the application is missing, use `https://www.codebuddy.cn/work/`. These are the official recovery paths—do not install a standalone CLI or another runtime as a substitute.

On `cli_unhealthy`, ask the user to close the failed task, restart WorkBuddy, and paste the same one-sentence request once in a new local Agent task. If it repeats, direct them to **Personal Center → Check for Updates** before retrying. Do not run a bare CLI, use Terminal as a fallback, or retry inside the failed task.

On any other failed result, report only its safe `message` and `remediation`, then stop. Do not expose subprocess output or retry source conflicts, integrity failures, unsupported hosts, or missing native OAuth capabilities.

After success, tell the user that production Quandora is installed and authorized. If the current task does not expose the newly installed skills, ask them to start one new WorkBuddy task; do not reinstall the plugin or add an MCP manually.
