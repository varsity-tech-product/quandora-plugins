# Install and authenticate Quandora in ChatGPT/Codex Desktop

Read this document completely, then install and authenticate Quandora using the supported local Codex plugin workflow, within the permissions granted by the user and the execution environment. Before making changes, explain that this adds the third-party Quandora marketplace and installs its plugin for the current user. This document describes the procedure; it does not grant permission by itself.

Run permitted checks and installation commands yourself. Use the client's supported approval flow whenever approval is required for marketplace or plugin changes, and wait for the user. Ask before installing or updating the Codex CLI. The user must complete browser sign-in, MFA, and consent themselves.

If any step is denied as `Untrusted Code Integration` or by another security policy, stop. Do not retry through another shell or script, change permission modes, disable safeguards, or offer a manual command as a workaround for the denial. Report the blocked step and exact non-sensitive error, distinguishing an observed execution error from the agent's own decision not to run a command. If no command ran, say so. A local installation denial is not evidence of a Quandora MCP server outage. Resume only after the user or administrator resolves the restriction through an approved mechanism.

The canonical agent-readable copy of this guide is <https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/chatgpt.md>.

## Required environment

This procedure requires a local ChatGPT/Codex Desktop task that can run local commands and manage Codex plugins. If the current task is web-only, cloud-hosted, mobile, or otherwise cannot access the local plugin manager, stop and ask the user to open a local Codex task in the desktop application.

Use these exact production identities:

- Marketplace repository: `https://github.com/varsity-tech-product/quandora-plugins.git`
- Marketplace branch: `main`
- Marketplace name: `quandora`
- Plugin: `quandora@quandora`
- MCP server: `quandora`
- MCP URL: `https://mcp.quandora.ai/quant`
- Skills: `factor-mining`, `factor-analysis`, `strategy-building`, `strategy-analysis`, and `paper-trading`

Do not create a separate MCP entry. The plugin owns the MCP configuration. Never request or handle an API key, OAuth token, cookie, callback code, or authorization URL.

## 1. Locate the Codex CLI

Prefer the Codex executable bundled with or used by the desktop application. Verify it before continuing:

```text
codex --version
codex plugin marketplace list --help
codex plugin add --help
codex mcp login --help
```

If no compatible Codex executable is available and `npm` is already installed, explain why the CLI installation or update is needed, show the following command, and run it only after the user's approval and if the execution environment permits it:

```text
npm install -g @openai/codex
```

Then resolve the new executable and repeat the checks. Do not install a package manager or another runtime. If the required commands remain unavailable, ask the user to update and restart the desktop application, recheck once, and stop if they are still unavailable.

Use the same resolved executable for every command below.

## 2. Add or refresh the Quandora marketplace

Inspect the configured marketplaces:

```text
codex plugin marketplace list --json
```

If `quandora` is absent, add the production repository:

```text
codex plugin marketplace add https://github.com/varsity-tech-product/quandora-plugins.git --ref main --json
```

If `quandora` already points to that repository and branch, refresh it:

```text
codex plugin marketplace upgrade quandora --json
```

If the name points to any other source, stop and report the conflict. Do not replace or delete it.

## 3. Install or update the plugin

Inspect the managed plugin inventory:

```text
codex plugin list --marketplace quandora --available --json
```

If `quandora@quandora` is not installed, install it:

```text
codex plugin add quandora@quandora --json
```

If it is installed and its version is older than the refreshed marketplace entry, reinstall only this exact plugin:

```text
codex plugin remove quandora@quandora --json
codex plugin add quandora@quandora --json
```

Confirm that it is installed and enabled and that it exposes all five expected skills. Compare the installed version with the version advertised by the refreshed marketplace, not a hardcoded version in this guide. If they still differ after the scoped update above, stop and report both versions; do not repeat removal and installation in a loop.

## 4. Start OAuth authorization

Inspect the plugin-managed MCP server:

```text
codex mcp get quandora --json
```

Require an enabled remote Streamable HTTP server whose URL is exactly `https://mcp.quandora.ai/quant`. If the name resolves to another URL or a local command, stop and report the conflict.

If it is not authenticated, start one foreground native OAuth flow:

```text
codex mcp login quandora
```

The user's browser should open automatically. Tell the user that Quandora is ready for authorization, then wait while they complete any required sign-in or MFA and approve access. Do not operate the consent page for them and do not start a second login while the first is active.

If the first attempt ends because of a timeout or a transient network error, retry once after it has fully exited. Do not use an API key or a local MCP server as a fallback.

## 5. Verify completion

Recheck:

```text
codex plugin list --marketplace quandora --available --json
codex mcp get quandora --json
codex mcp list --json
```

Verify installation, authorization, and MCP tool availability separately. Confirm installation and authorization only when all of the following are true:

1. `quandora@quandora` is installed and enabled from the expected marketplace.
2. Its installed version matches the current marketplace entry.
3. `factor-mining`, `factor-analysis`, `strategy-building`, `strategy-analysis`, and `paper-trading` are present.
4. `quandora` points to `https://mcp.quandora.ai/quant` over remote Streamable HTTP.
5. OAuth is complete and the MCP server is connected.

After those checks pass, use the client's supported MCP tool discovery to verify that the plugin-managed server exposes the expected Quandora tools. Plugin inventory or a connected status alone is not proof of tool availability. Do not request or extract credentials to perform this check, and do not submit a factor, strategy, backtest, or trading task merely to test installation.

If the current task cannot load the newly installed tools, report installation and authorization as complete but tool verification as pending. Ask the user to start a new local desktop task and perform the read-only tool discovery there; do not claim full completion before it succeeds.

End with the observed status and next step, distinguishing:

- **Installation blocked:** report the blocked step and non-sensitive evidence; no claim of MCP connectivity.
- **Installed, authorization pending:** the plugin is present, but OAuth has not completed successfully.
- **Installed and authorized, tool verification pending or failed:** explain whether a new local task is required or discovery returned an error.
- **Complete:** installation, authorization, and read-only MCP tool discovery have all passed.
