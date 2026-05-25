# Factor Mining Agent Plugins

Product repository for local agent plugins that connect agent coding tools to
Factor Mining.

The included adapters let an agent create or locate `plugin.py`, validate
metadata without executing generated code, upload the plugin to Factor Mining,
submit a backtest, wait for results, retrieve the default factor card, and
summarize the outcome for the user.

## Adapter Status

- Codex: supported with a native Codex plugin manifest and skill.
- Claude Code: adapter-ready with a native Claude Code plugin manifest, skill,
  and packaged helper scripts.
- OpenClaw: adapter-ready with a native OpenClaw plugin manifest, skill, and
  packaged helper scripts. Official OpenClaw tool validation is not included in
  this repository.

## Repository Layout

- `.agents/plugins/marketplace.json` publishes the local plugin entry.
- `codex/plugins/factor-mining/.codex-plugin/plugin.json` is the Codex plugin manifest.
- `codex/plugins/factor-mining/scripts/` contains the setup and workflow helpers.
- `codex/plugins/factor-mining/skills/factor-mining/SKILL.md` defines Codex behavior.
- `codex/plugins/factor-mining/tests/` covers local state, security, and API request construction.
- `codex/plugins/factor-mining/tests/acceptance/` runs the mock backend acceptance flow.
- `claude-code/` contains the Claude Code plugin package.
- `openclaw/` contains the OpenClaw plugin package.

## User Flow

1. Install the Factor Mining adapter for the target agent.
2. Provide a Factor Mining Agent API Key through secure setup.
3. Let the agent create or reuse a task-backed session.
4. Let the agent create or locate `plugin.py`.
5. Let the agent run the waitable upload and backtest command.
6. Review the summarized result, including job status, failures, metrics, and artifacts.

Setup always verifies `/health` and `/agent/status`. Setup succeeds only when
the API is healthy and `/agent/status` accepts the delegated Factor Mining Agent
API Key. The current success response is `status: ok` and `agent_key: valid`;
a `403` response means the key is not an external-agent credential.

## Validation

Run these checks from the repository root:

```bash
python3 -m unittest discover -s codex/plugins/factor-mining/tests -v
python3 -m compileall -q codex/plugins/factor-mining/scripts codex/plugins/factor-mining/tests
python3 -m compileall -q claude-code/scripts openclaw/scripts
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool codex/plugins/factor-mining/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool claude-code/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool openclaw/openclaw.plugin.json >/dev/null
python3 codex/plugins/factor-mining/tests/acceptance/run_mock_acceptance.py
```

For the official Codex plugin validator, create a temporary virtual environment,
install `requirements-dev.txt`, and run the validator from your Codex
installation against `codex/plugins/factor-mining`.
