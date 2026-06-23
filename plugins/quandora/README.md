# Quandora

Quandora is the all-in-one plugin package in the Quandora plugin marketplace.
Factor Mining is the first bundled skill.

## Remote MCP

The Factor Mining skill uses the `quandora-mcp` Remote MCP server:

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

Authorization is handled by the host platform's Remote MCP OAuth flow:

- Codex Desktop can open the Quandora OAuth page during first use.
- Codex CLI requires `codex mcp login quandora-mcp`.
- Claude Desktop requires connecting and enabling the required Quandora
  connector in the chat.
- Claude Code requires authenticating `quandora-mcp` from `/mcp`.
- OpenClaw uses its MCP registry and auth UI.

Claude Desktop chat can use the connected Remote MCP tools after the connector
is enabled; it does not need a local coding workspace. Local coding agents such
as Codex CLI and Claude Code may write a local `plugin.py`, but all hosts submit
the factor as inline `plugin_source`.

## Skills

```text
skills/
  factor-mining/
```
