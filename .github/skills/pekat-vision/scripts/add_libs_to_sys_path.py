"""Add an explicitly configured staged library directory to sys.path."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def add_lib_dir(path_value: str) -> Path:
    path = Path(path_value).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"library directory does not exist: {path}")
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)
    return path


def main(context: dict[str, Any], form: dict[str, Any] | None = None) -> None:
    values = form or {}
    path_value = values.get("library_path")
    if not path_value:
        context["external_library_status"] = "library_path_not_configured"
        return
    try:
        path = add_lib_dir(str(path_value))
    except ValueError as exc:
        context["external_library_status"] = f"invalid_path: {exc}"
        return
    context["external_library_status"] = f"path_added: {path}"
