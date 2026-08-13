"""Small PEKAT Form runtime normalization helpers.

PEKAT 4.0.1 evidence shows that untouched number/select defaults can have a
different representation from values edited in the UI.  Normalize only when
the calculation depends on type; do not mutate the runtime Form mapping.
"""
from __future__ import annotations

from typing import Any, Sequence


def number(values: dict[str, Any], key: str, default: Any, minimum: float, maximum: float) -> float:
    raw = values.get(key, default)
    if isinstance(raw, bool):
        raise ValueError(f"{key} must be numeric")
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be numeric") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{key} outside range {minimum}..{maximum}")
    return value


def boolean(values: dict[str, Any], key: str, default: bool = False) -> bool:
    raw = values.get(key, default)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off", ""}:
            return False
    raise ValueError(f"{key} must be boolean")


def choice(values: dict[str, Any], key: str, default: Any, choices: Sequence[str]) -> str:
    if not choices:
        raise ValueError("choices must not be empty")
    raw = values.get(key, default)
    if isinstance(raw, bool):
        raise ValueError(f"unsupported {key}: {raw!r}")
    if isinstance(raw, int):
        index = raw
    else:
        value = str(raw).strip()
        if value in choices:
            return value
        if not value.isdigit():
            raise ValueError(f"unsupported {key}: {raw!r}")
        index = int(value)
    if not 0 <= index < len(choices):
        raise ValueError(f"unsupported {key} index: {index}")
    return choices[index]
