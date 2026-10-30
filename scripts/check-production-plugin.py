#!/usr/bin/env python3
"""Validate portable, Agent-facing invariants for the production Plugin package."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPOSITORY_ROOT / "plugins" / "quandora"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
REQUIRED_SKILLS = {
    "account-connection",
    "factor-analysis",
    "factor-mining",
    "portfolio-trading-analysis",
    "strategy-analysis",
    "strategy-building",
    "portfolio-building",
    "portfolio-analysis",
}
ALLOWED_REPOSITORY_ROOT_ENTRIES = {
    ".gitbook",
    "SUMMARY.md",
    "agent-install-guide",
    "llms.txt",
    ".agents",
    ".claude-plugin",
    ".codebuddy-plugin",
    ".cursor-plugin",
    ".github",
    ".gitignore",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "assets",
    "kimi.plugin.json",
    "plugins",
    "scripts",
}
ALLOWED_PLUGIN_ROOT_ENTRIES = {
    ".claude-plugin",
    ".codebuddy-plugin",
    ".codex-plugin",
    ".cursor-plugin",
    ".mcp.json",
    "README.md",
    "assets",
    "mcp.json",
    "scripts",
    "skills",
    "references",
}
ALLOWED_SKILL_ENTRIES = {"SKILL.md", "agents", "assets", "references", "scripts"}
CLAUDE_PLUGIN_SUPPORT_SCRIPTS = {
    "claude-mcp-login-macos.sh",
    "claude-mcp-login-windows.ps1",
}
PRODUCTION_SUPPORT_SCRIPTS = CLAUDE_PLUGIN_SUPPORT_SCRIPTS | {'workbuddy-cn-install-macos.js', 'workbuddy-cn-bootstrap-macos.sh', 'workbuddy-mcp-login-macos.sh', 'workbuddy-cn-oauth-macos.js', 'workbuddy-mcp-login-windows.ps1'}
PUBLIC_PROSE_CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
MAX_MAIN_SKILL_LINES = 220
MAX_CODEX_DEFAULT_PROMPT_CHARS = 128
PORTFOLIO_RESULT_METRIC_MARKERS = (
    "net_profit_pct",
    "annual_return_pct",
    "annual_std",
    "max_drawdown_pct",
)
PORTFOLIO_SOURCE_EVIDENCE_MARKERS = (
    "operation.portfolio.manage", "preparing_sources", "one to five", "100000", "summary",
    "equity_curve.points[].t", "equity_curve.points[].value",
    "source_result_evidence_unavailable", "invalid_backend_response",
    "run.automatic_paper", "source_portfolio_run_id", "portfolio_trading_run_id",
    "base_portfolio_id",
)
STRATEGY_CALLER_BOUNDARY_GUIDANCE_MARKERS = (
    "`caller_supplied_fields`",
    "the sole request boundary",
    "Do not copy server-managed values into Skill guidance",
    "do not add any field absent from the live submit schema",
    "Do not display or ask for confirmation of server-managed fields",
)
STRATEGY_SERVER_VALUE_GUIDANCE_MARKERS = (
    "`initial_cash=100000`",
    "`taker_fee_rate=0.0004`",
    "`maker_fee_rate=0.0002`",
    "`attribution=true`",
)
ROUTING_MARKERS = {
    "factor-analysis": ("Do not use for creating", "$factor-mining"),
    "factor-mining": ("Do not use for the Strategy", "$strategy-building", "$factor-analysis"),
    "portfolio-trading-analysis": ("Do not use to create", "$strategy-building", "$portfolio-building"),
    "strategy-analysis": ("Do not use to compose", "$strategy-building"),
    "strategy-building": (
        "Do not use for multi-Strategy Portfolio",
        "$portfolio-building",
        "$portfolio-trading-analysis",
        "$strategy-analysis",
    ),
    "portfolio-building": ("Do not use for single-Strategy", "$strategy-building", "$portfolio-trading-analysis"),
    "portfolio-analysis": ("Do not use to select", "$portfolio-building", "$strategy-analysis", "$portfolio-trading-analysis"),
}
INTRADAY_CONTRACT_MARKERS = {
    "factor-mining": (
        "`runtime_rules.data_availability.binance_intraday`",
        "`runtime_rules.research_guidance`",
        "`upstream_pipeline_version`",
        "`source_date == as_of_date - 1 day`",
        "Do not keep a separate 86-field",
        "`trade_vol_max_b` and `trade_vol_max_s` are not excluded",
        "selected public Task's returned research fields",
    ),
    "factor-analysis": (
        "`get_factor_plugin_contract`",
        "`data_columns[].upstream_pipeline_version`",
        "current global 86-field semantics",
        "Large trades are not automatically smart money",
        "not evidence that a historical row had arrived",
        "pre-00:02 UTC publication SLA is not proof of historical arrival",
    ),
    "strategy-building": (
        "Strategy construction consumes exact admitted Factor identities",
        "86-field semantic registry",
        "apply an additional date shift",
    ),
    "strategy-analysis": (
        "Factor input definitions and D/D+1 alignment",
        "current Factor Plugin Contract proves what data was available",
    ),
    "portfolio-building": (
        "must not copy the `binance_intraday` field registry",
        "preserve the retained StrategyRun evidence",
    ),
    "portfolio-trading-analysis": (
        "realign the D feature row to D+1",
        "publication SLA as an arrival guarantee",
        "validates every required history column and bar before Lean execution",
        "does not silently filter that symbol into a smaller universe",
    ),
}
CANONICAL_TOOL_OWNERS = {
    "account-connection": {"get_quandora_account"},
    "factor-mining": {
        "download_result_bundle",
        "get_factor_mining_status",
        "list_factor_mining_tasks",
        "get_factor_plugin_contract",
        "create_factor_task_session",
        "create_custom_factor_session",
        "validate_factor_plugin",
        "get_factor_dedup_context",
        "submit_factor_backtest",
        "continue_factor_backtest",
        "get_factor_reversal",
        "list_owned_factor_families",
        "get_factor_family_history",
        "get_quandora_guidance",
        "check_quandora_plugin_version",
    },
    "factor-analysis": {
        "get_factor_backtest_window_cards",
        "get_factor_backtest_chart_data",
        "get_factor_backtest_source",
        "create_factor_chart_download",
        "create_factor_raw_artifact_download",
        "read_factor_chart_chunk",
        "get_official_factor_window_cards",
        "get_official_factor_chart_data",
        "get_official_factor_source",
    },
    "strategy-building": {
        "create_strategy",
        "create_strategy_folder",
        "get_eligible_strategy_factor",
        "get_strategy",
        "get_strategy_backtest",
        "get_strategy_capabilities",
        "get_strategy_folder",
        "list_eligible_strategy_factors",
        "list_strategies",
        "list_strategy_backtests",
        "list_strategy_folders",
        "submit_strategy_backtest",
    },
    "strategy-analysis": {
        "get_strategy_backtest_artifact",
        "get_strategy_backtest_analysis_data",
        "create_strategy_artifact_download",
    },
    "portfolio-building": {
        "create_portfolio",
        "create_portfolio_folder",
        "create_portfolio_share",
        "get_portfolio",
        "get_portfolio_backtest",
        "get_portfolio_folder",
        "get_portfolio_share",
        "get_portfolio_share_research",
        "list_portfolio_backtests",
        "list_portfolio_folders",
        "list_portfolio_shares",
        "list_portfolios",
        "list_community_portfolios", "get_community_portfolio", "get_community_portfolio_research",
        "get_community_strategy_research", "get_community_factor_research", "read_community_research_artifact",
        "publish_portfolio_to_community", "get_portfolio_sharing", "share_portfolio_with_user",
        "extend_portfolio_share", "update_portfolio_share_intro", "set_portfolio_favorite", "list_favorite_portfolios",
        "submit_portfolio_backtest",
        "search_portfolio_share_recipients",
    },
    "portfolio-analysis": {
        "get_portfolio_backtest_result",
    },
    "portfolio-trading-analysis": {
        "create_and_start_simulation_account", "get_simulation_account_operation", "continue_simulation_account_operation",
        "rename_simulation_account", "archive_simulation_account", "restore_simulation_account",
        "list_live_accounts", "get_live_account", "list_live_account_runs", "get_live_account_run", "get_live_account_facts",
        "get_portfolio_trading_equity_curve",
        "get_portfolio_trading_run",
        "list_portfolio_trading_equity_points",
        "list_portfolio_trading_position_snapshots",
        "list_portfolio_trading_runs",
        "list_portfolio_trading_signals",
        "start_portfolio_trading_run",
        "stop_portfolio_trading_run",
        "list_simulation_accounts", "create_simulation_account", "start_simulation_account_run",
        "pause_portfolio_trading_run", "resume_portfolio_trading_run",
        "get_portfolio_net_snapshot", "list_portfolio_net_equity_points",
        "list_portfolio_net_fills", "list_portfolio_net_position_cycles",
    },
}
RETIRED_TOOL_NAMES = {
    # Factor reversal is retired: QuantAI evaluates each Factor's direction and Strategies apply it.
    "reverse_factor",
    "list_shared_strategy_factor_candidates", "admit_shared_strategy_factor",
    "redeem_portfolio_share", "create_live_account", "prepare_live_portfolio_run",
    "estimate_live_portfolio_capital", "start_live_portfolio_run", "stop_live_portfolio_run",
    "import_strategy_factor", "get_strategy_factor_import",
    "ImportStrategyFactor", "BeginStrategyFactorImport", "GetStrategyFactorImport",
    "operation.strategy.factor.import",
    "fm_status", "fm_list_tasks", "fm_get_contract", "fm_task_session",
    "fm_custom_sess", "fm_validate", "fm_dedup_context", "fm_run_backtest",
    "fm_resume_run", "fm_window_cards", "fm_chart_data", "fm_run_source",
    "fm_png_ticket", "fm_raw_ticket", "fm_bundle_ticket", "fm_bundle_chunk",
    "fm_png_chunk", "fm_list_factors", "fm_get_history", "of_window_cards",
    "of_chart_data", "of_run_source", "of_bundle_ticket", "of_bundle_chunk",
    "qd_get_guidance", "qd_plugin_ver", "sb_get_contract", "sb_list_eligible",
    "sb_factor_detail", "sb_shared_list", "sb_shared_add", "sb_import_factor",
    "sb_submit_run", "sb_list_runs", "sb_get_run", "sb_resume_run",
    "sb_rerun_run", "sb_get_artifact", "sb_analysis_data", "sb_file_ticket",
    "sb_bundle_ticket", "sb_bundle_chunk", "pt_src_create", "pt_src_revise",
    "pt_src_def_get", "pt_src_ver_get", "pt_src_bt_submit", "pt_list_sources",
    "pt_get_source", "pt_list_runs", "pt_get_run", "pt_submit_run",
    "pt_get_portfolio", "pt_list_pos", "pt_get_equity", "pt_list_fills",
    "pt_list_funding", "pt_get_code", "pt_stop_run", "pt_sp_list",
    "pt_sp_create", "pt_sp_revise", "pt_sp_get", "pt_sp_version",
    "pt_sp_bt_submit", "pt_sp_bt_get", "pt_sp_bt_result", "pt_sp_run_submit",
    "pt_sp_run_get", "pt_sp_run_stop",
    "submit_strategy_portfolio_backtest", "get_strategy_portfolio_backtest",
    "get_strategy_portfolio_backtest_result",
    "continue_strategy_backtest",
    "create_strategy_portfolio",
    "get_paper_trade",
    "get_paper_trade_equity_curve",
    "get_paper_trade_source",
    "get_paper_trade_strategy_code",
    "get_strategy_portfolio",
    "get_strategy_portfolio_evaluation",
    "get_strategy_portfolio_evaluation_result",
    "get_strategy_portfolio_paper_trade",
    "get_strategy_portfolio_version",
    "get_strategy_version",
    "list_closed_paper_trade_positions",
    "list_eligible_strategy_portfolio_source_runs",
    "list_paper_trade_fills",
    "list_paper_trade_funding",
    "list_paper_trade_sources",
    "list_paper_trades",
    "list_strategy_portfolios",
    "refresh_paper_trade_account_snapshot",
    "rerun_strategy_backtest",
    "revise_strategy",
    "revise_strategy_portfolio",
    "start_paper_trade",
    "start_strategy_portfolio_paper_trade",
    "stop_paper_trade",
    "stop_strategy_portfolio_paper_trade",
    "submit_adhoc_strategy_backtest",
    "submit_strategy_portfolio_evaluation",
}
DIRECT_VERSION_MANIFESTS = (
    REPOSITORY_ROOT / "kimi.plugin.json",
    PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codebuddy-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
    PLUGIN_ROOT / ".cursor-plugin" / "plugin.json",
)
MARKETPLACE_MANIFESTS = (
    REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
    REPOSITORY_ROOT / ".codebuddy-plugin" / "marketplace.json",
)
PORTFOLIO_METADATA_MANIFESTS = (
    REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
    REPOSITORY_ROOT / ".codebuddy-plugin" / "marketplace.json",
    REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json",
    REPOSITORY_ROOT / "kimi.plugin.json",
    PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codebuddy-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
    PLUGIN_ROOT / ".cursor-plugin" / "plugin.json",
)
FORBIDDEN_RUNTIME_MARKDOWN = {
    "/Users/": "workstation-specific POSIX path",
    "C:\\Users\\": "workstation-specific Windows path",
    "quandora-results/": "obsolete local result root",
    "10 MiB ZIP cap": "stale client-wide bundle cap",
    "at most 40 chunk calls": "stale fixed chunk-call cap",
    "Bundled plugin version:": "release version coupled to Skill instructions",
    "Release invariant:": "release-process history in user-facing documentation",
    "## Release Order": "deployment sequencing in user-facing documentation",
    "StrategyVersion": "removed Strategy identity layer",
    "PortfolioVersion": "removed Portfolio identity layer",
    "strategy_version_id": "removed Strategy selector",
    "portfolio_version_id": "removed Portfolio selector",
}
SEARCH_DISCOVERY_SKILLS = {
    "factor-analysis",
    "factor-mining",
    "portfolio-trading-analysis",
    "strategy-analysis",
    "strategy-building",
    "portfolio-building",
    "portfolio-analysis",
}
REQUIRED_RESULT_DESTINATIONS = {
    PLUGIN_ROOT / "README.md": (
        "Quandora result/factor/<factor_slug>.zip",
        "Quandora result/strategy/<strategy_slug>.zip",
    ),
    SKILLS_ROOT / "factor-mining" / "SKILL.md": (
        "Quandora result/factor/<factor_slug>.zip",
        "never silently fall back to a generic `factor` slug",
    ),
    SKILLS_ROOT / "strategy-building" / "SKILL.md": (
        "Quandora result/strategy/<strategy_slug>.zip",
    ),
}
MANDATORY_VERSION_PROBE_PATTERNS = (
    re.compile(r"^##\s+Plugin Version Reminder\s*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"first entry.{0,400}check_quandora_plugin_version", re.DOTALL | re.IGNORECASE),
    re.compile(
        r"check_quandora_plugin_version.{0,240}(before the business entry point|before the business action)",
        re.DOTALL | re.IGNORECASE,
    ),
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(REPOSITORY_ROOT)}: invalid JSON: {exc}") from exc


def _direct_version(path: Path) -> str | None:
    document = _load_json(path)
    if not isinstance(document, dict):
        return None
    version = document.get("version")
    return version if isinstance(version, str) and version else None


def _marketplace_versions(path: Path) -> list[str]:
    document = _load_json(path)
    if not isinstance(document, dict):
        return []
    versions = []
    root_version = document.get("version")
    if isinstance(root_version, str) and root_version:
        versions.append(root_version)
    plugins = document.get("plugins")
    if isinstance(plugins, list):
        staging = [
            item
            for item in plugins
            if isinstance(item, dict) and item.get("name") == "quandora"
        ]
        if len(staging) == 1 and isinstance(staging[0].get("version"), str):
            versions.append(staging[0]["version"])
    return versions


def _check_manifests(errors: list[str]) -> str | None:
    recorded: list[tuple[Path, str]] = []
    for path in DIRECT_VERSION_MANIFESTS:
        version = _direct_version(path)
        if version is None:
            errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: missing top-level version")
        else:
            recorded.append((path, version))

    for path in MARKETPLACE_MANIFESTS:
        versions = _marketplace_versions(path)
        if len(versions) != 2:
            errors.append(
                f"{path.relative_to(REPOSITORY_ROOT)}: expected marketplace and "
                "quandora versions"
            )
        else:
            recorded.extend((path, version) for version in versions)

    distinct = {version for _, version in recorded}
    if len(distinct) != 1:
        rendered = ", ".join(
            f"{path.relative_to(REPOSITORY_ROOT)}={version}" for path, version in recorded
        )
        errors.append(f"Plugin version drift: {rendered}")
        return None

    for path in PORTFOLIO_METADATA_MANIFESTS:
        manifest_text = path.read_text(encoding="utf-8")
        for label in ("Portfolio Building", "Portfolio Analysis", "Portfolio Trading Analysis"):
            if label not in manifest_text:
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: metadata omits {label}")
        if "Staging Quandora" in manifest_text:
            errors.append(
                f"{path.relative_to(REPOSITORY_ROOT)}: use the canonical Quandora name"
            )
        if ('"keywords"' in manifest_text or '"tags"' in manifest_text) and (
            '"strategy-building"' not in manifest_text
        ):
            errors.append(
                f"{path.relative_to(REPOSITORY_ROOT)}: discovery metadata omits "
                "strategy-building"
            )

    codex = _load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    prompts = codex.get("interface", {}).get("defaultPrompt") if isinstance(codex, dict) else None
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append(
            "plugins/quandora/.codex-plugin/plugin.json: "
            "defaultPrompt must contain 1-3 production entry examples"
        )
    elif not all(isinstance(prompt, str) and prompt.strip() for prompt in prompts):
        errors.append("Codex defaultPrompt entries must be non-empty strings")
    else:
        for index, prompt in enumerate(prompts):
            if len(prompt) > MAX_CODEX_DEFAULT_PROMPT_CHARS:
                errors.append(
                    "plugins/quandora/.codex-plugin/plugin.json: "
                    f"defaultPrompt[{index}] exceeds the "
                    f"{MAX_CODEX_DEFAULT_PROMPT_CHARS}-character Codex limit"
                )

    return next(iter(distinct), None)


def _check_package_shape(errors: list[str]) -> None:
    for entry in REPOSITORY_ROOT.iterdir():
        if entry.name == ".git":
            continue
        if entry.name not in ALLOWED_REPOSITORY_ROOT_ENTRIES:
            errors.append(
                f"{entry.name}: undeclared repository-root package or maintainer entry"
            )

    for entry in PLUGIN_ROOT.iterdir():
        if entry.name not in ALLOWED_PLUGIN_ROOT_ENTRIES:
            errors.append(
                f"plugins/quandora/{entry.name}: undeclared public package entry"
            )

    plugin_scripts = PLUGIN_ROOT / "scripts"
    unsupported_script_entries = (
        sorted(
            path.name
            for path in plugin_scripts.iterdir()
            if path.is_symlink() or not path.is_file()
        )
        if plugin_scripts.is_dir()
        else []
    )
    if unsupported_script_entries:
        errors.append(
            "plugins/quandora/scripts: only regular files are allowed; "
            f"unsupported={unsupported_script_entries}"
        )
    actual_plugin_scripts = (
        {
            path.name
            for path in plugin_scripts.iterdir()
            if path.is_file() and not path.is_symlink()
        }
        if plugin_scripts.is_dir()
        else set()
    )
    if actual_plugin_scripts != PRODUCTION_SUPPORT_SCRIPTS:
        missing = sorted(PRODUCTION_SUPPORT_SCRIPTS - actual_plugin_scripts)
        unexpected = sorted(actual_plugin_scripts - PRODUCTION_SUPPORT_SCRIPTS)
        errors.append(
            "plugins/quandora/scripts: expected only the documented production "
            f"authorization launchers; missing={missing}, unexpected={unexpected}"
        )
    else:
        package_readmes = (
            REPOSITORY_ROOT / "README.md",
            PLUGIN_ROOT / "README.md",
        )
        for script_name in sorted(CLAUDE_PLUGIN_SUPPORT_SCRIPTS):
            script_path = plugin_scripts / script_name
            script_text = script_path.read_text(encoding="utf-8")
            if "plugin:quandora:quandora" not in script_text:
                errors.append(
                    f"{script_path.relative_to(REPOSITORY_ROOT)}: launcher must remain "
                    "bound to the plugin-managed production MCP identity"
                )
            for readme in package_readmes:
                if script_name not in readme.read_text(encoding="utf-8"):
                    errors.append(
                        f"{readme.relative_to(REPOSITORY_ROOT)}: documented Claude "
                        f"authorization bridge omits {script_name!r}"
                    )
        macos_launcher = plugin_scripts / "claude-mcp-login-macos.sh"
        if macos_launcher.stat().st_mode & 0o111 == 0:
            errors.append(
                "plugins/quandora/scripts/claude-mcp-login-macos.sh: "
                "launcher must remain executable"
            )

    for skill_dir in sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir()):
        for entry in skill_dir.iterdir():
            if entry.name not in ALLOWED_SKILL_ENTRIES:
                errors.append(
                    f"{entry.relative_to(REPOSITORY_ROOT)}: undeclared Skill package entry"
                )

        scripts_dir = skill_dir / "scripts"
        if scripts_dir.is_dir():
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            for script in sorted(path for path in scripts_dir.rglob("*") if path.is_file()):
                relative = script.relative_to(skill_dir).as_posix()
                if relative not in skill_text:
                    errors.append(
                        f"{script.relative_to(REPOSITORY_ROOT)}: Skill script is not routed "
                        "from SKILL.md"
                    )


def _skill_files(errors: list[str]) -> dict[str, Path]:
    files = {path.parent.name: path for path in SKILLS_ROOT.glob("*/SKILL.md")}
    missing = REQUIRED_SKILLS - set(files)
    if missing:
        errors.append(f"missing required production Skills: {sorted(missing)}")
    unexpected = set(files) - REQUIRED_SKILLS
    if unexpected:
        errors.append(f"unexpected production Skills: {sorted(unexpected)}")
    return files


def _check_skills(
    errors: list[str],
    skill_files: dict[str, Path],
) -> None:
    for skill_name, path in sorted(skill_files.items()):
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        if line_count > MAX_MAIN_SKILL_LINES:
            errors.append(
                f"{skill_name}/SKILL.md: {line_count} lines exceeds the "
                f"{MAX_MAIN_SKILL_LINES}-line progressive-disclosure limit"
            )
        if not text.startswith("---\n"):
            errors.append(f"{skill_name}/SKILL.md: missing YAML frontmatter")
        if f"name: {skill_name}\n" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: frontmatter name does not match directory")
        if "description:" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: missing frontmatter description")
        if "Use when" not in text[:1500] or "Do not use" not in text[:1500]:
            errors.append(
                f"{skill_name}/SKILL.md: description must state positive and negative triggers"
            )
        for marker in ROUTING_MARKERS.get(skill_name, ()):
            if marker not in text:
                errors.append(f"{skill_name}/SKILL.md: missing routing boundary {marker!r}")
        if any(pattern.search(text) for pattern in MANDATORY_VERSION_PROBE_PATTERNS):
            errors.append(
                f"{skill_name}/SKILL.md: version checks must remain explicit diagnostics, "
                "not a mandatory entry probe"
            )
        if "Use the user's language" not in text:
            errors.append(f"{skill_name}/SKILL.md: missing user-language output policy")

        agent_file = path.parent / "agents" / "openai.yaml"
        if not agent_file.is_file():
            errors.append(f"{skill_name}: missing agents/openai.yaml")
        else:
            agent_text = agent_file.read_text(encoding="utf-8")
            if f"${skill_name}" not in agent_text:
                errors.append(
                    f"{skill_name}/agents/openai.yaml: default prompt must name ${skill_name}"
                )
            if skill_name == "account-connection" and "dependencies:" in agent_text:
                errors.append("account-connection must load before MCP authentication")
            if skill_name != "account-connection" and 'value: "quandora"' not in agent_text:
                errors.append(
                    f"{skill_name}/agents/openai.yaml: missing Quandora MCP dependency"
                )
            for metadata_key in ("icon_small", "icon_large", "brand_color"):
                if f"  {metadata_key}:" not in agent_text:
                    errors.append(
                        f"{skill_name}/agents/openai.yaml: missing interface.{metadata_key}"
                    )
            for icon_path in re.findall(
                r'^\s+icon_(?:small|large):\s+"([^"]+)"$', agent_text, re.MULTILINE
            ):
                resolved_icon = (path.parent / icon_path).resolve()
                if not resolved_icon.is_file():
                    errors.append(
                        f"{skill_name}/agents/openai.yaml: icon does not exist: {icon_path!r}"
                    )

        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#")):
                continue
            local_target = (path.parent / target.split("#", 1)[0]).resolve()
            if not local_target.exists():
                errors.append(f"{skill_name}/SKILL.md: broken local reference {target!r}")

        reference_dir = path.parent / "references"
        if reference_dir.is_dir():
            linked = {
                (path.parent / target.split("#", 1)[0]).resolve()
                for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
                if not target.startswith(("http://", "https://", "#"))
            }
            for reference in reference_dir.glob("*.md"):
                if reference.resolve() not in linked:
                    errors.append(
                        f"{skill_name}/references/{reference.name}: supporting material is not "
                        "linked from its primary SKILL.md"
                    )

        if skill_name in SEARCH_DISCOVERY_SKILLS:
            support_text = text
            reference_dir = path.parent / "references"
            if reference_dir.is_dir():
                support_text += "\n" + "\n".join(
                    reference.read_text(encoding="utf-8")
                    for reference in sorted(reference_dir.glob("*.md"))
                )
            for marker in ("`query`", "`filters`", "byte-for-byte"):
                if marker not in support_text:
                    errors.append(
                        f"{skill_name}: search/pagination guidance is missing {marker!r}"
                    )

    all_tools = [
        tool for owned_tools in CANONICAL_TOOL_OWNERS.values() for tool in owned_tools
    ]
    if len(all_tools) != len(set(all_tools)):
        errors.append("canonical tool ownership map contains duplicate primary owners")
    for owner, owned_tools in CANONICAL_TOOL_OWNERS.items():
        owner_path = skill_files.get(owner)
        if owner_path is None:
            continue
        owner_text = owner_path.read_text(encoding="utf-8")
        for tool in sorted(owned_tools):
            if f"`{tool}`" not in owner_text:
                errors.append(f"{owner}/SKILL.md: missing primary tool ownership for {tool}")

    for skill_name, path in sorted(skill_files.items()):
        text = path.read_text(encoding="utf-8")
        for retired in sorted(RETIRED_TOOL_NAMES):
            if retired == "qd_plugin_ver" and path == PLUGIN_ROOT / "references/plugin-update.md":
                continue
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(retired)}(?![A-Za-z0-9_])", text):
                errors.append(f"{skill_name}/SKILL.md: retired tool name remains: {retired}")

        support_text = text
        reference_dir = path.parent / "references"
        if reference_dir.is_dir():
            support_text += "\n" + "\n".join(
                reference.read_text(encoding="utf-8")
                for reference in sorted(reference_dir.glob("*.md"))
            )
        normalized_support_text = " ".join(support_text.split())
        for marker in INTRADAY_CONTRACT_MARKERS.get(skill_name, ()):
            if " ".join(marker.split()) not in normalized_support_text:
                errors.append(
                    f"{skill_name}: missing Binance intraday contract boundary {marker!r}"
                )

    portfolio_path = skill_files.get("portfolio-building")
    if portfolio_path is not None:
        portfolio_text = portfolio_path.read_text(encoding="utf-8")
        for marker in PORTFOLIO_RESULT_METRIC_MARKERS:
            if marker not in portfolio_text:
                errors.append(
                    "portfolio-building/SKILL.md: missing canonical Portfolio result metric "
                    f"{marker!r}"
                )
        for marker in PORTFOLIO_SOURCE_EVIDENCE_MARKERS:
            if marker not in portfolio_text:
                errors.append(
                    "portfolio-building/SKILL.md: missing source-evidence workflow marker "
                    f"{marker!r}"
                )

    strategy_path = skill_files.get("strategy-building")
    if strategy_path is not None:
        ordinary_workflow = strategy_path.parent / "references" / "ordinary-strategy-workflow.md"
        ordinary_text = " ".join(
            ordinary_workflow.read_text(encoding="utf-8").split()
        )
        for marker in STRATEGY_CALLER_BOUNDARY_GUIDANCE_MARKERS:
            if marker not in ordinary_text:
                errors.append(
                    "strategy-building ordinary workflow: missing caller-boundary marker "
                    f"{marker!r}"
                )
        for marker in STRATEGY_SERVER_VALUE_GUIDANCE_MARKERS:
            if marker in ordinary_text:
                errors.append(
                    "strategy-building ordinary workflow: server-managed value leaked into "
                    f"Agent guidance via {marker!r}"
                )
        if "dates, cash, fee rates" in ordinary_text:
            errors.append(
                "strategy-building ordinary workflow: server-managed fields remain "
                "documented as caller fields"
            )

    paper_path = skill_files.get("portfolio-trading-analysis")
    if paper_path is not None:
        paper_text = " ".join(paper_path.read_text(encoding="utf-8").split())
        if (
            "Use each exact `source_strategy_run_id` with `get_paper_trade_source`"
            in paper_text
        ):
            errors.append(
                "portfolio-trading-analysis: Portfolio-local source selector is cross-wired into the "
                "ordinary canonical FM source tool"
            )
        for marker in (
            "`start_portfolio_trading_run`",
            "`portfolio.portfolio_id`",
            "`execution_enabled=false`",
            "`execution_status=not_configured`",
            "one-component Portfolio",
            "Internal command IDs are not public selectors.",
        ):
            if marker not in paper_text:
                errors.append(f"portfolio-trading-analysis: missing canonical Trading boundary {marker!r}")
        for retired in ("a Portfolio-local selector is not a canonical FM StrategyRun identifier",
                        "evaluation and Paper both inherit creation-time capital"):
            if retired in paper_text:
                errors.append(f"portfolio-trading-analysis: retired contract remains: {retired!r}")



def _check_runtime_markdown(errors: list[str], skill_files: dict[str, Path]) -> None:
    references = sorted(SKILLS_ROOT.glob("*/references/*.md")) + sorted((PLUGIN_ROOT / "references").glob("*.md"))
    paths = [
        REPOSITORY_ROOT / "README.md",
        PLUGIN_ROOT / "README.md",
        *skill_files.values(),
        *references,
    ]
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8")
        cjk_match = PUBLIC_PROSE_CJK.search(text)
        if cjk_match:
            line = text.count("\n", 0, cjk_match.start()) + 1
            errors.append(
                f"{path.relative_to(REPOSITORY_ROOT)}:{line}: public package prose "
                "must remain in consistent English"
            )
        for needle, meaning in FORBIDDEN_RUNTIME_MARKDOWN.items():
            if needle in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: contains {meaning}: {needle!r}"
                )
        for retired in sorted(RETIRED_TOOL_NAMES):
            if retired == "qd_plugin_ver" and path == PLUGIN_ROOT / "references/plugin-update.md":
                continue
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(retired)}(?![A-Za-z0-9_])", text):
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: retired tool name remains: {retired}"
                )

    for path, required_fragments in REQUIRED_RESULT_DESTINATIONS.items():
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: "
                    f"missing portable result-destination contract: {fragment!r}"
                )


SHARED_CONNECTION_POLICY = "../../references/connection-and-security.md"


def _check_research_workflows(errors: list[str], skill_files: dict[str, Path]) -> None:
    """Keep the executable prompt package's intent, evidence and access boundaries intact."""
    shared = PLUGIN_ROOT / "references/research-workflows.md"
    if not shared.is_file():
        errors.append("missing shared research intent/evidence contract")
        return
    for name, path in skill_files.items():
        if name == "account-connection":
            continue
        if "](../../references/research-workflows.md)" not in path.read_text(encoding="utf-8"):
            errors.append(f"{name}: missing shared research intent/evidence link")

    boundaries = {
        shared: (
            "Analysis-only is read-only",
            "For design-only requests, stop at the proposed definition",
            "Never silently change supplied",
            "Historical OOS is still a backtest",
            "Shared child research remains in its returned access context",
            "No dedicated guaranteed public projection",
            "local runtime, ZIP, notebook or export",
        ),
        PLUGIN_ROOT / "references/portfolio-neutrality.md": (
            "Positive constant scaling does not change correlation",
            "Sleeve equity shares can drift",
            "Do not present initial-weight estimates as realized full-run risk contributions",
        ),
        SKILLS_ROOT / "portfolio-building/references/selection-and-weighting.md": (
            "one to five distinct exact Strategies",
            "one-component Portfolio remains valid",
            "Initial weights can drift",
            "authorized additional experiment",
        ),
        SKILLS_ROOT / "portfolio-analysis/SKILL.md": (
            "This is read-only backtest diagnosis",
            "components[].strategy_run_id",
            "Do not substitute a better or newer member run",
            "Historical evidence supports improvement",
            "Insufficient evidence",
            "Analysis alone does not authorize an experiment or write",
        ),
        SKILLS_ROOT / "portfolio-analysis/references/evidence-contract.md": (
            "Without a supported same-window projection",
            "Clipped curves alone do not establish clipped fees or funding",
            "never fetch replacement prices",
        ),
        SKILLS_ROOT / "portfolio-trading-analysis/SKILL.md": (
            "For analysis-only requests, remain read-only",
            "## Real Live Is Read Only",
            "all other Live changes are frontend-only",
            "never create a replacement",
        ),
        SKILLS_ROOT / "portfolio-trading-analysis/references/forward-test-analysis.md": (
            "authoritative current net book",
            "Do not sum legacy member snapshots",
            "bounded recent records, not a full historical export",
            "Historical OOS remains a backtest",
            "separate validation segments",
            "does not authorize changing weights",
        ),
    }
    for path, markers in boundaries.items():
        if not path.is_file():
            errors.append(f"missing research workflow reference: {path.relative_to(REPOSITORY_ROOT)}")
            continue
        text = " ".join(path.read_text(encoding="utf-8").split())
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: missing research boundary {marker!r}")

    # Supporting references and metadata must be migrated too, not just the primary SKILL files.
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        for retired in ("strategy-portfolio", "paper-trading"):
            if retired in text:
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: retired Skill entry {retired!r}")
        for name in re.findall(r"\$([a-z]+(?:-[a-z]+)+)", text):
            if name not in skill_files:
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: unknown Skill handoff ${name}")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#")):
                    continue
                if not (path.parent / target.split("#", 1)[0]).resolve().exists():
                    errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: broken supporting reference {target!r}")


def _check_connection_policy(errors: list[str], skill_files: dict[str, Path]) -> None:
    policy = PLUGIN_ROOT / "references/connection-and-security.md"
    if not policy.is_file():
        errors.append("missing shared connection recovery policy")
        return
    for name, path in skill_files.items():
        if f"]({SHARED_CONNECTION_POLICY})" not in path.read_text(encoding="utf-8"):
            errors.append(f"{name}: missing shared connection recovery policy link")
    text = " ".join(policy.read_text(encoding="utf-8").split())
    for marker in (
        "automatic token refresh first", "retry an affected read once",
        "first inspect the existing operation/status", "original idempotency key",
        "terminal authorization failure", "Respect cancellation and security denials",
        "Do not display token lifetimes", "same installed package",
        "A failed check is nonblocking", "without guessing",
        "Preserve explicit version pins", "existing update authorization",
    ):
        if marker not in text.replace("**", ""):
            errors.append(f"shared connection policy: missing recovery boundary {marker!r}")
    codex_recovery = PLUGIN_ROOT / "references/codex-authorization-recovery.md"
    if "](codex-authorization-recovery.md)" not in policy.read_text(encoding="utf-8"):
        errors.append("shared connection policy: missing Codex authorization recovery link")
    if not codex_recovery.is_file():
        errors.append("missing bundled Codex authorization recovery guide")
    else:
        recovery_text = " ".join(codex_recovery.read_text(encoding="utf-8").split())
        for marker in (
            "`plugin_not_found`", "not an authorization denial",
            "same desktop host and configuration context",
            "Do not assume a global `codex` executable shares the desktop configuration",
            "codex --version", "codex mcp get quandora --json", "codex mcp login --help",
            "enabled", "Streamable HTTP", "https://mcp.quandora.ai/quant",
            "codex mcp login quandora", "one foreground native OAuth flow",
            "Do not ask the user to paste a recovery prompt or run the command",
            "Respect a security denial; never try another execution path to bypass it",
            "Only the user approves additional access",
            "Do not repeat login when the callback succeeds but the grant remains unchanged",
            "`list_strategy_folders`", "`list_strategies`", "`list_portfolio_folders`",
            "`list_portfolios`", "Do not use a fixed tool count",
            "Do not create a Portfolio or submit a backtest as a recovery probe",
        ):
            if marker not in recovery_text:
                errors.append(f"Codex authorization recovery: missing boundary {marker!r}")
    guide = PLUGIN_ROOT / "references/plugin-update.md"
    if not guide.is_file():
        errors.append("missing bundled plugin update guide")
    else:
        guide_text = guide.read_text()
        for command in ("codex plugin marketplace upgrade quandora",
                        "codex plugin add quandora@quandora --json",
                        "claude plugin marketplace update quandora",
                        "claude plugin update quandora@quandora"):
            if command not in guide_text:
                errors.append("update guide missing host-managed refresh/update command")
    paths = [REPOSITORY_ROOT / "README.md", *PLUGIN_ROOT.rglob("*.md")]
    for path in paths:
        text = " ".join(path.read_text(encoding="utf-8").split())
        if re.search(r"(?:create_\w+_result_bundle_download|read_\w+_result_bundle_chunk)", text):
            errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: use the unified Result Bundle export tool")
        for pattern, reason in (
            (r"update or reinstall", "premature reinstall guidance"),
            (r"(?:access )?token is valid for", "user-facing token lifetime boilerplate"),
            (r"Refresh the Quandora MCP connection", "user-facing refresh prompt"),
            (r"before every business call.*check_quandora_plugin_version",
             "repeated blocking version probe"),
        ):
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: {reason}")
        if path.name == "SKILL.md" or path == policy:
            if re.search(r"`\d+\.\d+(?:\.\d+)?-[\w.]+`", text) or any(
                re.search(r"(?:installed_version|plugin version|release label)", line, re.I)
                and re.search(r"`\d+\.\d+(?:\.\d+)?`", line)
                for line in path.read_text(encoding="utf-8").splitlines()
            ):
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: hardcoded release label")



def _check_production_delivery(errors: list[str]) -> None:
    expected_url = "https://mcp.quandora.ai/quant"
    for filename in (".mcp.json", "mcp.json"):
        document = _load_json(PLUGIN_ROOT / filename)
        servers = document.get("mcpServers", document)
        if set(servers) != {"quandora"}:
            errors.append(f"{filename}: production MCP identity mismatch")
        server = servers.get("quandora", {})
        if server.get("url") != expected_url or server.get("oauth_resource", expected_url) != expected_url:
            errors.append(f"{filename}: production MCP endpoint mismatch")
    kimi = _load_json(REPOSITORY_ROOT / "kimi.plugin.json")
    if kimi.get("mcpServers", {}).get("quandora", {}).get("url") != expected_url:
        errors.append("Kimi production MCP endpoint mismatch")
    for path in DIRECT_VERSION_MANIFESTS:
        if _load_json(path).get("name") != "quandora":
            errors.append(f"{path.name}: production plugin identity mismatch")
    for path in PLUGIN_ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".yaml", ".json", ".sh", ".ps1", ".js"}:
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in ("quandora-staging", "mcp-staging.", "quandora-plugins-staging")):
                errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: staging identity leaked into production")
    scripts = PLUGIN_ROOT / "scripts"
    bootstrap = scripts / "workbuddy-cn-bootstrap-macos.sh"
    source = bootstrap.read_text(encoding="utf-8")
    for variable, filename in (("INSTALLER_SHA256", "workbuddy-cn-install-macos.js"), ("OAUTH_SHA256", "workbuddy-cn-oauth-macos.js")):
        digest = hashlib.sha256((scripts / filename).read_bytes()).hexdigest()
        if f"{variable}='{digest}'" not in source:
            errors.append(f"WorkBuddy component integrity mismatch: {filename}")
    guide = (REPOSITORY_ROOT / "agent-install-guide/workbuddy-cn.md").read_text(encoding="utf-8")
    if hashlib.sha256(bootstrap.read_bytes()).hexdigest() not in guide:
        errors.append("WorkBuddy bootstrap guide integrity mismatch")
    installer = (scripts / "workbuddy-cn-install-macos.js").read_text(encoding="utf-8")
    declared = re.search(r"const EXPECTED_SKILLS = (\[.*?\]);", installer, re.DOTALL)
    if not declared or set(re.findall(r'"([^"\n]+)"', declared.group(1))) != REQUIRED_SKILLS:
        errors.append("WorkBuddy expected Skill set differs from package")
    for filename in ("workbuddy-cn-install-macos.js", "workbuddy-cn-oauth-macos.js"):
        if "get_factor_mining_status" not in (scripts / filename).read_text(encoding="utf-8"):
            errors.append("WorkBuddy protected probe must use canonical status tool")


def main() -> int:
    errors: list[str] = []
    try:
        package_version = _check_manifests(errors)
        _check_production_delivery(errors)
        _check_package_shape(errors)
        skills = _skill_files(errors)
        _check_skills(errors, skills)
        _check_runtime_markdown(errors, skills)
        _check_connection_policy(errors, skills)
        _check_research_workflows(errors, skills)
    except ValueError as exc:
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Quandora package checks passed for version {package_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
