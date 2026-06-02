import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_METADATA = ("FACTOR_TYPE", "FACTOR_NAME", "FACTOR_DEFAULT_PARAMS")


class MetadataError(RuntimeError):
    pass


@dataclass(frozen=True)
class PluginMetadata:
    factor_type: str
    factor_name: str
    params: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor_type": self.factor_type,
            "factor_name": self.factor_name,
            "params": self.params,
        }


def _assignment_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _literal_value(name: str, value_node: ast.AST) -> Any:
    try:
        return ast.literal_eval(value_node)
    except (ValueError, TypeError, SyntaxError) as exc:
        raise MetadataError(f"{name} must be a static literal value") from exc


def parse_plugin_metadata(plugin_path: str | Path) -> PluginMetadata:
    path = Path(plugin_path)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MetadataError(f"Cannot read plugin.py: {exc}") from exc

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise MetadataError(f"Cannot parse plugin.py: {exc}") from exc

    values: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                name = _assignment_name(target)
                if name in REQUIRED_METADATA:
                    values[name] = _literal_value(name, node.value)
        elif isinstance(node, ast.AnnAssign):
            name = _assignment_name(node.target)
            if name in REQUIRED_METADATA and node.value is not None:
                values[name] = _literal_value(name, node.value)

    missing = [name for name in REQUIRED_METADATA if name not in values]
    if missing:
        raise MetadataError(f"Missing required plugin metadata: {', '.join(missing)}")

    factor_type = values["FACTOR_TYPE"]
    factor_name = values["FACTOR_NAME"]
    params = values["FACTOR_DEFAULT_PARAMS"]
    if not isinstance(factor_type, str) or not factor_type.strip():
        raise MetadataError("FACTOR_TYPE must be a non-empty string")
    if not isinstance(factor_name, str) or not factor_name.strip():
        raise MetadataError("FACTOR_NAME must be a non-empty string")
    if not isinstance(params, dict):
        raise MetadataError("FACTOR_DEFAULT_PARAMS must be a static dict")

    return PluginMetadata(factor_type=factor_type, factor_name=factor_name, params=params)
