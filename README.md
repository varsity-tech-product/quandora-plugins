# Quandora Plugins

## Jerald


## Fangyi

Quandora Plugins is the public marketplace for Quandora agent integrations. The current package is:

```text
quandora@quandora
```

Quandora Factor Mining lets local agents create `plugin.py`, submit it through the authenticated Quandora connection, run a backtest, retrieve available factor cards and chart artifacts, and save the run files in the local workspace.

## Install

### Codex

Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: leave blank
Plugin: quandora@quandora
```

You can also ask Codex Desktop to install and connect Quandora for you:

```text
Install Quandora from varsity-tech-product/quandora-plugins, then connect Quandora Factor Mining.
```

Codex may ask before running the Codex CLI setup commands. These commands install the Quandora plugin into Codex, write Codex plugin/MCP configuration, and open Quandora OAuth. They do not grant Quandora access to your local files.

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins
codex plugin add quandora@quandora
```

Authorize when prompted. If Codex does not open the authorization flow automatically, use:

```bash
codex mcp login quandora
```

After installation or authorization, open a new chat. If Codex Desktop still does not expose Quandora tools, fully quit and reopen Codex Desktop.

### Claude

Claude Code:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin install quandora@quandora
```

Claude Desktop requires both the Quandora plugin and the Quandora connector. After installing the plugin, manually add and connect the Connector in Claude Desktop:

```text
Name: quandora
URL: https://mcp-staging.varsity.lol/factor-mining
```

Use Settings -> Connectors, add the Connector above, click Connect, authorize Quandora in the browser, then start a new chat.

In Claude Code, open `/mcp` and authenticate `quandora`, then start a new chat.

Claude Desktop can use the connected Quandora tools in chat, but local result-folder archiving is only guaranteed in local agent environments such as Claude Code, Codex, and OpenClaw. Claude Desktop's built-in file creation uses Claude's sandbox and may provide downloadable files rather than writing directly to a chosen local folder.

### OpenClaw

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/HEAD/install-openclaw.sh | bash
```

Authorize Quandora:

```bash
openclaw mcp login quandora
```

Open the printed URL, approve access, then run the code command printed by OpenClaw:

```bash
openclaw mcp login quandora --code <code>
```

Start a new OpenClaw chat after installation or authorization.

## Use Factor Mining

Use the skill command when available:

```text
/factor-mining show public tasks
```

You can also ask naturally:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

When the host supports local files, each run is saved under:

```text
results/factor-mining/<factor_name>/
```

The run folder contains the submitted `plugin.py`, a redacted `run_summary.json`, a `factor_card.json` when available, and a `factor_mining_artifacts/` folder for safe artifacts returned by Quandora, including PNG charts when chart images are available. The agent prints the result folder path at the end of each run.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
