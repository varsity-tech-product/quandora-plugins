#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="${QUANDORA_PLUGIN_NAME:-quandora}"
MARKETPLACE_URL="${QUANDORA_PLUGIN_MARKETPLACE_URL:-https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.3}"
INSTALLER_URL="${QUANDORA_OPENCLAW_INSTALLER_URL:-https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/v0.4.3/install-openclaw.sh}"
MCP_NAME="${QUANDORA_MCP_NAME:-quandora-mcp}"
MCP_URL="${QUANDORA_MCP_URL:-https://mcp.quandora.ai/factor-mining}"
SKILL_NAME="${QUANDORA_FACTOR_MINING_SKILL_NAME:-factor-mining}"
ALLOW_SKILL=0
TARGET_AGENT="${QUANDORA_OPENCLAW_AGENT_ID:-}"

usage() {
  cat <<'USAGE'
Usage: install-openclaw.sh [options]

Options:
  --allow-skill       Add factor-mining to the target agent skill allowlist and
                      verify the existing install.
  --agent <id>        Target agent for --allow-skill. Defaults to OpenClaw's
                      current default agent.
  -h, --help          Show this help.

Default install:
  openclaw plugins install quandora --marketplace https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.3 --force
  openclaw mcp add quandora-mcp --transport streamable-http --url https://mcp.quandora.ai/factor-mining --auth oauth --no-probe
USAGE
}

verify_openclaw_install() {
  echo "Verifying OpenClaw plugin: ${PLUGIN_NAME}"
  openclaw plugins inspect "${PLUGIN_NAME}" >/dev/null

  echo "Verifying Remote MCP server: ${MCP_NAME}"
  openclaw mcp show "${MCP_NAME}" >/dev/null

  echo "Verifying OpenClaw skill: ${SKILL_NAME}"
  local skill_info
  skill_info="$(openclaw skills info "${SKILL_NAME}" 2>&1)"

  if [[ "${skill_info}" == *"Excluded by agent allowlist"* ]]; then
    echo "The ${SKILL_NAME} skill is installed but excluded by the current agent allowlist."
    echo "Run:"
    echo "  curl -fsSL ${INSTALLER_URL} | bash -s -- --allow-skill"
    return 0
  fi

  echo "OpenClaw verification passed."
  echo "Start OpenClaw:"
  echo "  openclaw chat"
  echo "Then run:"
  echo "  /${SKILL_NAME} show public tasks"
}

allow_skill_for_agent() {
  if ! command -v node >/dev/null 2>&1; then
    echo "node is required for --allow-skill so the existing agent allowlist can be preserved." >&2
    exit 1
  fi

  local config_path
  config_path="$(openclaw config file)"
  config_path="${config_path/#\~/$HOME}"

  local patch_file
  patch_file="$(mktemp)"

  local result
  result="$(
    OPENCLAW_CONFIG_PATH="${config_path}" \
    QUANDORA_OPENCLAW_PATCH_FILE="${patch_file}" \
    QUANDORA_OPENCLAW_AGENT_ID="${TARGET_AGENT}" \
    QUANDORA_FACTOR_MINING_SKILL_NAME="${SKILL_NAME}" \
    node <<'NODE'
const fs = require("fs");

const configPath = process.env.OPENCLAW_CONFIG_PATH;
const patchFile = process.env.QUANDORA_OPENCLAW_PATCH_FILE;
const targetAgentId = process.env.QUANDORA_OPENCLAW_AGENT_ID || "";
const skillName = process.env.QUANDORA_FACTOR_MINING_SKILL_NAME || "factor-mining";

const data = JSON.parse(fs.readFileSync(configPath, "utf8"));
const agents = Array.isArray(data?.agents?.list) ? data.agents.list : [];
if (agents.length === 0) {
  throw new Error("No OpenClaw agents are configured.");
}

let index = -1;
if (targetAgentId) {
  index = agents.findIndex((agent) => agent && agent.id === targetAgentId);
} else {
  index = agents.findIndex((agent) => agent && agent.default === true);
  if (index < 0) index = 0;
}

if (index < 0) {
  throw new Error(`OpenClaw agent not found: ${targetAgentId}`);
}

const agent = agents[index];
const agentId = agent.id || String(index);
if (!Array.isArray(agent.skills)) {
  console.log(`noop:${agentId}:all-skills`);
  process.exit(0);
}

if (agent.skills.includes(skillName)) {
  console.log(`noop:${agentId}:already-allowed`);
  process.exit(0);
}

const nextAgents = agents.map((entry, i) => {
  if (i !== index) return entry;
  return { ...entry, skills: [...entry.skills, skillName] };
});

fs.writeFileSync(patchFile, JSON.stringify({ agents: { list: nextAgents } }, null, 2) + "\n");
console.log(`patch:${agentId}`);
NODE
  )"

  case "${result}" in
    patch:*)
      local agent_id="${result#patch:}"
      echo "Adding ${SKILL_NAME} to OpenClaw agent allowlist: ${agent_id}"
      openclaw config patch --file "${patch_file}" --replace-path agents.list >/dev/null
      echo "Reloading OpenClaw gateway."
      openclaw gateway restart >/dev/null || openclaw mcp reload >/dev/null || true
      ;;
    noop:*:all-skills)
      local value="${result#noop:}"
      echo "OpenClaw agent ${value%:all-skills} does not use an explicit skill allowlist."
      ;;
    noop:*:already-allowed)
      local value="${result#noop:}"
      echo "OpenClaw agent ${value%:already-allowed} already allows ${SKILL_NAME}."
      ;;
    *)
      echo "Unexpected --allow-skill result: ${result}" >&2
      exit 1
      ;;
  esac

  rm -f "${patch_file}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-skill)
      ALLOW_SKILL=1
      shift
      ;;
    --agent)
      if [[ $# -lt 2 ]]; then
        echo "--agent requires an OpenClaw agent id." >&2
        exit 2
      fi
      TARGET_AGENT="$2"
      shift 2
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
done

if ! command -v openclaw >/dev/null 2>&1; then
  echo "OpenClaw CLI is required. Install or update OpenClaw, then run this script again." >&2
  exit 1
fi

if [[ "${ALLOW_SKILL}" -eq 1 ]]; then
  allow_skill_for_agent
  verify_openclaw_install
  exit 0
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
verify_openclaw_install
