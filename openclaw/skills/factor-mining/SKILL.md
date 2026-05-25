---
name: factor-mining
description: Use when OpenClaw needs to create, validate, upload, backtest, poll, summarize, or resume a Factor Mining plugin.py run through the packaged helper scripts.
---

# Factor Mining OpenClaw Skill

Use this skill for Factor Mining external-agent work in OpenClaw. Run the
packaged Python helpers from the OpenClaw plugin root. Do not duplicate the API
client or call Factor Mining endpoints directly.

## Setup

Run setup from the OpenClaw plugin root when local configuration is missing or
invalid:

```bash
python3 scripts/factor_setup.py
```

The setup helper uses a non-echo prompt by default. Never ask the user to paste
the Factor Mining Agent API Key into chat. In automation, use one of these
secure inputs when appropriate:

```bash
python3 scripts/factor_setup.py --api-key-stdin
FACTOR_MINING_AGENT_API_KEY=<agent-key> python3 scripts/factor_setup.py
```

Setup calls `/health` and `/agent/status`. Continue only when `/health` is
healthy and `/agent/status` accepts the delegated Agent API Key. The current
success response is `status: ok` and `agent_key: valid`. If `/agent/status`
returns `403`, tell the user the key is not an external-agent credential. Do
not bypass this check.

## Workflow

1. Verify setup:

```bash
python3 scripts/factor_status.py
```

2. List available tasks for worker-mode sessions:

```bash
python3 scripts/factor_api.py tasks --limit 20 --status open
```

3. Create a task-backed session.

For a published task:

```bash
python3 scripts/factor_api.py create-session --task-id <task_id> --client-run-id <client_run_id>
```

For a custom or free-form idea, write a direct `task_payload` JSON file first.
It must include `task_id`, `title`, `category`, `description`, non-empty
`allowed_data`, and `fwd_period`.

```bash
python3 scripts/factor_api.py create-session --idea "<research idea>" --task-payload-file task_payload.json --client-run-id <client_run_id>
```

4. Request deduplication context when a draft description and formula exist:

```bash
python3 scripts/factor_api.py dedup-context --session-id <session_id> --description "<draft description>" --formula "<draft formula>"
```

5. Inspect `plugin.py` metadata without executing generated code:

```bash
python3 scripts/factor_api.py metadata --plugin-path plugin.py
```

6. Upload and wait using the packaged helper:

```bash
python3 scripts/factor_upload_backtest.py --session-id <session_id> --plugin-path plugin.py --client-run-id <client_run_id> --position-mode both --fwd-period 7 --wait
```

7. Resume interrupted runs with the persisted client run id:

```bash
python3 scripts/factor_api.py resume --client-run-id <client_run_id> --wait
```

## Reporting

Summarize the returned JSON. Always inspect `ok`, `status`,
`terminal_status`, `failures`, terminal jobs, artifact availability, and factor
card metrics. If `ok` is false, report the terminal failure instead of
presenting the backtest as successful.
