# Quandora

Quandora is the all-in-one plugin package in the Quandora plugin marketplace.
Factor Mining is the first bundled skill.

## Remote MCP

The Factor Mining skill uses the `quandora-factor-mining` Remote MCP server:

```text
https://mcp.quandora.ai/factor-mining
```

Internal validation may use:

```text
https://mcp-staging.varsity.lol/factor-mining
```

The plugin package includes a shared `.mcp.json` for Codex-compatible bundled
MCP loading and an HTTP MCP declaration in the Claude Code manifest. OpenClaw
registration is handled by the repository installer because OpenClaw stores
Remote MCP definitions in its own registry.

Authorization is handled by the host platform's Remote MCP OAuth flow during
first use or through the platform MCP UI.

## Skills

```text
skills/
  factor-mining/
```

Additional Quandora services can be added later as sibling skills under this
same plugin package.
