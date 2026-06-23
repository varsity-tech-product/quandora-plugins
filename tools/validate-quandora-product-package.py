#!/usr/bin/env python3
"""Validate the v0.4.5 Quandora Remote MCP product package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.4.5"
TAG = "v0.4.5"
PLUGIN = "quandora"
PLUGIN_DIR = ROOT / "plugins" / PLUGIN
REMOTE_MCP_URL = "https://mcp-staging.varsity.lol/factor-mining"
REMOTE_MCP_NAME = "quandora-mcp"

FORBIDDEN_PRODUCT_PATHS = [
    ROOT / "docs",
    ROOT / "install-codex.sh",
    ROOT / "install-codex-desktop.sh",
    ROOT / "plugins" / "factor-mining",
    ROOT / "plugins" / "factor-mining-demo",
    ROOT / "plugins" / "factor-mining-batch-test",
    PLUGIN_DIR / "assets",
    PLUGIN_DIR / "mcp" / "server.py",
    PLUGIN_DIR / "mcp" / "launch.py",
    PLUGIN_DIR / "mcp" / "factor_mining_agent_lib",
    PLUGIN_DIR / "skills" / "factor-mining-batch",
]

FORBIDDEN_REMOTE_MCP_KEYS = {"command", "args", "cwd"}
FORBIDDEN_TEXT_PATTERNS = [
    (re.compile(r"factor-mining-agent-plugins"), "old product repository name"),
    (re.compile(r"factor-mining-marketplace"), "old marketplace name"),
    (re.compile(r"factor-mining-demo"), "demo package reference"),
    (re.compile(r"factor-mining-batch-test"), "batch package reference"),
    (re.compile(r"\bvt_"), "direct vt_ credential flow"),
    (re.compile(r"\bCursor\b|\bcursor\b"), "Cursor install claim"),
    (re.compile(r"--ref main|@main|/main/"), "moving main install ref"),
    (re.compile(r"quandora-factor-mining"), "old Factor Mining-specific MCP name"),
    (re.compile(r"Codex CLI/TUI|Codex CLI and TUI"), "Codex TUI install label"),
]

USER_FACING_DOCS = [
    ROOT / "README.md",
    ROOT / "install-openclaw.sh",
]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing JSON file: {path.relative_to(ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}


def fail(message: str) -> None:
    FAILURES.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_marketplace(path: Path, claude: bool = False) -> None:
    data = load_json(path)
    expect(data.get("name") == PLUGIN, f"{rel(path)} name must be {PLUGIN!r}")
    plugins = data.get("plugins")
    expect(isinstance(plugins, list), f"{rel(path)} plugins must be a list")
    expect(len(plugins or []) == 1, f"{rel(path)} must list exactly one plugin")
    if not plugins:
        return
    entry = plugins[0]
    expect(entry.get("name") == PLUGIN, f"{rel(path)} plugin name must be {PLUGIN!r}")
    source = entry.get("source")
    source_path = source if isinstance(source, str) else source.get("path") if isinstance(source, dict) else None
    expect(source_path == "./plugins/quandora", f"{rel(path)} plugin source must be ./plugins/quandora")
    if claude:
        expect(entry.get("version") == VERSION, f"{rel(path)} plugin version must be {VERSION}")
    else:
        policy = entry.get("policy") or {}
        expect(policy.get("installation") == "AVAILABLE", f"{rel(path)} must mark plugin available")
        expect(policy.get("authentication") == "ON_USE", f"{rel(path)} auth policy must be ON_USE")


def validate_plugin_manifest(path: Path, *, codex: bool) -> None:
    data = load_json(path)
    expect(data.get("name") == PLUGIN, f"{rel(path)} name must be {PLUGIN!r}")
    expect(data.get("version") == VERSION, f"{rel(path)} version must be {VERSION}")
    expect(data.get("repository") == "https://github.com/varsity-tech-product/quandora-plugins", f"{rel(path)} repository URL is wrong")
    expect(data.get("homepage") == "https://github.com/varsity-tech-product/quandora-plugins", f"{rel(path)} homepage URL is wrong")
    if codex:
        expect((data.get("interface") or {}).get("displayName") == "Quandora", f"{rel(path)} display name must be Quandora")
        expect(data.get("skills") == "./skills/", f"{rel(path)} must expose ./skills/")
        expect(data.get("mcpServers") == "./.mcp.json", f"{rel(path)} must point to ./.mcp.json")
    else:
        servers = data.get("mcpServers")
        expect(isinstance(servers, dict), f"{rel(path)} must inline Claude Remote MCP servers")
        server = (servers or {}).get(REMOTE_MCP_NAME)
        expect(isinstance(server, dict), f"{rel(path)} must define {REMOTE_MCP_NAME}")
        if not isinstance(server, dict):
            return
        expect(server.get("type") == "http", f"{rel(path)} Claude MCP transport must be http")
        expect(server.get("url") == REMOTE_MCP_URL, f"{rel(path)} Claude MCP URL is wrong")
        expect(not (FORBIDDEN_REMOTE_MCP_KEYS & set(server)), f"{rel(path)} must not contain stdio MCP keys")


def validate_shared_mcp() -> None:
    data = load_json(PLUGIN_DIR / ".mcp.json")
    servers = data.get("mcp_servers") if isinstance(data.get("mcp_servers"), dict) else data
    expect(isinstance(servers, dict), "plugins/quandora/.mcp.json must be a server map")
    server = (servers or {}).get(REMOTE_MCP_NAME)
    expect(isinstance(server, dict), f"plugins/quandora/.mcp.json must define {REMOTE_MCP_NAME}")
    if not isinstance(server, dict):
        return
    expect(server.get("url") == REMOTE_MCP_URL, "shared MCP URL is wrong")
    expect(server.get("oauth_resource") == REMOTE_MCP_URL, "shared MCP OAuth resource is wrong")
    expect(not (FORBIDDEN_REMOTE_MCP_KEYS & set(server)), "shared MCP must not contain stdio keys")


def validate_layout() -> None:
    expect(PLUGIN_DIR.is_dir(), "plugins/quandora must exist")
    packages = sorted(path.name for path in (ROOT / "plugins").iterdir() if path.is_dir()) if (ROOT / "plugins").exists() else []
    expect(packages == [PLUGIN], "plugins/ must contain exactly plugins/quandora")
    for path in FORBIDDEN_PRODUCT_PATHS:
        expect(not path.exists(), f"forbidden product path exists: {rel(path)}")
    expect((PLUGIN_DIR / "skills" / "factor-mining" / "SKILL.md").is_file(), "factor-mining skill is missing")
    expect((PLUGIN_DIR / "skills" / "factor-mining" / "agents" / "openai.yaml").is_file(), "factor-mining openai.yaml is missing")
    for path in PLUGIN_DIR.rglob("*"):
        expect("factor_mining_agent_lib" not in path.parts, f"forbidden library path in plugin: {rel(path)}")
        if path.is_file():
            expect(path.name not in {"server.py", "launch.py"}, f"forbidden local MCP file in plugin: {rel(path)}")


def validate_docs() -> None:
    for path in USER_FACING_DOCS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        expect(TAG in text, f"{rel(path)} must pin stable install docs to {TAG}")
        for pattern, reason in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                fail(f"{rel(path)} contains {reason}")


def validate_skill() -> None:
    path = PLUGIN_DIR / "skills" / "factor-mining" / "SKILL.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_tools = [
        "factor_mining_status",
        "factor_mining_list_public_tasks",
        "factor_mining_create_task_session",
        "factor_mining_create_custom_session",
        "factor_mining_validate_plugin_source",
        "factor_mining_request_dedup_context",
        "factor_mining_upload_backtest_wait",
        "factor_mining_resume_run",
        "factor_mining_get_artifact",
    ]
    forbidden_tools = ["factor_mining_batch_start", "factor_mining_batch_upload_backtest_wait"]
    for tool in required_tools:
        expect(tool in text, f"skill must mention Remote MCP tool {tool}")
    for tool in forbidden_tools:
        expect(tool not in text, f"skill must not expose v0.4.5 batch tool {tool}")
    expect("plugin_source" in text, "skill must require inline plugin_source")
    expect("plugin_path" not in text, "skill must not allow plugin_path upload")


FAILURES: list[str] = []


def main() -> int:
    validate_layout()
    validate_marketplace(ROOT / ".agents" / "plugins" / "marketplace.json")
    validate_marketplace(ROOT / ".claude-plugin" / "marketplace.json", claude=True)
    validate_plugin_manifest(PLUGIN_DIR / ".codex-plugin" / "plugin.json", codex=True)
    validate_plugin_manifest(PLUGIN_DIR / ".claude-plugin" / "plugin.json", codex=False)
    validate_shared_mcp()
    validate_docs()
    validate_skill()

    if FAILURES:
        print("Quandora product package validation failed:", file=sys.stderr)
        for failure in FAILURES:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("Quandora product package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
