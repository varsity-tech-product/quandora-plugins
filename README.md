<p align="center">
  <img src="assets/banner.png" alt="Quandora" width="100%">
</p>

# Quandora Plugins

<p align="center">
  <a href="https://quandora.ai"><img src="https://img.shields.io/badge/Built%20by-Quandora-F28C00?style=flat" alt="Built by Quandora"></a>
  <a href="https://discord.com/invite/9WshZMnjGE"><img src="https://img.shields.io/badge/Join-Discord-5865F2?style=flat&logo=discord&logoColor=white" alt="Join Discord"></a>
  <a href="https://x.com/quandora_labs"><img src="https://img.shields.io/badge/Follow-%40quandora__labs-000000?style=flat&logo=x&logoColor=white" alt="Follow on X"></a>
</p>

Quandora connects supported hosts to the production MCP service for Factor, Strategy and
Portfolio research, Simulation management and read-only Live analysis.

## Included workflows

| Skill | User goal |
| --- | --- |
| Quandora Account | Connect, reauthorize, switch accounts, verify the active identity, and report problems to the Quandora team. |
| Factor Mining | Turn a research hypothesis into a validated Factor and backtest. |
| Factor Analysis | Diagnose exact Factor evidence and propose controlled improvements. |
| Strategy Building | Select eligible Factors, create or revise a Strategy, and submit requested backtests. |
| Strategy Analysis | Diagnose a Strategy backtest and provide a reusable Strategy logic card. |
| Portfolio Building | Select complementary Strategies, allocate initial capital, build/backtest, discover, favorite or share a Portfolio. |
| Portfolio Analysis | Evaluate an existing Portfolio backtest against its actual members and declared baselines. |
| Portfolio Trading Analysis | Manage Simulation accounts/runs and analyze Simulation or real Live forward evidence. |

The plugin exposes eight Skill directories to each supported host: account management, six
backtest research workflows and one forward-test workflow. Account authorization uses the
host capabilities actually available; the bundled CLI fallback is specific to Codex. Analysis-only requests
are read-only. Explicit Simulation management uses supported writes; real Live remains read-only.
Authentication, tool schemas, admission and financial facts remain server-owned. See
[research workflows and evidence](plugins/quandora/references/research-workflows.md).

### Install

#### Codex

Codex Desktop:

```
Source: varsity-tech-product/quandora-plugins
Git ref: leave blank
Plugin: quandora@quandora
```

The agent-readable guides also handle users starting in a web conversation: they
provide the official desktop download and a continuation prompt for a supported
local session. Public GitHub distribution does not require a GitHub account.
The agent checks existing tools, recovers supported installation failures, and
asks only for required approvals or sign-in/consent. See the
[shared recovery policy](agent-install-guide/install-recovery.md) and
[verification checklist](agent-install-guide/verification.md).

You can also ask Codex Desktop to install and connect Quandora for you:

```
Read https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/chatgpt.md completely, then install and authenticate Quandora for me. Ask me to approve any required installation permissions; I will complete browser sign-in and consent myself.
```

Codex may ask before running the Codex CLI setup commands. These commands install the Quandora plugin into Codex, write Codex plugin/MCP configuration, and open Quandora OAuth. They do not grant Quandora access to your local files.

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins
codex plugin add quandora@quandora
```

Authorize when prompted. If Codex does not open the authorization flow automatically, use:

```bash
codex mcp login quandora
```

After installation or authorization, open a new chat. If Codex Desktop still does not expose Quandora tools, fully quit and reopen Codex Desktop.

When a Quandora connection is unavailable, follow the installation guide to identify the failed stage and resume there. Do not reinstall a working plugin for an OAuth or tool-discovery failure. OAuth and credentials remain host-managed: agents must never request API keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, or pasted credentials.

#### Claude

Claude Desktop Code supports an Agent-readable one-sentence installation flow:

```text
Read https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/claude.md completely, then install and authenticate Quandora for me. Ask me to approve any required installation permissions; I will complete browser sign-in and consent myself.
```

The linked guide supports local Claude Desktop Code and local Claude Code CLI sessions on macOS or Windows, uses the official Claude Code plugin and MCP commands, and invokes the platform-native interactive OAuth path. The normal Chat tab uses the separate Connector workflow described below.

Claude Code in an interactive terminal:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin install quandora@quandora
claude mcp login plugin:quandora:quandora
```

The plugin ships fixed-purpose OAuth launchers for Claude Desktop Code under `plugins/quandora/scripts/`: `claude-mcp-login-macos.sh` and `claude-mcp-login-windows.ps1`. The macOS launcher uses the operating system's `/usr/bin/script` PTY, and the Windows launcher uses Windows PowerShell 5.1 to open a native console. Both invoke only the official `claude mcp login plugin:quandora:quandora` flow, suppress OAuth output logging, and leave browser sign-in, MFA, and consent to the user.

Claude Desktop's normal Chat tab uses its Connector workflow rather than the local Claude Code plugin. Add and connect:

```text
Name: quandora
URL: https://mcp.quandora.ai/quant
```

Use Settings -> Connectors, click Connect, complete Quandora authorization in the browser, then start a new chat. Local result-folder archiving is guaranteed only in hosts that expose local file writes; Claude Desktop may instead provide downloadable files in its sandbox.

#### Cursor Desktop

In a new Cursor Desktop Agent chat, enter:

```text
/add-plugin quandora@https://github.com/varsity-tech-product/quandora-plugins
```

After installation, authenticate the plugin-provided `quandora` Remote MCP server in the browser, then start a new Agent chat before invoking Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, or Paper Trading.

#### CodeBuddy CLI

CodeBuddy CLI installs the plugin through its official plugin manager. If the standalone CLI is not installed, use the official installer for the host platform.

macOS and Linux:

```bash
curl -fsSL https://www.codebuddy.cn/cli/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
```

Windows PowerShell:

```powershell
irm https://www.codebuddy.cn/cli/install.ps1 | iex
$env:Path = "$env:USERPROFILE\AppData\Local\codebuddy\bin;$env:Path"
```

Install or update the Quandora plugin:

```bash
codebuddy plugin marketplace add varsity-tech-product/quandora-plugins --name quandora
codebuddy plugin install quandora@quandora --scope user
codebuddy plugin list --json
```

CodeBuddy uses the plugin-managed remote HTTP MCP server and opens its native browser authorization flow when the server connects. No Python, Node.js, local MCP server, or Quandora API key is required.

#### WorkBuddy China edition

On macOS, give a local WorkBuddy China Agent this one-sentence prompt:

```text
Read https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/workbuddy-cn.md completely, then install and authenticate Quandora for me.
```

The guide downloads one hash-pinned, repo-owned macOS bootstrap. That bootstrap discovers the signed local WorkBuddy China application and active config, downloads and verifies the reviewed installer components from this public repository, and runs them with WorkBuddy's bundled runtime. The installer closes CLI stdin, bounds every plugin-manager call, installs and verifies the managed package, writes only Quandora's account-scoped encrypted OAuth slot, and verifies the protected `get_factor_mining_status` tool. It does not require a fixed application path, config path, WorkBuddy/CLI/plugin version, standalone runtime, custom MCP server, or pasted credential.

#### Kimi Code CLI

Install the Quandora plugin directly from GitHub:

```text
/plugins install https://github.com/varsity-tech-product/quandora-plugins
```

Confirm the source, inspect the installation, and reload plugins:

```text
/plugins info quandora
/plugins reload
```

Start a new session, authorize the plugin-provided MCP server, and verify the connection:

```text
/mcp-config login plugin-quandora:quandora
/mcp
```

Complete authorization in the browser, then start a new session before invoking Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, or Paper Trading.

## Use

In Codex, select **Quandora Account** from the Skill picker or reference
`$account-connection` and ask to show the current account, open authorization,
reauthorize, or switch accounts. Explicit authorization requests start a new native
flow even when already connected. You complete browser sign-in and consent; the
agent verifies the active account afterward. Ask it to report a problem and it files a
text report with the Quandora team after you confirm, then gives you the report reference. See the
[account workflow](plugins/quandora/skills/account-connection/SKILL.md).

Ask naturally or invoke a Skill explicitly when the host supports Skill commands:

```text
/quandora:factor-mining show public factor tasks
/quandora:factor-analysis analyze my latest factor result
/quandora:strategy-building list eligible factors matching momentum
/quandora:portfolio-building combine these exact Strategies, backtest, and share when requested
/quandora:portfolio-analysis compare my Portfolio backtest with its actual members
/quandora:strategy-analysis analyze my latest completed strategy
/quandora:portfolio-trading-analysis analyze my Simulation performance or manage the selected account
```

Mutating workflows preserve existing explicit authorization across calls and Skills; ask only
for unresolved material choices or additional authorization. A timeout or ambiguous response is never treated as permission to create a
replacement command.

## Result files

When the host supports local files and the user requests or reaches the relevant export step,
verified Result Bundles are saved relative to the active workspace:

```text
Quandora result/factor/<factor_slug>.zip
Quandora result/strategy/<strategy_slug>.zip
```

The verified archive is retained without automatic extraction or reconstruction. Server-returned
metadata and manifests remain authoritative for readiness, contents, omissions, and integrity.

## Connection recovery and security

The Agent lets the host refresh the connection automatically first, then uses supported reconnect
or tool discovery and resumes the task. User interaction is limited to unavoidable sign-in or
consent after terminal authorization failure or an explicit host consent requirement. Do not
reinstall a working plugin, display token lifetimes, or ask users to run refresh commands.
Version diagnostics remain on demand and use the actual installed package metadata.
See [Connection and Security](plugins/quandora/references/connection-and-security.md) for bounded retries, uncertain
mutation recovery, and host-native fallbacks. Never request secrets or bypass MCP with internal HTTP.

For missing workflow permissions in Codex Desktop, the Agent selects an available native
authorization action or the verified same-host official CLI. A plugin-management lookup failure
does not by itself end recovery. The user only handles required approval, sign-in or consent;
the Agent verifies the needed reads and resumes the task. See
[Codex authorization recovery](plugins/quandora/references/codex-authorization-recovery.md).

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).

## Keeping Quandora updated

Agents check the release on first use per session. With existing update authority, refresh the
marketplace before updating the installed plugin; preserve explicit pins and authentication.
See the [host update guide](agent-install-guide/update.md) for Codex, Claude Code, other-host
limits, and the distinction between installation and loading. Offline clients and cached sessions
may not receive release notices immediately.
