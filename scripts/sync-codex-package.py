#!/usr/bin/env python3
"""Regenerate the Codex package: the shared package without its Agent Plugins and Antigravity root files.

Codex reads a plugin whose root plugin.json declares the Agent Plugins $schema through that format
and then binds only part of its MCP tools. WorkBuddy and Antigravity need those root files, so Codex
installs this mirror instead. Run after every change under plugins/quandora/.
"""

from __future__ import annotations

import shutil
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SHARED_PACKAGE = REPOSITORY_ROOT / "plugins" / "quandora"
CODEX_PACKAGE = REPOSITORY_ROOT / "plugins" / "quandora-codex"
CODEX_EXCLUDED_ROOT_FILES = ("plugin.json", "mcp.json", "mcp_config.json")


def _ignore(directory: str, names: list[str]) -> set[str]:
    if Path(directory) == SHARED_PACKAGE:
        return {name for name in names if name in CODEX_EXCLUDED_ROOT_FILES}
    return set()


def main() -> int:
    if CODEX_PACKAGE.exists():
        shutil.rmtree(CODEX_PACKAGE)
    shutil.copytree(SHARED_PACKAGE, CODEX_PACKAGE, ignore=_ignore, symlinks=True)
    print(f"Synced {CODEX_PACKAGE.relative_to(REPOSITORY_ROOT)} from {SHARED_PACKAGE.relative_to(REPOSITORY_ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
