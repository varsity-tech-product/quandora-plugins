# Quandora Plugins

Quandora Plugins is the public marketplace for Quandora agent integrations.
Version 0.4.0 ships one all-in-one plugin package:

```text
quandora@quandora
```

Factor Mining is the first bundled skill. It uses Quandora Remote MCP over
HTTP/OAuth for public task listing, custom factor sessions, inline
`plugin_source` submission, backtesting, artifact retrieval, and result
summaries.

## Codex CLI

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.0
codex plugin add quandora@quandora
```

Or run the installer from a checkout:

```bash
./install-codex.sh
```

## Codex Desktop

Use these fields in Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: v0.4.0
Plugin: quandora@quandora
```

You can also run:

```bash
./install-codex-desktop.sh
```

## Claude Code

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins@v0.4.0
claude plugin install quandora@quandora
```

## OpenClaw

Use the installer so OpenClaw installs the plugin bundle and registers the
Factor Mining Remote MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.0/install-openclaw.sh | bash
```

Manual install requires both steps:

```bash
openclaw plugins install quandora --marketplace https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.0 --force
openclaw mcp add quandora-factor-mining --transport streamable-http --url https://mcp.quandora.ai/factor-mining --auth oauth --no-probe
```

If `openclaw mcp add` does not support `--no-probe` or fails, use
`install-openclaw.sh`; the script includes a Remote MCP registration fallback.

## First Prompts

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## Authorization

The Factor Mining Remote MCP server is named `quandora-factor-mining` and uses:

```text
https://mcp.quandora.ai/factor-mining
```

Authorization is handled by the agent platform's Remote MCP OAuth flow during
first use or from that platform's MCP UI. Plugin installation does not require
a separate auth command.

## Repository Layout

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/quandora/
tools/validate-quandora-product-package.py
```

Future Quandora services can be added as sibling skills under
`plugins/quandora/skills/`.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
