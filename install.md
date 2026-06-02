# Install Quandora Factor Mining

## 1. Codex CLI

```bash
codex plugin marketplace add varsity-tech-product/factor-mining-agent-plugins --ref main
codex plugin add factor-mining@factor-mining-marketplace
```

Start with:

```text
Show me the Factor Mining public task list.
```

## 2. Codex Desktop

Add a marketplace with:

```text
Source: varsity-tech-product/factor-mining-agent-plugins
Git ref: main
Plugin: factor-mining@factor-mining-marketplace
```

## 3. Local Checkout Validation

From a local checkout of this repository:

```bash
codex plugin marketplace add /path/to/factor-mining-agent-plugins
codex plugin add factor-mining@factor-mining-marketplace
```

The local marketplace entry points to `./plugins/factor-mining`.

## 4. Claude Code Reserved

The `adapters/claude-code/` slot is reserved for a future release. No Claude
Code manifest or install command is published yet.

## 5. OpenClaw Reserved

The `adapters/openclaw/` slot is reserved for a future release. No OpenClaw
manifest or install command is published yet.
