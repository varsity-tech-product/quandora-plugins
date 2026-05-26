# Factor Mining Agent Plugins

Local agent plugins that connect coding agents to Factor Mining.

The included adapters let an agent create or locate `plugin.py`, validate
metadata without executing generated code, upload the plugin to Factor Mining,
submit a backtest, wait for results, retrieve the default factor card, and
summarize the outcome for the user.

## Supported Adapters

- Codex: supported with a native Codex plugin manifest and skill.
- Claude Code: packaged with a native Claude Code plugin manifest, skill, and
  helper scripts.
- OpenClaw: packaged with a native OpenClaw manifest, skill, and helper scripts.

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
3. Start from a public task or a custom idea.
4. Let the agent create or reuse a task-backed session.
5. Let the agent create or locate `plugin.py`.
6. Let the agent run the waitable upload and backtest command.
7. Review the summarized result, including job status, failures, metrics, and artifacts.

Setup always verifies `/health` and `/agent/status`. Setup succeeds only when
the API is healthy and `/agent/status` accepts the delegated Factor Mining Agent
API Key. The current success response is `status: ok` and `agent_key: valid`;
a `403` response means the key is not an external-agent credential.

## Codex CLI Install

For Codex, the shortest product flow is to install the marketplace, install the
plugin, configure the Factor Mining Agent API Key in the terminal, and start a
Codex session with the Factor Mining workflow prompt. The key is entered at a
hidden terminal prompt before Codex starts; it is not pasted into chat, not passed
as a command argument, and not written to shell history. The setup helper stores
configuration under `~/.factor-mining-agent` with user-only file permissions.

From a clone of this repository:

```bash
./install-codex.sh
```

If distribution requires GitHub authentication, use a local clone or a
Git-authenticated clone:

```bash
tmpdir="$(mktemp -d)" && git clone --depth 1 git@github.com:varsity-tech-product/factor-mining-agent-plugins.git "$tmpdir/factor-mining-agent-plugins" && "$tmpdir/factor-mining-agent-plugins/install-codex.sh"
```

After the repository or release asset is public, direct distribution can use:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/factor-mining-agent-plugins/main/install-codex.sh | bash
```

Set `FACTOR_MINING_PLUGIN_REF` to pin a release or branch:

```bash
FACTOR_MINING_PLUGIN_REF=v0.1.0 ./install-codex.sh
```

Set `FACTOR_MINING_START_CODEX=0` or pass `--no-start` to install and configure
without starting a Codex session. Pass `--install-only` to install without
configuration. Pass `--force-setup` to replace the saved Agent API Key.

## Codex Desktop Install

Install, configure Factor Mining, and open Codex Desktop for the current
workspace:

```bash
./install-codex-desktop.sh
```

The Desktop launcher prints the Factor Mining start prompt before opening the
app. Start a new Codex Desktop chat with that prompt.

## Starting A Factor Run

After installation, use natural language in Codex. You can start from public
tasks published in Factor Mining or from a custom idea.

To inspect available public tasks:

```text
Show me the Factor Mining public task list.
```

To start from your own research idea:

```text
Use Factor Mining with this custom idea: build a short-term crypto liquidity stress factor using close and volume.
```

## Switching Agent API Keys In Codex

After the plugin is installed, a running Codex CLI or Codex Desktop session can
switch to a different Factor Mining Agent API Key without reinstalling or
restarting Codex. Ask Codex to run:

```bash
python3 scripts/factor_setup.py --browser
```

The helper opens a local browser setup page on `127.0.0.1`. Paste the new
Agent API Key into that page, not into chat. The next Factor Mining command will
use the updated key.

### Manual Codex CLI Commands

These are the three commands run by the installer:

```bash
codex plugin marketplace add varsity-tech-product/factor-mining-agent-plugins --ref main
codex plugin add factor-mining@factor-mining-marketplace
PLUGIN_ROOT="$(codex plugin list --marketplace factor-mining-marketplace | awk '$1 == "factor-mining@factor-mining-marketplace" { print $NF; exit }')" && python3 "$PLUGIN_ROOT/scripts/factor_setup.py" && codex "Use the Factor Mining plugin. Verify Factor Mining status, then show me the Factor Mining public task list. Do not create a session until I choose a public task or provide a custom idea. Then write a valid plugin.py locally, upload it, wait for the backtest, fetch the default factor card if available, and summarize the result."
```

For local product validation, replace the first command with the repository path:

```bash
codex plugin marketplace add /path/to/factor-mining-agent-plugins
```

## Quality Checks

Run these checks from the repository root:

```bash
python3 -m unittest discover -s codex/plugins/factor-mining/tests -v
python3 -m compileall -q codex/plugins/factor-mining/scripts codex/plugins/factor-mining/tests
python3 -m compileall -q claude-code/scripts openclaw/scripts
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool codex/plugins/factor-mining/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool claude-code/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool openclaw/openclaw.plugin.json >/dev/null
bash -n install-codex.sh
bash -n install-codex-desktop.sh
python3 codex/plugins/factor-mining/tests/acceptance/run_mock_acceptance.py
```

When a Codex plugin validator is available in the environment, run it against
`codex/plugins/factor-mining`.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
