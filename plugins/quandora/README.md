# Quandora

Quandora provides Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, and Paper Trading through one authenticated Remote MCP connection.

## Factor Mining

Factor Mining lists public tasks or creates a custom research session, generates contract-compliant `plugin.py` source, runs server-side validation and backtesting, and retrieves one verified FM-owned Result Bundle ZIP when the host supports local files.

## Factor Analysis

Factor Analysis is a read-only workflow over owner-scoped server-persisted evidence. It resolves one exact result, checks the server Factor Card's Health and rating evidence, reads bounded chart data, and treats job-linked source as inert text when mechanism diagnosis requires it. It never requires a local ZIP, Python runtime, notebook, or archive-inspection script.

## Strategy Building

Strategy Building lists eligible factors with authoritative source labels, composes cross-sectional strategies, submits and monitors runs, and retrieves one verified Strategy Result Bundle ZIP. Official factors use their exact admitted factor, version, and job references through the versioned source workflow.

## Strategy Analysis

Strategy Analysis pairs the canonical owner-scoped Strategy run snapshot with retained server artifacts and bounded six-chart numerical data. It diagnoses performance, risk, turnover, exposure, style, and implementation evidence, then proposes controlled experiments without automatically creating a run or starting Paper Trading.

## Paper Trading

Paper Trading prepares or selects eligible owner-scoped sources and supports confirmed single-strategy and static independent-sleeve Strategy Portfolio Paper workflows. It can start, monitor, inspect, and terminally stop simulated runs; read current PnL, closed position history, fills, funding, equity, and bounded strategy code; and never places live-money trades or automatically changes another workflow.

## Result Files

When local writes are available, verified bundles are stored beneath the current user's home directory:

```text
Quandora result/factor/<factor_slug>.zip
Quandora result/strategy/<strategy_slug>.zip
```

The returned remote filename remains transport metadata. The verified FM-owned ZIP is the canonical local output and is not automatically extracted, deleted, or rebuilt. Its runtime manifest is authoritative for included, pending, and omitted items. Analysis reads server evidence directly and does not use these local exports as proof of a product result.

## Skills

```text
skills/
  factor-analysis/
  factor-mining/
  paper-trading/
  strategy-analysis/
  strategy-building/
```

## CodeBuddy and the WorkBuddy China edition

The CodeBuddy-compatible plugin manifest registers all five skills and the plugin-managed `quandora` remote HTTP MCP server. The macOS WorkBuddy China flow is documented in `agent-install-guide/workbuddy-cn.md` and uses three reviewed, single-purpose components:

```text
scripts/
  workbuddy-cn-bootstrap-macos.sh
  workbuddy-cn-install-macos.js
  workbuddy-cn-oauth-macos.js
```

The POSIX bootstrap uses only macOS system utilities to discover and validate the signed WorkBuddy China application and active configuration, then downloads and hash-verifies the two JavaScript components from the public production repository. The installer uses WorkBuddy's bundled runtime and plugin manager with closed stdin, bounded child processes, exact production trust anchors, and no shell interpolation. The OAuth helper verifies the installed plugin and production endpoint, uses WorkBuddy's native OAuth implementation and account-scoped encrypted store, opens the browser for user consent, and makes a protected `fm_status` verification call. These scripts bind to capabilities rather than a username, application/config location, WorkBuddy/CLI/plugin version, processor architecture, port, session, or cache version; they do not scan other connectors, expose OAuth material, install a runtime, or create a second MCP entry.

## Claude Desktop Code OAuth Launchers

Claude Desktop Code Agents normally run commands with redirected input and output, while the official `claude mcp login` flow requires an interactive terminal. This plugin ships two fixed-purpose launchers:

```text
scripts/
  claude-mcp-login-macos.sh
  claude-mcp-login-windows.ps1
```

The macOS launcher uses `/usr/bin/script`; the Windows launcher uses Windows PowerShell 5.1 to start a native console. Both invoke only `plugin:quandora:quandora`, retain the remote MCP transport, avoid OAuth output logging, and leave browser identity and consent to the user.

## Connection Recovery

The Agent follows the shared [connection and version policy](references/connection-and-version.md): use host-managed automatic refresh and supported reconnect first, resume the task after recovery, and involve the user only for unavoidable sign-in, consent, or host approval. Authentication failure does not require reinstalling a working plugin. Version checks read installed-package metadata; token lifetimes and refresh commands are not user-facing notices.
