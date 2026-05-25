# Factor Mining OpenClaw Plugin

OpenClaw plugin for the Factor Mining external-agent workflow.

This adapter includes a native `openclaw.plugin.json` manifest, a Factor Mining
skill under `skills/factor-mining/SKILL.md`, and packaged Python helper scripts
under `scripts/`.

OpenClaw uses this plugin to configure Factor Mining access, create or reuse a
task-backed session, write or receive `plugin.py`, inspect metadata without
executing generated code, upload the plugin, submit a backtest, wait for
terminal results, retrieve the default factor card, and summarize the outcome.

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

OpenClaw normally runs these helpers for the user:

```bash
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

## Validation Status

The manifest follows the native OpenClaw plugin shape provided for this adapter
work. Official OpenClaw tooling was not available in this repository, so this
branch validates the manifest as JSON and validates the packaged Python helpers
with the repository test and compile checks.
