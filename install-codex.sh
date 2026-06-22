#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE_SOURCE="${QUANDORA_PLUGIN_SOURCE:-varsity-tech-product/quandora-plugins}"
MARKETPLACE_REF="${QUANDORA_PLUGIN_REF:-v0.4.0}"
MARKETPLACE_NAME="${QUANDORA_PLUGIN_MARKETPLACE:-quandora}"
PLUGIN_NAME="${QUANDORA_PLUGIN_NAME:-quandora}"
START_MODE="${QUANDORA_START_MODE:-none}"
WORKSPACE_PATH="${QUANDORA_WORKSPACE:-.}"
CODEX_PROMPT="${QUANDORA_CODEX_PROMPT:-Use Quandora Factor Mining to show public tasks.}"

usage() {
  cat <<'USAGE'
Usage: install-codex.sh [options]

Options:
  --desktop      Install, print next steps, then open Codex Desktop.
  --start        Install, print next steps, then start Codex CLI.
  --no-start     Install and print next steps. This is the default.
  -h, --help     Show this help.

Default install:
  codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.0
  codex plugin add quandora@quandora
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --desktop)
      START_MODE="desktop"
      ;;
    --start)
      START_MODE="cli"
      ;;
    --no-start)
      START_MODE="none"
      ;;
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
  shift
done

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is required. Install or update Codex, then run this script again." >&2
  exit 1
fi

marketplace_configured() {
  codex plugin marketplace list 2>/dev/null | awk 'NR > 1 { print $1 }' | grep -Fxq "${MARKETPLACE_NAME}"
}

plugin_installed() {
  codex plugin list --marketplace "${MARKETPLACE_NAME}" 2>/dev/null |
    grep -E "^${PLUGIN_NAME}@${MARKETPLACE_NAME}[[:space:]]+installed, enabled" >/dev/null
}

print_next_steps() {
  echo "Quandora plugin is installed."
  echo "Remote MCP authorization is handled by Codex during first use."
  echo "Try:"
  printf '  codex %q\n' "${CODEX_PROMPT}"
}

echo "Configuring Codex marketplace: ${MARKETPLACE_NAME}"
if marketplace_configured; then
  echo "Marketplace already configured; refreshing if it is Git-backed."
  if ! codex plugin marketplace upgrade "${MARKETPLACE_NAME}" >/dev/null 2>&1; then
    echo "Marketplace refresh did not complete. Continuing with the configured source." >&2
  fi
else
  if [[ -d "${MARKETPLACE_SOURCE}" ]]; then
    codex plugin marketplace add "${MARKETPLACE_SOURCE}"
  else
    codex plugin marketplace add "${MARKETPLACE_SOURCE}" --ref "${MARKETPLACE_REF}"
  fi
fi

echo "Installing Codex plugin: ${PLUGIN_NAME}@${MARKETPLACE_NAME}"
if plugin_installed; then
  echo "Plugin already installed."
else
  codex plugin add "${PLUGIN_NAME}@${MARKETPLACE_NAME}"
fi

case "${START_MODE}" in
  none)
    print_next_steps
    ;;
  desktop)
    print_next_steps
    exec codex app "${WORKSPACE_PATH}"
    ;;
  cli)
    print_next_steps
    exec codex "${CODEX_PROMPT}"
    ;;
  *)
    echo "Unknown start mode: ${START_MODE}" >&2
    exit 2
    ;;
esac
