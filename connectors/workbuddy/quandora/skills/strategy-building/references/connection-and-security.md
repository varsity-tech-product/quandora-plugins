# Connection and Security

Load this reference only when a required canonical Quandora action is unavailable or the
host reports terminal authorization failure.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask for API keys,
bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or pasted
credentials. Do not reauthorize merely because an access token expired while the host is
refreshing.

Use only the host-native reconnect path:

- Codex CLI/TUI: `codex mcp login quandora`.
- Codex Desktop: authorize the plugin connector, start a new chat, and fully restart Desktop only
  if tools remain unavailable.
- Kimi Code: `/mcp-config login plugin-quandora:quandora`, then start a new chat.
- Claude Code: authenticate `quandora` from `/mcp`, then start a new chat.
- Claude Desktop: add the `quandora` Connector at
  `https://mcp.quandora.ai/quant`, authorize it, then start a new chat.
- CodeBuddy/WorkBuddy: update or reinstall the plugin, reconnect its managed MCP server, finish
  browser authorization, then start a new chat.

Do not use raw HTTP, local helper scripts, internal service paths, or credential paste. The only
direct HTTP exception is immediate consumption of the opaque short-lived URL returned by
`create_strategy_result_bundle_download`; never construct, modify, persist, reuse, or summarize it.
