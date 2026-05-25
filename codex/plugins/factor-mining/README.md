# Factor Mining Codex Plugin

Codex plugin for the Factor Mining external-agent workflow.

Codex uses this plugin to create or locate `plugin.py`, inspect metadata without
executing generated code, upload the plugin to Factor Mining, submit a backtest,
wait for terminal workflow and job state, retrieve the default factor card, and
summarize the result.

## Codex CLI Install

Install from the repository root:

```bash
./install-codex.sh
```

The installer configures the Factor Mining marketplace, installs the Codex
plugin, asks for the Factor Mining Agent API Key in the terminal with hidden
input, validates setup, and starts a Codex session with the Factor Mining
workflow prompt. The key is not pasted into chat, not passed as a command
argument, and not written to shell history.

Manual install uses three Codex CLI commands:

```bash
codex plugin marketplace add varsity-tech-product/factor-mining-agent-plugins --ref main
codex plugin add factor-mining@factor-mining-marketplace
PLUGIN_ROOT="$(codex plugin list --marketplace factor-mining-marketplace | awk '$1 == "factor-mining@factor-mining-marketplace" { print $NF; exit }')" && python3 "$PLUGIN_ROOT/scripts/factor_setup.py" && codex "Use the Factor Mining plugin. Verify Factor Mining status, then choose an open task, write a valid plugin.py, upload it, wait for the backtest, fetch the default factor card if available, and summarize the result."
```

## Setup

Run setup from the plugin directory:

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

Setup uses this Factor Mining API URL by default:

```text
https://d25q1jf66e8y4g.cloudfront.net
```

Use `--base-url` only for a staging or private Factor Mining API environment.
The configured environment must expose `/agent/status`; the plugin deliberately
rejects credentials that the endpoint does not accept as delegated Agent API
Keys.

Local configuration is stored at:

```text
~/.factor-mining-agent/config.json
```

Run state is stored at:

```text
~/.factor-mining-agent/runs/<client_run_id>.json
```

## Agent Workflow

Codex normally runs these helpers for the user:

```bash
python3 scripts/factor_status.py
python3 scripts/factor_api.py tasks --limit 20 --status open
python3 scripts/factor_api.py create-session --task-id <task_id> --client-run-id <client_run_id>
python3 scripts/factor_api.py create-session --idea "<research idea>" --task-payload-file task_payload.json --client-run-id <client_run_id>
python3 scripts/factor_api.py metadata --plugin-path plugin.py
python3 scripts/factor_upload_backtest.py --session-id <session_id> --plugin-path plugin.py --client-run-id <client_run_id> --position-mode both --fwd-period 7 --wait
python3 scripts/factor_api.py resume --client-run-id <client_run_id> --wait
```

Worker sessions can use a published `task_id`. Custom sessions must include a
direct `task_payload` so external-agent uploads are task-backed. The payload must
include `task_id`, `title`, `category`, `description`, non-empty `allowed_data`,
and `fwd_period`. Include any useful hints, research fields, or mechanism notes
that help Codex generate the factor.

The upload helper default is `fwd_period=7`. The wait command returns compact
JSON containing `ok`, `status`, `terminal_status`, `client_run_id`,
`session_id`, `plugin_id`, `job_ids`, workflow status, terminal jobs, artifact
availability, and summary fields suitable for Codex to report.

## Security

- Use only a Factor Mining delegated Agent API Key.
- Do not use frontend user keys, OpenAI API keys, Codex auth files, or BYOK
  credentials with this plugin.
- Setup always calls `/health` and `/agent/status`.
- Setup succeeds only when `/health` is healthy and `/agent/status` accepts the
  delegated Agent API Key. The current success response is `status: ok` and
  `agent_key: valid`.
- A `403` response from `/agent/status` means the key is not an external-agent
  credential.
- API keys are redacted from output and errors.
- Upload requests omit optional `submitter_label` and `agent_id` fields so the
  backend applies external-agent provenance from the API key.
- `plugin.py` metadata is parsed with `ast` and `ast.literal_eval`; generated
  code is never imported or executed by the helper scripts.
- Generated `plugin.py` source is uploaded as multipart request content but is
  not written to logs or run summaries.
- Artifact `404` and `410` responses are reported as unavailable. Authentication,
  authorization, network, malformed response, and server errors fail clearly.

## Validation

Run from the repository root:

```bash
python3 -m unittest discover -s codex/plugins/factor-mining/tests -v
python3 -m compileall -q codex/plugins/factor-mining/scripts codex/plugins/factor-mining/tests
python3 -m compileall -q claude-code/scripts openclaw/scripts
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool codex/plugins/factor-mining/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool claude-code/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool openclaw/openclaw.plugin.json >/dev/null
bash -n install-codex.sh
python3 codex/plugins/factor-mining/tests/acceptance/run_mock_acceptance.py
```

For official plugin validation, use a temporary virtual environment with
`requirements-dev.txt` and run your Codex plugin validator against
`codex/plugins/factor-mining`.
