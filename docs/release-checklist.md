# Quandora Plugin Release Checklist

## v0.4.0

- Confirm the product branch contains one plugin package at `plugins/quandora`.
- Confirm Factor Mining is the only v0.4.0 skill at
  `plugins/quandora/skills/factor-mining`.
- Confirm root Codex and Claude Code marketplaces are named `quandora` and list
  only `quandora` from `./plugins/quandora`.
- Confirm plugin manifests are version `0.4.0` and point to
  `https://github.com/varsity-tech-product/quandora-plugins`.
- Confirm the Factor Mining Remote MCP server is named
  `quandora-factor-mining` and points to
  `https://mcp.quandora.ai/factor-mining`.
- Confirm stable install docs pin to `v0.4.0`.
- Confirm user-facing install docs do not require a separate auth command.
- Confirm Codex CLI, Claude Code, and OpenClaw install validation passes.
- Confirm OpenClaw registration uses Remote MCP HTTP/OAuth.
- Confirm the Factor Mining skill uses the verified single-run Remote MCP tool
  names and does not include batch mining in v0.4.0.
- Confirm the product pollution scan has no user-facing setup leaks.
- Confirm `git diff --check` passes.

After review, create the release tag:

```bash
git tag -a v0.4.0 -m "Quandora plugin v0.4.0"
git push origin v0.4.0
```
