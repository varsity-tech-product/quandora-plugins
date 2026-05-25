import json
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


DEFAULT_HOME = Path.home() / ".factor-mining-agent"
DEFAULT_BASE_URL = "https://d25q1jf66e8y4g.cloudfront.net"
HOME_ENV = "FACTOR_MINING_AGENT_HOME"


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentConfig:
    base_url: str
    api_key: str
    agent_status: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AgentConfig":
        try:
            base_url = str(payload["base_url"]).rstrip("/")
            api_key = str(payload["api_key"])
        except KeyError as exc:
            raise ConfigError(f"Missing config field: {exc.args[0]}") from exc
        return cls(base_url=base_url, api_key=api_key, agent_status=payload.get("agent_status") or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url.rstrip("/"),
            "api_key": self.api_key,
            "agent_status": dict(self.agent_status),
        }


def agent_home(home: str | Path | None = None, env: Mapping[str, str] | None = None) -> Path:
    if home is not None:
        return Path(home).expanduser()
    env = env if env is not None else os.environ
    if env.get(HOME_ENV):
        return Path(env[HOME_ENV]).expanduser()
    return DEFAULT_HOME


def config_path(home: str | Path | None = None) -> Path:
    return agent_home(home) / "config.json"


def ensure_agent_home(home: str | Path | None = None) -> Path:
    root = agent_home(home)
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, stat.S_IRWXU)
    except OSError:
        pass
    return root


def _write_private_json(path: Path, payload: Mapping[str, Any]) -> None:
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
    finally:
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass


def save_config(config: AgentConfig, home: str | Path | None = None) -> Path:
    root = ensure_agent_home(home)
    path = root / "config.json"
    _write_private_json(path, config.to_dict())
    return path


def load_config(home: str | Path | None = None) -> AgentConfig:
    path = config_path(home)
    if not path.exists():
        raise ConfigError(f"Missing Factor Mining config at {path}. Run setup first.")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return AgentConfig.from_dict(payload)
