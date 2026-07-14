"""Read-only PEKAT Python ABI and distribution fingerprint for Windows."""
from __future__ import annotations

import json
import platform
import re
from pathlib import Path
from typing import Any


def fingerprint_installation(installation: Path, version: str) -> dict[str, Any]:
    installation = installation.resolve()
    if not installation.is_dir():
        raise ValueError(f"PEKAT installation does not exist: {installation}")
    dlls = sorted(installation.rglob("python3*.dll"))
    abi = "not_detected"
    for dll in dlls:
        match = re.search(r"python(\d)(\d+)\.dll$", dll.name.lower())
        if match:
            abi = f"cp{match.group(1)}{match.group(2)}"
            break
    packages: dict[str, str] = {}
    for dist in installation.rglob("*.dist-info"):
        match = re.match(r"(.+?)-(\d[^/]*)\.dist-info$", dist.name, re.IGNORECASE)
        if match:
            packages[match.group(1).replace("_", "-").lower()] = match.group(2)
    return {
        "version": version,
        "path": str(installation),
        "architecture": platform.machine(),
        "python_abi": abi,
        "python_dlls": [str(path.relative_to(installation)) for path in dlls],
        "packages": dict(sorted(packages.items())),
        "probe_mode": "read_only_filesystem",
    }


def discover() -> list[dict[str, Any]]:
    results = []
    for version in ("3.19.3", "4.0.1"):
        for base in (Path(r"C:\Program Files"), Path(r"C:\Program Files (x86)")):
            candidate = base / f"PEKAT VISION {version}"
            if candidate.is_dir():
                results.append(fingerprint_installation(candidate, version))
    return results


if __name__ == "__main__":
    print(json.dumps({"installations": discover()}, ensure_ascii=False, indent=2))
