import json
import re
from typing import Any, Iterable


FACTOR_KEY_RE = re.compile(r"vt_[A-Za-z0-9_-]{8,}")


def redact_secret(secret: str | None) -> str:
    if not secret:
        return ""
    if len(secret) <= 8:
        return "***"
    if secret.startswith("vt_"):
        return f"vt_...{secret[-4:]}"
    return f"***{secret[-4:]}"


def redact_text(text: str, extra_secrets: Iterable[str] | None = None) -> str:
    redacted = text
    for secret in extra_secrets or []:
        if secret:
            redacted = redacted.replace(secret, redact_secret(secret))
    return FACTOR_KEY_RE.sub(lambda match: redact_secret(match.group(0)), redacted)


def redact_obj(value: Any, extra_secrets: Iterable[str] | None = None) -> Any:
    if isinstance(value, str):
        return redact_text(value, extra_secrets=extra_secrets)
    if isinstance(value, list):
        return [redact_obj(item, extra_secrets=extra_secrets) for item in value]
    if isinstance(value, tuple):
        return [redact_obj(item, extra_secrets=extra_secrets) for item in value]
    if isinstance(value, dict):
        return {key: redact_obj(item, extra_secrets=extra_secrets) for key, item in value.items()}
    return value


def dumps_redacted(value: Any, extra_secrets: Iterable[str] | None = None) -> str:
    return json.dumps(redact_obj(value, extra_secrets=extra_secrets), separators=(",", ":"), sort_keys=True)
