# Quandora Plugins

Quandora Plugins is the public marketplace for Quandora agent integrations.
Version 0.4.3 ships one all-in-one plugin package:

```text
quandora@quandora
```

Factor Mining is the first bundled skill. It uses Quandora Remote MCP over
HTTP/OAuth for public task listing, custom factor sessions, inline
`plugin_source` submission, backtesting, artifact retrieval, and result
summaries.

The Remote MCP server is named:

```text
quandora-mcp
```

## Install

### Codex Desktop

Use these fields in Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: v0.4.3
Plugin: quandora@quandora
```

### Codex CLI

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.3
codex plugin add quandora@quandora
```

### Claude Desktop

Install the Quandora plugin in Claude Desktop.

### Claude Code

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins@v0.4.3
claude plugin install quandora@quandora
```

### OpenClaw

Install and verify the plugin bundle and Remote MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.3/install-openclaw.sh | bash
```

If the installer reports `Excluded by agent allowlist`, allow the skill and
verify again:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.3/install-openclaw.sh | bash -s -- --allow-skill
```

## Authorization

The current Quandora Remote MCP endpoint is:

```text
https://mcp.quandora.ai/factor-mining
```

Authorize `quandora-mcp` through the host platform:

- Codex Desktop can open the Quandora OAuth page during first use.
- Codex CLI uses `codex mcp login quandora-mcp`.
- Claude Desktop connects the Quandora connector from Settings -> Connectors.
- Claude Code authenticates `quandora-mcp` from `/mcp`.
- OpenClaw authenticates the registered MCP server from its MCP UI or first-use
  auth flow.

## Use

In OpenClaw, start chat first:

```bash
openclaw chat
```

Use the slash command when the host supports skills:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
