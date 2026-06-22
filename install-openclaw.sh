#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="${QUANDORA_PLUGIN_NAME:-quandora}"
MARKETPLACE_URL="${QUANDORA_PLUGIN_MARKETPLACE_URL:-https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.0}"
MCP_NAME="${QUANDORA_FACTOR_MINING_MCP_NAME:-quandora-factor-mining}"
MCP_URL="${QUANDORA_FACTOR_MINING_MCP_URL:-https://mcp.quandora.ai/factor-mining}"

usage() {
  cat <<'USAGE'
Usage: install-openclaw.sh [options]

Options:
  -h, --help    Show this help.

Default install:
  openclaw plugins install quandora --marketplace https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.0 --force
  openclaw mcp add quandora-factor-mining --transport streamable-http --url https://mcp.quandora.ai/factor-mining --auth oauth --no-probe
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v openclaw >/dev/null 2>&1; then
  echo "OpenClaw CLI is required. Install or update OpenClaw, then run this script again." >&2
  exit 1
fi

echo "Installing OpenClaw plugin: ${PLUGIN_NAME}"
openclaw plugins install "${PLUGIN_NAME}" --marketplace "${MARKETPLACE_URL}" --force

echo "Registering Remote MCP server: ${MCP_NAME}"
if openclaw mcp add "${MCP_NAME}" \
  --transport streamable-http \
  --url "${MCP_URL}" \
  --auth oauth \
  --no-probe >/dev/null 2>&1; then
  :
else
  openclaw mcp set "${MCP_NAME}" "{\"url\":\"${MCP_URL}\",\"transport\":\"streamable-http\",\"auth\":\"oauth\"}" >/dev/null
fi

echo "Quandora plugin is installed for OpenClaw."
echo "Remote MCP authorization is handled by OpenClaw during first use or from the MCP UI."
echo "Try:"
echo '  openclaw agent --message "Use Quandora Factor Mining to show public tasks."'
