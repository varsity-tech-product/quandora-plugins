# Connection and Security

Load this reference only when Quandora tools are unavailable, authentication is terminally
failed, or a host-specific reconnect is required.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask for API keys,
bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or pasted
credentials. Token expiry alone is not a reason to start another authorization flow while the host
is refreshing.

Use the host-native recovery path:

- Codex CLI/TUI: `codex mcp login quandora`, complete browser authorization, then check for
  the required canonical action.
- Codex Desktop: authorize the plugin-provided Quandora connector. Start a new chat after
  authorization; fully quit and reopen Desktop only if the tools remain unavailable.
- Kimi Code: `/mcp-config login plugin-quandora:quandora`, then start a new chat and
  check `/mcp`.
- Claude Code: open `/mcp`, authenticate `quandora`, then start a new chat.
- Claude Desktop: add a Connector named `quandora` with
  `https://mcp.quandora.ai/quant`, authorize it, then start a new chat.
- CodeBuddy/WorkBuddy: update or reinstall the plugin, reconnect its managed Remote MCP server,
  finish browser authorization, then start a new chat.

Do not use raw HTTP, local helper scripts, internal service endpoints, local execution keys, or a
credential-paste flow. The only direct HTTP exception is immediate consumption of an unmodified,
short-lived Result Bundle URL returned by the canonical bundle-ticket action. Never construct,
persist, log, reuse, or summarize that URL.
