# Quandora Plugins

Quandora Plugins is the public marketplace for Quandora agent integrations.
Version 0.4.8 ships one all-in-one plugin package for staging Remote MCP testing:

```text
quandora@quandora
```

Factor Mining is the first bundled skill. It uses Quandora Remote MCP over
HTTP/OAuth for public task listing, custom factor sessions, inline
`plugin_source` submission, backtesting, artifact retrieval, and result
summaries.

The Remote MCP server is named:

```text
quandora-mcp
```

The current Quandora Remote MCP endpoint is:

```text
https://mcp-staging.varsity.lol/factor-mining
```

## Codex

### Install

Use these fields in Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: v0.4.8
Plugin: quandora@quandora
```

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.8
codex plugin add quandora@quandora
```

### Authorize

Codex Desktop can open the Quandora OAuth page during first use.

Codex CLI uses:

```bash
codex mcp login quandora-mcp
```

### Use

Use the skill command when available:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## Claude Code

### Install

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins@v0.4.8
claude plugin install quandora@quandora
```

### Authorize

Open `/mcp` in Claude Code and authenticate `quandora-mcp`.

### Use

Use the skill command when available:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## OpenClaw

### Install

Install and verify the plugin bundle and Remote MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.8/install-openclaw.sh | bash
```

If the installer reports `Excluded by agent allowlist`, allow the skill and
verify again:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.8/install-openclaw.sh | bash -s -- --allow-skill
```

### Authorize

Run:

```bash
openclaw mcp login quandora-mcp
```

Open the printed URL, approve access, then run the code command printed by
OpenClaw:

```bash
openclaw mcp login quandora-mcp --code <code>
```

Verify the authorized MCP connection:

```bash
openclaw mcp doctor quandora-mcp --probe
```

### Use

Start OpenClaw:

```bash
openclaw chat
```

Then run:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
