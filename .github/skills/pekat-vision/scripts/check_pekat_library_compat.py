"""Check known PEKAT Code library state and wheel tags without installing anything."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

DATA = Path(__file__).resolve().parents[1] / "references" / "data" / "pekat401_code_libraries.json"
WHEEL = re.compile(r"^(?P<base>.+)-(?P<python>[^-]+)-(?P<abi>[^-]+)-(?P<platform>[^-]+)\.whl$", re.IGNORECASE)


def load_matrix() -> dict[str, Any]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def find_package(matrix: dict[str, Any], name: str) -> dict[str, Any] | None:
    needle = normalize_name(name)
    for item in matrix["packages"]:
        if needle in {normalize_name(item["library"]), normalize_name(item["import_name"])}:
            return item
    return None


def check_wheel(filename: str, *, python_abi: str = "cp312", platform: str = "win_amd64") -> dict[str, Any]:
    name = Path(filename).name
    match = WHEEL.match(name)
    if not match:
        return {"status": "UNKNOWN_TEST_REQUIRED", "wheel": name, "reason": "wheel filename tags could not be parsed"}
    tags = match.groupdict()
    py_tags = set(tags["python"].lower().split("."))
    abi_tags = set(tags["abi"].lower().split("."))
    platform_tags = set(tags["platform"].lower().split("."))
    if platform_tags == {"any"} and abi_tags == {"none"} and any(tag.startswith("py3") for tag in py_tags):
        return {
            "status": "LIKELY_COMPATIBLE", "wheel": name,
            "reason": "pure-Python candidate; dependencies still require Python 3.12 compatibility and a Code import test",
            "tags": tags,
        }
    if platform not in platform_tags:
        return {"status": "WRONG_ARCH", "wheel": name, "reason": f"expected {platform}, found {tags['platform']}", "tags": tags}
    if python_abi not in py_tags:
        return {"status": "WRONG_ABI", "wheel": name, "reason": f"expected Python tag {python_abi}, found {tags['python']}", "tags": tags}
    if python_abi not in abi_tags and "abi3" not in abi_tags:
        return {"status": "WRONG_ABI", "wheel": name, "reason": f"expected ABI {python_abi} or abi3, found {tags['abi']}", "tags": tags}
    return {
        "status": "COMPATIBLE_TAGS", "wheel": name,
        "reason": "wheel tags match cp312/win_amd64; dependencies, native DLLs and direct Code import/function still require verification",
        "tags": tags,
    }


def check(pekat_version: str, package: str | None = None, wheel: str | None = None) -> dict[str, Any]:
    matrix = load_matrix()
    result: dict[str, Any] = {
        "pekat_version": pekat_version,
        "matrix_applied": pekat_version == "4.0.1",
        "read_only": True,
    }
    if pekat_version != "4.0.1":
        result["status"] = "UNKNOWN_TEST_REQUIRED"
        result["reason"] = "the bundled library matrix is scoped only to the tested PEKAT 4.0.1 runtime"
        if wheel:
            result["wheel"] = {"status": "UNKNOWN_TEST_REQUIRED", "reason": "fingerprint the target version ABI before checking this wheel"}
        return result
    result["runtime"] = matrix["python"]
    if package:
        item = find_package(matrix, package)
        result["package"] = item or {"library": package, "status": "unknown", "version": "unknown"}
    if wheel:
        result["wheel"] = check_wheel(wheel)
    if wheel and result["wheel"]["status"] in {"WRONG_ABI", "WRONG_ARCH"}:
        result["status"] = result["wheel"]["status"]
    elif package and result["package"]["status"] == "functionally_verified":
        result["status"] = "RUNTIME_VERIFIED_ON_TESTED_INSTALLATION"
    elif package and result["package"]["status"] == "import_verified":
        result["status"] = "IMPORT_VERIFIED_ON_TESTED_INSTALLATION"
    elif package and result["package"]["status"] == "present_import_failed":
        result["status"] = "NOT_USABLE_IMPORT_FAILED"
    elif package and result["package"]["status"] == "unavailable":
        result["status"] = "NOT_AVAILABLE_ON_TESTED_INSTALLATION"
    elif wheel:
        result["status"] = result["wheel"]["status"]
    else:
        result["status"] = "UNKNOWN_TEST_REQUIRED"
    return result


def render(report: dict[str, Any]) -> str:
    lines = [report["status"], f"PEKAT: {report['pekat_version']}"]
    if "runtime" in report:
        runtime = report["runtime"]
        lines.append(f"Runtime: CPython {runtime['version']} / {runtime['abi']} / {runtime['wheel_platform']}")
    if "package" in report:
        item = report["package"]
        lines.append(f"Package: {item['library']} ({item.get('import_name', 'unknown')}) {item.get('version', 'unknown')} — {item['status']}")
        if item.get("notes"):
            lines.append(f"Boundary: {item['notes']}")
    if "wheel" in report:
        lines.append(f"Wheel: {report['wheel']['status']} — {report['wheel']['reason']}")
    lines.append("Success gate: import inside PEKAT Code, preferably followed by one minimal functional call.")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check PEKAT Code library evidence and wheel tags; never install packages.")
    parser.add_argument("--pekat-version", required=True)
    parser.add_argument("--package")
    parser.add_argument("--wheel")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.package and not args.wheel:
        parser.error("provide --package and/or --wheel")
    report = check(args.pekat_version, args.package, args.wheel)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
