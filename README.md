# Quandora Plugins

Quandora Plugins is the public marketplace for Quandora agent integrations.
Version 0.4.1 ships one all-in-one plugin package:

```text
quandora@quandora
```

Factor Mining is the first bundled skill. It uses Quandora Remote MCP over
HTTP/OAuth for public task listing, custom factor sessions, inline
`plugin_source` submission, backtesting, artifact retrieval, and result
summaries.

## Codex Desktop

Use these fields in Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: v0.4.1
Plugin: quandora@quandora
```

Codex Desktop can launch the Quandora OAuth page during first use. After the
browser authorization finishes, return to Codex Desktop and start a new chat:

```text
Use Quandora Factor Mining to show public tasks.
```

## Codex CLI and TUI

Install the plugin, then authenticate the Remote MCP server from the shell:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.1
codex plugin add quandora@quandora
codex mcp login quandora-factor-mining
codex
```

Inside the Codex TUI, run:

```text
Use Quandora Factor Mining to show public tasks.
```

Run `codex mcp login quandora-factor-mining` before expecting the Remote MCP
tools to be available in a TUI session.

## Claude Desktop

Install the Quandora plugin in Claude Desktop, then connect the required
Quandora connector:

```text
Settings -> Connectors -> Quandora -> Connect
```

The connector URL is:

```text
https://mcp.quandora.ai/factor-mining
```

Claude Desktop may route through a Claude sign-in page before opening the
Quandora OAuth authorization page. After connecting, enable the Quandora
connector for the current chat from the `+` menu, then use:

```text
Use Quandora Factor Mining to show public tasks.
```

The Claude Desktop chat flow does not require a local workspace. Claude can
draft the factor source in the conversation and submit it as inline
`plugin_source` through the connected Remote MCP tools.

## Claude Code

Install the plugin:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins@v0.4.1
claude plugin install quandora@quandora
```

Then start Claude Code and authenticate the Remote MCP server from `/mcp`:

```text
/mcp
```

Select `quandora-factor-mining`, choose Authenticate/Login, complete the
browser authorization, and then use the `factor-mining` skill in the local
coding session.

## OpenClaw

Use the installer so OpenClaw installs the plugin bundle and registers the
Factor Mining Remote MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.1/install-openclaw.sh | bash
```

Manual install requires both steps:

```bash
openclaw plugins install quandora --marketplace https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.1 --force
openclaw mcp add quandora-factor-mining --transport streamable-http --url https://mcp.quandora.ai/factor-mining --auth oauth --no-probe
```

If `openclaw mcp add` does not support `--no-probe` or fails, use
`install-openclaw.sh`; the script includes a Remote MCP registration fallback.

## First Prompts

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## Authorization

The Factor Mining Remote MCP server is named `quandora-factor-mining` and uses:

```text
https://mcp.quandora.ai/factor-mining
```

Authorization is handled by the agent platform's Remote MCP OAuth flow:

- Codex Desktop can open the Quandora OAuth page during first use.
- Codex CLI/TUI requires `codex mcp login quandora-factor-mining`.
- Claude Desktop requires connecting and enabling the Quandora connector.
- Claude Code requires authenticating `quandora-factor-mining` from `/mcp`.
- OpenClaw requires the registered Remote MCP server to be authenticated from
  OpenClaw's MCP UI or first-use auth flow.

The plugin never asks users to paste Quandora credentials into chat.

## Repository Layout

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/quandora/
tools/validate-quandora-product-package.py
```

Future Quandora services can be added as sibling skills under
`plugins/quandora/skills/`.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
