# Quandora Factor Mining Codex Plugin

This is the Codex package for Quandora Factor Mining. It lets Codex write local
`plugin.py` factors, validate metadata, upload factors to Quandora, run
user-scoped backtests, poll workflows and jobs, fetch factor-card artifacts,
and summarize results through bundled MCP tools.

## Product Defaults

Production Local Agent Connect opens:

```text
https://www.quandora.ai/local-agent/connect
```

Local connect web testing is available only through explicit configuration:

```bash
QUANDORA_CONNECT_WEB_URL=http://127.0.0.1:3037/local-agent/connect
```

The connect backend exchange and revoke routes are:

```text
POST /api/agent/connect/exchange
POST /api/agent/connect/revoke
```

After exchange, the plugin uses the returned `base_url` for API calls. The
production base URL returned by Quandora should be:

```text
https://www.quandora.ai/api
```

## Local Agent Connect

Codex calls `quandora_connect`. The plugin starts a local loopback callback,
opens Quandora Local Agent Connect, exchanges the returned code and state with
PKCE, stores only the returned `vt_agent_...` credential locally, and validates
it with `/agent/status` under the returned `base_url`.

Users never provide raw Agent API credentials. Buddy is optional desktop
animation only and is not part of authorization.

## MCP Tools

The bundled `quandora-factor-mining` MCP server exposes:

- `quandora_connect`
- `quandora_connect_wait`
- `quandora_connect_pending`
- `quandora_connect_cancel`
- `quandora_disconnect`
- `quandora_status`
- `quandora_list_public_tasks`
- `quandora_create_task_session`
- `quandora_create_custom_session`
- `quandora_parse_plugin_metadata`
- `quandora_request_dedup_context`
- `quandora_upload_backtest_wait`
- `quandora_resume_run`
- `quandora_get_workflow`
- `quandora_get_job`
- `quandora_get_artifact`

The plugin does not expose raw credential tools, generic API-call tools, or
animation-state tools.

## Security

- Accept only plugin-owned `vt_agent_...` Local Agent Connect credentials.
- Store credentials under the local agent home with owner-only permissions.
- Never print raw credentials; status output is redacted.
- Use `/agent/status` under the exchange-returned `base_url` for live checks.
- If a credential expires or is revoked, run `quandora_connect` again.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.

## First Prompts

```text
Show me the Factor Mining public task list.
Use Factor Mining with my custom factor idea.
Resume my Factor Mining run and summarize results.
```
