import json
import os
import re
import stat
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import agent_home, ensure_agent_home


CLIENT_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


class RunStateError(RuntimeError):
    pass


@dataclass(frozen=True)
class RunState:
    client_run_id: str
    session_id: str | None = None
    plugin_id: str | None = None
    job_ids: list[str] = field(default_factory=list)
    plugin_path: str | None = None
    workflow_stage: str | None = None
    artifact_paths: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunState":
        return cls(
            client_run_id=str(payload["client_run_id"]),
            session_id=payload.get("session_id"),
            plugin_id=payload.get("plugin_id"),
            job_ids=list(payload.get("job_ids") or []),
            plugin_path=payload.get("plugin_path"),
            workflow_stage=payload.get("workflow_stage"),
            artifact_paths=dict(payload.get("artifact_paths") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_client_run_id(client_run_id: str) -> None:
    if not CLIENT_RUN_ID_RE.match(client_run_id):
        raise RunStateError("client_run_id may contain only letters, numbers, '.', '_', and '-'")


def runs_dir(home: str | Path | None = None) -> Path:
    root = ensure_agent_home(home)
    path = root / "runs"
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, stat.S_IRWXU)
    except OSError:
        pass
    return path


def run_state_path(client_run_id: str, home: str | Path | None = None) -> Path:
    _validate_client_run_id(client_run_id)
    return agent_home(home) / "runs" / f"{client_run_id}.json"


def save_run_state(state: RunState, home: str | Path | None = None) -> Path:
    _validate_client_run_id(state.client_run_id)
    path = runs_dir(home) / f"{state.client_run_id}.json"
    data = json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
    finally:
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
    return path


def load_run_state(client_run_id: str, home: str | Path | None = None) -> RunState:
    path = run_state_path(client_run_id, home)
    if not path.exists():
        raise RunStateError(f"No run state found for client_run_id {client_run_id}")
    with path.open("r", encoding="utf-8") as handle:
        return RunState.from_dict(json.load(handle))
