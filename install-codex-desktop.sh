#!/usr/bin/env bash
set -euo pipefail

# Delegates to install-codex.sh, whose stable default ref is v0.4.0.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
exec "${SCRIPT_DIR}/install-codex.sh" --desktop "$@"
