# Factor Mining Agent Plugins

Product repository for local agent plugins that connect Codex to Factor Mining.

The included Codex plugin lets an agent create or locate `plugin.py`, validate
metadata without executing generated code, upload the plugin to Factor Mining,
submit a backtest, wait for results, retrieve the default factor card, and
summarize the outcome for the user.

## Repository Layout

- `.agents/plugins/marketplace.json` publishes the local plugin entry.
- `codex/plugins/factor-mining/.codex-plugin/plugin.json` is the Codex plugin manifest.
- `codex/plugins/factor-mining/scripts/` contains the setup and workflow helpers.
- `codex/plugins/factor-mining/skills/factor-mining/SKILL.md` defines Codex behavior.
- `codex/plugins/factor-mining/tests/` covers local state, security, and API request construction.

## User Flow

1. Install the Factor Mining Codex plugin from this repository.
2. Provide a Factor Mining Agent API Key through secure setup.
3. Let Codex create or reuse a task-backed session.
4. Let Codex create or locate `plugin.py`.
5. Let Codex run the waitable upload and backtest command.
6. Review the summarized result, including job status, failures, metrics, and artifacts.

Setup always verifies `/health` and `/agent/status`. The configured Factor
Mining API environment must expose the external-agent status endpoint and return
`key_purpose: external_agent`; otherwise setup fails before storing
configuration.

## Validation

Run these checks from the repository root:

```bash
python3 -m unittest discover -s codex/plugins/factor-mining/tests -v
python3 -m compileall -q codex/plugins/factor-mining/scripts codex/plugins/factor-mining/tests
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool codex/plugins/factor-mining/.codex-plugin/plugin.json >/dev/null
```

For the official Codex plugin validator, create a temporary virtual environment,
install `requirements-dev.txt`, and run the validator from your Codex
installation against `codex/plugins/factor-mining`.
