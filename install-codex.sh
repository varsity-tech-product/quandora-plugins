#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE_SOURCE="${FACTOR_MINING_PLUGIN_SOURCE:-varsity-tech-product/factor-mining-agent-plugins}"
MARKETPLACE_REF="${FACTOR_MINING_PLUGIN_REF:-main}"
MARKETPLACE_NAME="${FACTOR_MINING_PLUGIN_MARKETPLACE:-factor-mining-marketplace}"
PLUGIN_NAME="${FACTOR_MINING_PLUGIN_NAME:-factor-mining}"
START_CODEX="${FACTOR_MINING_START_CODEX:-1}"
SKIP_SETUP="${FACTOR_MINING_SKIP_SETUP:-0}"
CODEX_PROMPT="${FACTOR_MINING_CODEX_PROMPT:-Use the Factor Mining plugin. Verify Factor Mining status. If it is already configured, choose an open task, write a valid plugin.py, upload it, wait for the backtest, fetch the default factor card if available, and summarize the result. If setup is missing, run the secure setup helper and do not ask me to paste the key into chat.}"

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is required. Install or update Codex, then run this script again." >&2
  exit 1
fi

marketplace_configured() {
  codex plugin marketplace list 2>/dev/null | awk 'NR > 1 { print $1 }' | grep -Fxq "${MARKETPLACE_NAME}"
}

plugin_installed() {
  codex plugin list --marketplace "${MARKETPLACE_NAME}" 2>/dev/null \
    | grep -E "^${PLUGIN_NAME}@${MARKETPLACE_NAME}[[:space:]]+installed, enabled" >/dev/null
}

plugin_root() {
  codex plugin list --marketplace "${MARKETPLACE_NAME}" 2>/dev/null \
    | awk -v plugin="${PLUGIN_NAME}@${MARKETPLACE_NAME}" '$1 == plugin { print $NF; exit }'
}

prompt_agent_key() {
  local key
  if [[ -n "${FACTOR_MINING_AGENT_API_KEY:-}" ]]; then
    printf '%s\n' "${FACTOR_MINING_AGENT_API_KEY}"
    return
  fi
  if [[ ! -r /dev/tty ]]; then
    echo "A terminal is required to enter the Factor Mining Agent API Key securely." >&2
    echo "Run this script from an interactive terminal, or set FACTOR_MINING_SKIP_SETUP=1 and configure setup later." >&2
    exit 1
  fi
  printf 'Paste Factor Mining Agent API Key (input hidden): ' >/dev/tty
  IFS= read -r -s key </dev/tty
  printf '\n' >/dev/tty
  if [[ -z "${key}" ]]; then
    echo "A Factor Mining Agent API Key is required for setup." >&2
    exit 1
  fi
  printf '%s\n' "${key}"
}

configure_factor_mining() {
  local root="$1"
  if [[ "${SKIP_SETUP}" == "1" ]]; then
    echo "Skipping Factor Mining setup because FACTOR_MINING_SKIP_SETUP=1."
    return
  fi
  if python3 "${root}/scripts/factor_status.py" >/dev/null 2>&1; then
    echo "Factor Mining is already configured."
    return
  fi

  echo "Configuring Factor Mining Agent API access."
  echo "Paste the vt_ Agent API Key at the next prompt. It is hidden, not passed as a command argument, and not sent to Codex chat."
  local agent_key
  agent_key="$(prompt_agent_key)"
  printf '%s\n' "${agent_key}" | python3 "${root}/scripts/factor_setup.py" --api-key-stdin
  unset agent_key
}

echo "Configuring Codex marketplace: ${MARKETPLACE_NAME}"
if marketplace_configured; then
  echo "Marketplace already configured; refreshing if it is Git-backed."
  codex plugin marketplace upgrade "${MARKETPLACE_NAME}" >/dev/null 2>&1 || true
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

PLUGIN_ROOT="$(plugin_root)"
if [[ -z "${PLUGIN_ROOT}" || ! -d "${PLUGIN_ROOT}" ]]; then
  echo "Could not locate installed plugin root for ${PLUGIN_NAME}@${MARKETPLACE_NAME}." >&2
  exit 1
fi

configure_factor_mining "${PLUGIN_ROOT}"

if [[ "${START_CODEX}" == "0" ]]; then
  echo "Codex plugin is installed. Start it with:"
  printf 'codex %q\n' "${CODEX_PROMPT}"
  exit 0
fi

echo "Starting Codex."
exec codex "${CODEX_PROMPT}"
