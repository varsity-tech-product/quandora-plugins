#!/usr/bin/env python3
"""Validate the isolated production WorkBuddy Connector submission candidate."""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONNECTOR_ROOT = REPOSITORY_ROOT / "connectors" / "workbuddy" / "quandora"
REQUIRED_SKILLS = {
    "factor-analysis",
    "factor-mining",
    "paper-trading",
    "strategy-analysis",
    "strategy-building",
    "strategy-portfolio",
}
EXPECTED_ROOT_ENTRIES = {"connector-meta.json", "mcp.json", "icon.png", "skills"}
EXPECTED_SERVER = {
    "type": "streamableHttp",
    "url": "https://mcp.quandora.ai/quant",
    "timeout": 30000,
}
CANONICAL_TOOL_NAMES = frozenset(
    """
    get_factor_mining_status list_factor_mining_tasks get_factor_plugin_contract
    create_factor_task_session create_custom_factor_session validate_factor_plugin
    get_factor_dedup_context submit_factor_backtest continue_factor_backtest
    create_factor_result_bundle_download read_factor_result_bundle_chunk
    list_owned_factor_families get_factor_family_history get_quandora_guidance
    check_quandora_plugin_version get_factor_backtest_window_cards
    get_factor_backtest_chart_data get_factor_backtest_source create_factor_chart_download
    create_factor_raw_artifact_download read_factor_chart_chunk get_official_factor_window_cards
    get_official_factor_chart_data get_official_factor_source
    create_official_factor_result_bundle_download read_official_factor_result_bundle_chunk
    get_strategy_capabilities list_eligible_strategy_factors get_eligible_strategy_factor
    list_shared_strategy_factor_candidates admit_shared_strategy_factor import_strategy_factor
    submit_adhoc_strategy_backtest list_strategy_backtests get_strategy_backtest
    continue_strategy_backtest rerun_strategy_backtest create_strategy_result_bundle_download
    read_strategy_result_bundle_chunk create_strategy revise_strategy get_strategy
    get_strategy_version submit_strategy_backtest get_strategy_backtest_artifact
    get_strategy_backtest_analysis_data create_strategy_artifact_download
    list_strategy_portfolios create_strategy_portfolio revise_strategy_portfolio
    get_strategy_portfolio get_strategy_portfolio_version submit_strategy_portfolio_backtest
    get_strategy_portfolio_backtest get_strategy_portfolio_backtest_result
    list_paper_trade_sources get_paper_trade_source list_paper_trades get_paper_trade
    start_paper_trade refresh_paper_trade_account_snapshot list_closed_paper_trade_positions
    get_paper_trade_equity_curve list_paper_trade_fills list_paper_trade_funding
    get_paper_trade_strategy_code stop_paper_trade start_strategy_portfolio_paper_trade
    get_strategy_portfolio_paper_trade stop_strategy_portfolio_paper_trade
    """.split()
)
RETIRED_TOOL_NAMES = frozenset(
    """
    fm_status fm_list_tasks fm_get_contract fm_task_session fm_custom_sess fm_validate
    fm_dedup_context fm_run_backtest fm_resume_run fm_window_cards fm_chart_data
    fm_run_source fm_png_ticket fm_raw_ticket fm_bundle_ticket fm_bundle_chunk fm_png_chunk
    fm_list_factors fm_get_history of_window_cards of_chart_data of_run_source
    of_bundle_ticket of_bundle_chunk qd_get_guidance qd_plugin_ver sb_get_contract
    sb_list_eligible sb_factor_detail sb_shared_list sb_shared_add sb_import_factor
    sb_submit_run sb_list_runs sb_get_run sb_resume_run sb_rerun_run sb_get_artifact
    sb_analysis_data sb_file_ticket sb_bundle_ticket sb_bundle_chunk pt_src_create
    pt_src_revise pt_src_def_get pt_src_ver_get pt_src_bt_submit pt_list_sources
    pt_get_source pt_list_runs pt_get_run pt_submit_run pt_get_portfolio pt_list_pos
    pt_get_equity pt_list_fills pt_list_funding pt_get_code pt_stop_run pt_sp_list
    pt_sp_create pt_sp_revise pt_sp_get pt_sp_version pt_sp_bt_submit pt_sp_bt_get
    pt_sp_bt_result pt_sp_run_submit pt_sp_run_get pt_sp_run_stop
    """.split()
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(REPOSITORY_ROOT)}: invalid JSON: {exc}") from exc


def _check_metadata(errors: list[str]) -> None:
    document = _load_json(CONNECTOR_ROOT / "connector-meta.json")
    if not isinstance(document, dict):
        errors.append("connector-meta.json must contain one JSON object")
        return
    for field in (
        "name",
        "name_zh",
        "name_en",
        "description",
        "description_zh",
        "description_en",
    ):
        if not isinstance(document.get(field), str) or not document[field].strip():
            errors.append(f"connector-meta.json: {field} must be a non-empty string")
    if document.get("source") != "quandora":
        errors.append("connector-meta.json: source must be quandora")
    if document.get("type") != "mcp":
        errors.append("connector-meta.json: type must be mcp")
    if document.get("minWorkbuddyVersion") != "4.24.0":
        errors.append("connector-meta.json: localized examples require minWorkbuddyVersion 4.24.0")
    for forbidden in ("auth_mode", "maxWorkbuddyVersion", "version"):
        if forbidden in document:
            errors.append(f"connector-meta.json: omit unnecessary field {forbidden}")
    for field in ("examples_zh", "examples_en"):
        examples = document.get(field)
        if (
            not isinstance(examples, list)
            or not 2 <= len(examples) <= 5
            or any(not isinstance(item, str) or not item.strip() for item in examples)
        ):
            errors.append(f"connector-meta.json: {field} must contain 2-5 non-empty strings")


def _check_mcp(errors: list[str]) -> None:
    expected = {"mcpServers": {"quandora": EXPECTED_SERVER}}
    if _load_json(CONNECTOR_ROOT / "mcp.json") != expected:
        errors.append("mcp.json must declare exactly the approved single HTTPS streamableHttp server")


def _check_icon(errors: list[str]) -> None:
    path = CONNECTOR_ROOT / "icon.png"
    try:
        data = path.read_bytes()
    except OSError as exc:
        errors.append(f"icon.png cannot be read: {exc}")
        return
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        errors.append("icon.png must be a valid PNG")
        return
    width, height, _depth, color_type = struct.unpack(">IIBB", data[16:26])
    if width < 64 or height < 64:
        errors.append("icon.png must be at least 64x64")
    if color_type not in {4, 6}:
        errors.append("icon.png must include an alpha channel")


def _check_skills(errors: list[str]) -> None:
    skills_root = CONNECTOR_ROOT / "skills"
    actual_skills = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if actual_skills != REQUIRED_SKILLS:
        errors.append(f"skills must be exactly {sorted(REQUIRED_SKILLS)}")

    markdown_files = sorted(skills_root.rglob("*.md"))
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in markdown_files)
    if re.search(r"staging", corpus, re.IGNORECASE):
        errors.append("production Connector skills must not contain staging identity or wording")
    for name in sorted(CANONICAL_TOOL_NAMES):
        if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", corpus):
            errors.append(f"canonical tool is not documented: {name}")
    for name in sorted(RETIRED_TOOL_NAMES):
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", corpus):
            errors.append(f"retired tool name is forbidden: {name}")

    for skill_name in REQUIRED_SKILLS:
        skill_path = skills_root / skill_name / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"skills/{skill_name}/SKILL.md is required")
            continue
        text = skill_path.read_text(encoding="utf-8")
        if not re.match(rf"---\s*\nname:\s*{re.escape(skill_name)}\s*\n", text):
            errors.append(f"skills/{skill_name}/SKILL.md must start with matching frontmatter name")
        if "\ndescription:" not in text.split("---", 2)[1]:
            errors.append(f"skills/{skill_name}/SKILL.md must declare a frontmatter description")
        if "Bundled plugin version: 3.0-preview" not in text:
            errors.append(f"skills/{skill_name}/SKILL.md must retain the current production version")


def main() -> int:
    errors: list[str] = []
    if not CONNECTOR_ROOT.is_dir():
        errors.append("WorkBuddy Connector root is missing")
    else:
        entries = {path.name for path in CONNECTOR_ROOT.iterdir()}
        if entries != EXPECTED_ROOT_ENTRIES:
            errors.append(f"Connector root entries must be exactly {sorted(EXPECTED_ROOT_ENTRIES)}")
        if any(path.name == "scripts" for path in CONNECTOR_ROOT.rglob("scripts")):
            errors.append("Connector submission must not contain scripts")
        _check_metadata(errors)
        _check_mcp(errors)
        _check_icon(errors)
        _check_skills(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("WorkBuddy production Connector contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
