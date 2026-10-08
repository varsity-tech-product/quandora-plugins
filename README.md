# Quandora Plugins

<div align="center"><img src=".gitbook/assets/banner.png" alt="Quandora" width="100%"></div>

## Quandora: AI Enabler for Finance Agents

<p align="center"><a href="https://quandora.ai"><img src="https://img.shields.io/badge/Built%20by-Quandora-F28C00?style=flat" alt="Built by Quandora"></a> <a href="https://discord.com/invite/9WshZMnjGE"><img src="https://img.shields.io/badge/Join-Discord-5865F2?style=flat&#x26;logo=discord&#x26;logoColor=white" alt="Join Discord"></a> <a href="https://x.com/quandora_labs"><img src="https://img.shields.io/badge/Follow-%40quandora__labs-000000?style=flat&#x26;logo=x&#x26;logoColor=white" alt="Follow on X"></a></p>

#### Quandora is building an agentic finance infrastructure that turns generic AI agents into professional quant finance agents. Quandora gives AI agents the infrastructure to research markets, generate alphas and strategies, run backtests, and produce structured reports.

| AI-Native Research Workflow                 | Run the quant research loop from Codex, Claude, Cursor, CodeBuddy, the WorkBuddy China edition, or Kimi Code: factor research, backtesting, analysis, strategy creation, and simulated Paper Trading.             |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Institutional Quant Infrastructure          | Quandora provides end-to-end infrastructure for your agent: task cards, supported data, evaluation rails, and backtesting, while your agent focuses on writing Python factor logic. |
| Real Performance Evidence with Explanations | Get structured Factor and Strategy Reports with verdicts, metrics, risks, assumptions, and plain-English explanations.                                                              |
| Closed-Loop Learning                        | Agent-curated memory tracks iterations, failures, accepted factors, duplicates, and improvements to build a reusable factor library over time.                                      |
| AI Mentor                                   | Learn while you build through educational links, step-by-step workflow explanations, and clear reasoning behind each action.                                                        |

<br>

### How It Works

```
Factor Mining -> Factor Analysis -> Strategy Building -> Strategy Analysis -> simulated Paper Trading
      ^                |                    ^                    |
      +----------------+                    +--------------------+
       user-approved                         user-approved
       factor experiment                     strategy experiment
```

Analysis remains read-only. A factor experiment returns to Factor Mining, a composition or
configuration experiment returns to Strategy Building, and Paper Trading starts only after a
separate explicit user confirmation.

<br>

### Skills

| Skill | What it does |
| --- | --- |
| **Factor Mining** | Creates contract-compliant factor source, runs server-side validation and backtests, and retrieves one verified Result Bundle ZIP. |
| **Factor Analysis** | Diagnoses an exact factor result from owner-scoped server Factor Cards, Health and rating evidence, chart data, and inert job-linked source. |
| **Strategy Building** | Lists eligible factors, composes cross-sectional strategies, submits runs, and retrieves verified Strategy Result Bundle ZIPs. |
| **Strategy Analysis** | Pairs the canonical Strategy snapshot with retained artifacts and bounded six-chart data to diagnose performance and propose controlled experiments. |
| **Paper Trading** | Prepares or selects eligible sources and starts, monitors, inspects, or stops simulated Paper runs after explicit confirmation. |

<br>

Quandora Plugins is the public marketplace for Quandora agent integrations. The current package is:

```
quandora@quandora
```

The Quandora plugin includes all five skills above through one authenticated Remote MCP connection. Analysis uses server-persisted evidence and never requires a local ZIP, Python runtime, notebook, or archive-inspection script. Factor and Strategy exports are verified FM-owned ZIP files; Paper Trading is simulated and never places live-money trades.

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

The plugin ships fixed-purpose OAuth launchers for Claude Desktop Code under `plugins/quandora/scripts/`. The macOS launcher uses the operating system's `/usr/bin/script` PTY, and the Windows launcher uses Windows PowerShell 5.1 to open a native console. Both invoke only the official `claude mcp login plugin:quandora:quandora` flow, suppress OAuth output logging, and leave browser sign-in, MFA, and consent to the user.

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

The guide downloads one hash-pinned, repo-owned macOS bootstrap. That bootstrap discovers the signed local WorkBuddy China application and active config, downloads and verifies the reviewed installer components from this public repository, and runs them with WorkBuddy's bundled runtime. The installer closes CLI stdin, bounds every plugin-manager call, installs and verifies the managed package, writes only Quandora's account-scoped encrypted OAuth slot, and verifies the protected `fm_status` tool. It does not require a fixed application path, config path, WorkBuddy/CLI/plugin version, standalone runtime, custom MCP server, or pasted credential.

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

### Use Factor Mining

Use the skill command when available:

```
/quandora:factor-mining show public tasks
```

You can also ask naturally:

```
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

When the host supports local files, the verified FM-owned archive is saved under the current user's home directory with a local name derived from the user-facing factor name:

```
Quandora result/factor/<factor_slug>.zip
```

The verified ZIP is the canonical local output and is not automatically extracted, deleted, or rebuilt. Its runtime manifest is authoritative for the exact included, pending, and omitted items, including readable partial bundles.

### Use Factor Analysis

```text
/quandora:factor-analysis analyze my latest factor result
```

Factor Analysis resolves one exact run and reads its owner-scoped server Factor Card, Health and rating gates, bounded chart data, and inert job-linked source when needed. It is read-only and requires no local ZIP or Python runtime.

### Use Strategy Building

Use the skill command when available:

```text
/quandora:strategy-building list available factors
/quandora:strategy-building help me build a strategy
```

You can also ask naturally:

```text
Use Quandora Strategy Building to list eligible factors.
Use Quandora Strategy Building to compare selected factors before submission.
Use Quandora Strategy Building to combine eligible factors and show the effective configuration before submitting.
Use Quandora Strategy Building to resume a run and archive its results.
```

When a completed Strategy Result Bundle is saved locally, its path is derived from the current user-facing submitted Strategy name:

```text
Quandora result/strategy/<strategy_slug>.zip
```

The verified FM-owned Strategy ZIP is retained without automatic extraction or reconstruction.

### Use Strategy Analysis

```text
/quandora:strategy-analysis analyze my latest strategy result
```

Strategy Analysis selects one exact run, pairs the canonical Product Backend snapshot with retained artifacts, reads bounded six-chart numerical data, and proposes controlled experiments. It is read-only, requires no local ZIP or Python runtime, and treats Paper readiness as advisory.

### Use Paper Trading

```text
/quandora:paper-trading start a paper run
/quandora:paper-trading show my current Paper PnL
```

Paper Trading can prepare or select an eligible owner-scoped source, run its source backtest, and start a single-strategy or static independent-sleeve Strategy Portfolio Paper run. The skill asks for explicit confirmation before submit or terminal stop, monitors lifecycle through Paper detail, and can read current PnL, closed position history, fills, funding, equity curves, and bounded strategy code. It does not place live-money trades or automatically stop, restart, or modify another workflow.

### License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).

### Strategy evidence access

Oversized trade artifacts can be offered through the existing `sb_file_ticket`
download instead of retrying an inline read. A download link is not evidence that
the Agent has analyzed the file. Official Factor performance uses the additive
`fm_official_read` tool when available, preserving source restrictions and the
identity of the returned evidence. Deploy PB support, then Auth, before publishing
this plugin update. Existing owner-scoped reads remain unchanged.
