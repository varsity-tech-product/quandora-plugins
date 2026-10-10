#!/usr/bin/env python3
"""Validate the production Quandora plugin package and research boundaries."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "quandora"
SKILLS = PLUGIN / "skills"
EXPECTED_SKILLS = {
    "factor-analysis",
    "factor-mining",
    "paper-trading",
    "strategy-analysis",
    "strategy-building",
}
DIRECT_MANIFESTS = (
    ROOT / "kimi.plugin.json",
    PLUGIN / ".claude-plugin" / "plugin.json",
    PLUGIN / ".codebuddy-plugin" / "plugin.json",
    PLUGIN / ".codex-plugin" / "plugin.json",
    PLUGIN / ".cursor-plugin" / "plugin.json",
)
MARKETPLACES = (
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".codebuddy-plugin" / "marketplace.json",
)
PRODUCTION_FACTOR_ACTIONS = (
    "fm_list_tasks",
    "fm_get_contract",
    "fm_task_session",
    "fm_custom_sess",
    "fm_validate",
    "fm_run_backtest",
)
STAGING_FACTOR_ACTIONS = (
    "list_factor_mining_tasks",
    "get_factor_plugin_contract",
    "create_factor_task_session",
    "create_custom_factor_session",
    "validate_factor_plugin",
    "submit_factor_backtest",
)
RESEARCH_MARKERS = {
    "factor-mining": (
        "runtime_rules.data_availability.binance_intraday",
        "runtime_rules.research_guidance",
        "upstream_pipeline_version",
        "source_date == as_of_date - 1 day",
        "Do not keep a separate 86-field",
        "selected public Task's returned research fields",
        "trade_vol_max_b",
        "trade_vol_max_s",
    ),
    "factor-analysis": (
        "current global 86-field semantics",
        "Large trades are not automatically smart money",
        "not evidence that a historical row had arrived",
        "publication SLA is not proof of historical arrival",
    ),
    "strategy-building": (
        "Strategy construction consumes exact admitted Factor identities",
        "apply an additional date shift",
    ),
    "strategy-analysis": (
        "Factor input definitions and D/D+1 alignment",
        "current Factor Plugin Contract proves what data was available",
    ),
    "paper-trading": (
        "realign the D feature row to D+1",
        "publication SLA as an arrival",
        "validates every required history column and bar before Lean execution",
        "does not silently",
        "smaller universe",
    ),
}


def load_json(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return document


def support_text(skill: str) -> str:
    directory = SKILLS / skill
    parts = [(directory / "SKILL.md").read_text(encoding="utf-8")]
    references = directory / "references"
    if references.is_dir():
        parts.extend(
            path.read_text(encoding="utf-8")
            for path in sorted(references.glob("*.md"))
        )
    return "\n".join(parts)


def main() -> int:
    errors: list[str] = []
    try:
        version = load_json(PLUGIN / ".codex-plugin" / "plugin.json")["version"]
        if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9._+\-]{1,64}", version):
            raise ValueError("invalid installed release label")
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"ERROR: canonical plugin manifest: {exc}", file=sys.stderr)
        return 1
    policy = PLUGIN / "references" / "connection-and-version.md"
    if not policy.is_file():
        errors.append("missing shared connection-and-version policy")
    else:
        policy_text = policy.read_text(encoding="utf-8")
        if re.search(r"`[0-9]+\.[0-9]+[^`]*`", policy_text):
            errors.append("shared runtime policy must not hard-code a release label")
        if "Refresh the Quandora MCP connection." in policy_text or "A Quandora MCP access token is valid for" in policy_text:
            errors.append("shared runtime policy contains obsolete user-facing token boilerplate")

    for path in DIRECT_MANIFESTS:
        try:
            actual = load_json(path).get("version")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid manifest: {exc}")
            continue
        if actual != version:
            errors.append(f"{path.relative_to(ROOT)}: expected version {version}, got {actual!r}")

    for path in MARKETPLACES:
        try:
            document = load_json(path)
            plugins = document.get("plugins")
            plugin_versions = [
                item.get("version")
                for item in plugins
                if isinstance(item, dict) and item.get("name") == "quandora"
            ] if isinstance(plugins, list) else []
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid manifest: {exc}")
            continue
        if document.get("version") != version or plugin_versions != [version]:
            errors.append(f"{path.relative_to(ROOT)}: marketplace versions must all be {version}")

    actual_skills = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
    if actual_skills != EXPECTED_SKILLS:
        errors.append(
            f"skill set mismatch: expected={sorted(EXPECTED_SKILLS)} actual={sorted(actual_skills)}"
        )

    for skill in sorted(actual_skills):
        skill_path = SKILLS / skill / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        if "[connection and version policy](../../references/connection-and-version.md)" not in text:
            errors.append(f"{skill}/SKILL.md: missing shared runtime policy")
        if "installed_version" in text or "Bundled plugin version:" in text:
            errors.append(f"{skill}/SKILL.md: version logic must use the shared policy, not a copied label or check")
        normalized_skill = " ".join(text.split()).lower()
        if any(marker in normalized_skill for marker in (
            "access token is valid for", "access tokens expire after", "seven-day lifetime",
            "refresh the quandora mcp connection",
            "re-authenticate it with the cli",
        )):
            errors.append(f"{skill}/SKILL.md: obsolete token lifetime/refresh boilerplate")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#", "<")):
                continue
            resolved = (skill_path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"{skill}/SKILL.md: broken local reference {target!r}")

        normalized = " ".join(support_text(skill).split())
        for marker in RESEARCH_MARKERS.get(skill, ()):
            if " ".join(marker.split()) not in normalized:
                errors.append(f"{skill}: missing research boundary {marker!r}")

    factor_text = support_text("factor-mining")
    for action in PRODUCTION_FACTOR_ACTIONS:
        if f"`{action}`" not in factor_text:
            errors.append(f"factor-mining: missing production action {action!r}")
    for action in STAGING_FACTOR_ACTIONS:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(action)}(?![A-Za-z0-9_])", factor_text):
            errors.append(f"factor-mining: staging action leaked into production: {action!r}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Quandora production plugin checks passed for {version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
