# Factor Mining Claude Code Plugin

Claude Code plugin for the Factor Mining external-agent workflow.

This plugin is self-contained. It includes the Factor Mining Python helper
scripts under `scripts/`, the Claude Code plugin manifest under
`.claude-plugin/plugin.json`, and the agent skill under
`skills/factor-mining/SKILL.md`.

Claude Code uses this plugin to create or locate `plugin.py`, inspect metadata
without executing generated code, upload the plugin to Factor Mining, submit a
backtest, wait for terminal workflow and job state, retrieve the default factor
card, and summarize the result.

## Setup

Run setup from this plugin directory:

```bash
python3 scripts/factor_setup.py
```

The setup command prompts for the Factor Mining Agent API Key without echoing
the value. Do not paste the key into chat.

Automation can provide the key without a prompt:

```bash
python3 scripts/factor_setup.py --api-key-stdin
```

Environment variable input is supported for automation-only contexts:

```bash
FACTOR_MINING_AGENT_API_KEY=<agent-key> python3 scripts/factor_setup.py
```

Setup calls `/health` and `/agent/status`. Setup succeeds only when the API is
healthy and `/agent/status` accepts the delegated Factor Mining Agent API Key.
The current success response is `status: ok` and `agent_key: valid`; a `403`
response means the key is not an external-agent credential.

## Agent Workflow

Claude Code normally runs these helpers for the user:

```bash
python3 scripts/factor_setup.py
python3 scripts/factor_status.py
python3 scripts/factor_api.py tasks --limit 20 --status open
python3 scripts/factor_api.py create-session --task-id <task_id> --client-run-id <client_run_id>
python3 scripts/factor_api.py create-session --idea "<research idea>" --task-payload-file task_payload.json --client-run-id <client_run_id>
python3 scripts/factor_api.py metadata --plugin-path plugin.py
python3 scripts/factor_upload_backtest.py --session-id <session_id> --plugin-path plugin.py --client-run-id <client_run_id> --position-mode both --fwd-period 7 --wait
python3 scripts/factor_api.py resume --client-run-id <client_run_id> --wait
```

Worker sessions use a published `task_id`. Custom or free-form sessions require
a direct `task_payload` before upload. The payload must include `task_id`,
`title`, `category`, `description`, non-empty `allowed_data`, and `fwd_period`.

The upload command returns compact JSON with `ok`, `status`,
`terminal_status`, workflow state, jobs, artifact availability, and summary
fields. Report failed or cancelled terminal jobs clearly.

## Security

- Use only a delegated Factor Mining Agent API Key.
- Do not use frontend user keys, OpenAI API keys, Claude credentials, or BYOK
  credentials with this plugin.
- Setup always calls `/health` and `/agent/status`.
- Setup succeeds only when `/health` is healthy and `/agent/status` accepts the
  delegated Agent API Key. The current success response is `status: ok` and
  `agent_key: valid`.
- A `403` response from `/agent/status` means the key is not an external-agent
  credential.
- API keys are redacted from output and errors.
- `plugin.py` metadata is parsed statically; generated code is not imported or
  executed by the helper scripts.
