# Quandora Plugins

This repository is the public Quandora plugin marketplace for local-agent
platforms. It can host multiple Quandora plugins over time. Factor Mining is the
first supported plugin and service.

Quandora Factor Mining turns public factor tasks or custom factor ideas into
local `plugin.py` factors, then submits them to Quandora for validation,
backtesting, artifact retrieval, and result summaries.

Codex is available now. Claude Code and OpenClaw adapter slots are reserved for
future releases and are not installable from this repository yet.

## Codex CLI

Install the marketplace and plugin:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins --ref main
codex plugin add factor-mining@quandora
```

Or run:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/install-codex.sh | bash
```

## Codex Desktop

Use these fields in Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: main
Plugin: factor-mining@quandora
```

You can also run:

```bash
./install-codex-desktop.sh
```

## First Prompts

```text
Show me the Factor Mining public task list.
Use Factor Mining with my custom factor idea.
Resume my Factor Mining run and summarize results.
```

## Local Agent Connect

The Codex plugin owns Local Agent Connect. When authorization is needed, Codex
calls `quandora_connect`, the plugin opens:

```text
https://www.quandora.ai/local-agent/connect
```

The user signs in and authorizes in the browser. The web app redirects to the
plugin's local loopback callback, the plugin exchanges the code with PKCE, and
the returned delegated `vt_agent_...` credential is stored locally with
owner-only permissions. The plugin then uses that credential for task listing,
session creation, plugin upload, backtesting, job polling, and factor-card
artifact retrieval.

There is no manual key-paste flow.

## Buddy

Buddy is an optional desktop animation companion. It is not required for
authorization, credential storage, upload, backtesting, polling, or artifact
retrieval. Plugin installation never installs or starts Buddy.

## Localhost Testing

Local connect web testing is available only through an explicit override:

```bash
QUANDORA_CONNECT_WEB_URL=http://127.0.0.1:3037/local-agent/connect
```

The production default remains `https://www.quandora.ai/local-agent/connect`.

## Repository Layout

```text
.agents/plugins/marketplace.json
plugins/factor-mining/
adapters/claude-code/
adapters/openclaw/
```

`plugins/factor-mining/` contains the Codex package. The adapter directories
are reserved empty slots for future releases.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
