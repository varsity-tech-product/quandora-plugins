# README

<div align="center"><img src=".gitbook/assets/banner.png" alt="Quandora" width="100%"></div>

## Quandora: AI Enabler for Finance Agents

<p align="center"><a href="https://quandora.ai"><img src="https://img.shields.io/badge/Built%20by-Quandora-F28C00?style=flat" alt="Built by Quandora"></a> <a href="https://discord.com/invite/9WshZMnjGE"><img src="https://img.shields.io/badge/Join-Discord-5865F2?style=flat&#x26;logo=discord&#x26;logoColor=white" alt="Join Discord"></a> <a href="https://x.com/quandora_labs"><img src="https://img.shields.io/badge/Follow-%40quandora__labs-000000?style=flat&#x26;logo=x&#x26;logoColor=white" alt="Follow on X"></a></p>

#### Quandora is building an agentic finance infrastructure that turns generic AI agents into professional quant finance agents. Quandora gives AI agents the infrastructure to research markets, generate alphas and strategies, run backtests, and produce structured reports.

| AI-Native Research Workflow                 | Run the full quant research loop directly from CLI, Codex, Claude Code, or Cursor: autonomous research, backtesting, strategy creation, and deployment-ready workflow.              |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Institutional Quant Infrastructure          | Quandora provides end-to-end infrastructure for your agent: task cards, supported data, evaluation rails, and backtesting, while your agent focuses on writing Python factor logic. |
| Real Performance Evidence with Explanations | Get structured Factor and Strategy Reports with verdicts, metrics, risks, assumptions, and plain-English explanations.                                                              |
| Closed-Loop Learning                        | Agent-curated memory tracks iterations, failures, accepted factors, duplicates, and improvements to build a reusable factor library over time.                                      |
| AI Mentor                                   | Learn while you build through educational links, step-by-step workflow explanations, and clear reasoning behind each action.                                                        |

<br>

### How It Works

```
        +----------------------+
        | factor mining        |<----------------+
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | factor evaluation    |                 |
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | factor / strategy    |                 |
        | card                 |                 |
        +----------------------+                 |
                  |                              |
                  |                              |
                  |                              | performance decay
                  |                              | restarts mining
                  |                              |
                  v                              |
        +----------------------+                 |
        | strategy             |                 |
        | construction         |                 |
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | strategy evaluation  |                 |
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | paper trading /      |-----------------+
        | monitoring           |
        +----------------------+
                  |
                  | stable
                  |
                  v
        +----------------------+
        | supervised           |
        | deployment           |
        +----------------------+
                  |
                  v
        +----------------------+
        | optional live        |
        | trading              |
        +----------------------+
```

<br>

### Agents

Each agent is named for the workflow stage it runs.

| Agent                            | What it does                                                                                                               |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Factor Mining Agent**          | Turns an alpha-mining task into Python factor logic, checks memory for duplicates, and prepares candidates for evaluation. |
| **Factor Evaluation Agent**      | Submits factors to Quandora, tracks server-side validation and backtests, and summarizes pass/fail results.                |
| **Factor / Strategy Card Agent** | Produces structured cards with formulas, metrics, risks, assumptions, verdicts, and plain-English explanations.            |
| **Strategy Construction Agent**  | Combines accepted factors into strategy candidates with portfolio logic, sizing rules, and risk constraints.               |
| **Strategy Evaluation Agent**    | Evaluates strategy performance, drawdown, turnover, cost viability, and robustness before monitoring.                      |
| **Paper Trading Monitor Agent**  | Monitors paper performance and restarts factor mining when performance decay is detected.                                  |
| **Deployment Supervisor Agent**  | Keeps users in the loop for approvals, guardrails, deployment checks, and supervised rollout.                              |

<br>

Quandora Plugins is the public marketplace for Quandora agent integrations. The current package is:

```
quandora@quandora
```

Quandora Factor Mining lets local agents create `plugin.py`, submit it through the authenticated Quandora connection, run a backtest, retrieve available factor cards and chart artifacts, and save the run files in the local workspace.

### Install

#### Codex

Codex Desktop:

```
Source: varsity-tech-product/quandora-plugins
Git ref: leave blank
Plugin: quandora@quandora
```

You can also ask Codex Desktop to install and connect Quandora for you:

```
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

#### Claude

Claude Code:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin install quandora@quandora
```

Claude Desktop requires both the Quandora plugin and the Quandora connector. After installing the plugin, manually add and connect the Connector in Claude Desktop:

```
Name: quandora
URL: https://mcp.quandora.ai/factor-mining
```

Use Settings -> Connectors, add the Connector above, click Connect, authorize Quandora in the browser, then start a new chat.

In Claude Code, open `/mcp` and authenticate `quandora`, then start a new chat.

Claude Desktop can use the connected Quandora tools in chat, but local result-folder archiving is only guaranteed in local agent environments such as Claude Code, Codex, and OpenClaw. Claude Desktop's built-in file creation uses Claude's sandbox and may provide downloadable files rather than writing directly to a chosen local folder.

Factor Mining chart downloads use returned server `source_name` values for API calls and save local PNGs to returned `standard_local_path` values. Local filenames intentionally remove the `default_` prefix and p2/p3 suffixes.

#### OpenClaw

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

### Use Factor Mining

Use the skill command when available:

```
/factor-mining show public tasks
```

You can also ask naturally:

```
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

When the host supports local files, each run is saved under a stable folder named after the factor slug:

```
Quandora result/factor-mining/aggressive_flow_exhaustion_reversal/
```

The run folder contains the submitted `plugin.py`, a redacted `run_summary.json`, `factor_card_is.json` and `factor_card_all.json` when available, `artifact_manifest.json`, and PNG charts under `artifacts/is/` and `artifacts/all/`. The agent prints the result, artifact, and chart folder paths at the end of each run.

### License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE/).
