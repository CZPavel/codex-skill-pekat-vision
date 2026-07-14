"""Pure helpers for mocked industrial I/O with fail-closed write gating."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


def decode_u16_be(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise ValueError("device buffer is too short")
    return int.from_bytes(data[offset : offset + 2], "big", signed=False)


def extract_bits(value: int, *, bit_offset: int, bit_length: int) -> int:
    if value < 0 or bit_offset < 0 or bit_length <= 0:
        raise ValueError("value and bit range must be non-negative")
    return (value >> bit_offset) & ((1 << bit_length) - 1)


def guarded_write(
    writer: Callable[..., Any],
    *args: Any,
    dry_run: bool = True,
    approved: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Do not call writer unless both dry-run is disabled and approval is explicit."""
    if dry_run:
        return {"executed": False, "reason": "dry_run"}
    if not approved:
        raise PermissionError("industrial write requires explicit approval")
    return {"executed": True, "result": writer(*args, **kwargs)}
