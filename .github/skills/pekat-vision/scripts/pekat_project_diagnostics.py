"""Read-only PEKAT project diagnostics; no DB/model deserialization or writes."""
from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import subprocess
from pathlib import Path
from typing import Any, Iterable

from analyze_pekat_log import analyze_log_target

PACKAGE_MAX_BYTES = 1024 * 1024
PROJECT_DIRS = (
    "database", "database_old", "logs", "models", "images", "cache",
    "classifier", "detector", "supervised", "unsupervised",
)


def _load_package(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.is_file():
        return {}, "pekat_package.json not found"
    if path.stat().st_size > PACKAGE_MAX_BYTES:
        return {}, "pekat_package.json exceeds 1 MiB limit"
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, f"invalid pekat_package.json: {exc}"
    return (value, None) if isinstance(value, dict) else ({}, "pekat_package.json root is not an object")


def _scalar(value: Any) -> Any:
    return value if value is None or isinstance(value, (str, int, float, bool)) else None


def _port(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if 1 <= result <= 65535 else None


def _runtime_processes(project: Path) -> dict[str, Any]:
    if os.name != "nt":
        return {"status": "unsupported_on_this_os", "matches": []}
    script = (
        "Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
    )
    try:
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            check=False, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": f"process_query_failed: {exc}", "matches": []}
    if completed.returncode != 0:
        return {"status": "process_query_failed", "matches": [], "error": completed.stderr.strip()[:500]}
    try:
        payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        return {"status": f"process_query_invalid_json: {exc}", "matches": []}
    rows = payload if isinstance(payload, list) else [payload]
    needle = str(project).casefold()
    matches = []
    for row in rows:
        if not isinstance(row, dict) or needle not in str(row.get("CommandLine") or "").casefold():
            continue
        matches.append({"pid": row.get("ProcessId"), "name": row.get("Name"), "command_line_contains_project": True})
    return {"status": "checked", "matches": matches}


def _port_listening(port: int | None, timeout_s: float = 0.4) -> str:
    if port is None:
        return "not_checked_no_valid_port"
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout_s):
            return "reachable"
    except (OSError, TimeoutError):
        return "not_reachable"


def _http_head(port: int | None, timeout_s: float = 1.0) -> dict[str, Any]:
    if port is None:
        return {"status": "not_checked_no_valid_port"}
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout_s)
    try:
        connection.request("HEAD", "/")
        response = connection.getresponse()
        response.read(1024)
        return {"status": "response", "http_status": response.status, "content_type": response.getheader("Content-Type")}
    except OSError as exc:
        return {"status": "unreachable", "error": str(exc)}
    finally:
        connection.close()


def diagnose_project(
    project: Path, *, runtime: bool = False, probe_http: bool = False, include_flow: bool = False
) -> dict[str, Any]:
    project = project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    package, package_error = _load_package(project / "pekat_package.json")
    version = _scalar(package.get("version") if "version" in package else package.get("pekatVersion"))
    port = _port(package.get("port"))
    filesystem = {name: (project / name).is_dir() for name in PROJECT_DIRS}
    logs_dir = project / "logs"
    log_files = sorted(
        (path for path in logs_dir.glob("output.log*") if path.is_file()),
        key=lambda path: (path.stat().st_mtime_ns, path.name), reverse=True,
    ) if logs_dir.is_dir() else []
    logs: dict[str, Any] = {
        "present": filesystem["logs"],
        "count": len(log_files),
        "newest": str(log_files[0].relative_to(project)) if log_files else None,
    }
    if log_files:
        try:
            summary = analyze_log_target(log_files[0], max_families=3)
            logs["recent_range"] = summary["range"]
            logs["recent_error_records"] = summary["error_records"]
            logs["first_root_cause_candidates"] = summary["first_root_cause_candidates"]
        except ValueError as exc:
            logs["analysis_error"] = str(exc)
    camera_files = sorted(
        path for pattern in ("config-*.yaml", "*_extended_config.yaml", "basler-*")
        for path in project.glob(pattern) if path.is_file()
    )
    result: dict[str, Any] = {
        "project": {
            "path": str(project),
            "name": _scalar(package.get("name")) or project.name,
            "version": version,
            "configured_port": port,
            "gpu_index": _scalar(package.get("gpuIndex")),
            "cpu_index": _scalar(package.get("cpuIndex")),
            "created_at": _scalar(package.get("createdAt")),
            "last_open": _scalar(package.get("lastOpen")),
            "auto_start": _scalar(package.get("autoStart")),
            "package_error": package_error,
        },
        "filesystem": {
            **filesystem,
            "running_db_present": (project / "database" / "running.db").is_file(),
            "running_db_interpretation": "state_file_only_not_process_liveness",
        },
        "camera": {
            "stored_configuration_files": [
                {"path": str(path.relative_to(project)), "bytes": path.stat().st_size} for path in camera_files
            ],
            "runtime_state": "not_inferred_from_stored_configuration",
        },
        "logs": logs,
        "runtime": {
            "requested": runtime,
            "processes": _runtime_processes(project) if runtime else {"status": "not_requested", "matches": []},
            "configured_port": _port_listening(port) if runtime else "not_requested",
            "http_root": _http_head(port) if probe_http else {"status": "not_requested"},
            "state_rule": "server_running != camera_connected != camera_initialized != camera_acquiring != flow_evaluating",
        },
        "flow": {"status": "not_requested", "helper": "analyze_flow_database.py"},
        "read_only": True,
    }
    if include_flow:
        from analyze_flow_database import analyze_project
        result["flow"] = {"status": "analyzed_with_existing_safe_helper", "report": analyze_project(project)}
    return result


def render(report: dict[str, Any]) -> str:
    project = report["project"]
    fs = report["filesystem"]
    runtime = report["runtime"]
    lines = [
        "PROJECT",
        f"  name: {project['name']}",
        f"  version: {project['version'] or 'unknown'}",
        f"  configured port: {project['configured_port'] or 'unknown'}",
        f"  GPU/CPU: {project['gpu_index']!r}/{project['cpu_index']!r}",
        "FILESYSTEM",
        f"  database/logs/images/cache: {fs['database']}/{fs['logs']}/{fs['images']}/{fs['cache']}",
        f"  database_old: {fs['database_old']}",
        f"  running.db: {fs['running_db_present']} (state file only; not proof of a live process)",
        "RUNTIME",
        f"  process query: {runtime['processes']['status']}",
        f"  matching processes: {len(runtime['processes']['matches'])}",
        f"  configured port: {runtime['configured_port']}",
        f"  HTTP root: {runtime['http_root']['status']}",
        "CAMERA",
        f"  stored config files: {len(report['camera']['stored_configuration_files'])}",
        "LOGS",
        f"  files/newest: {report['logs']['count']}/{report['logs']['newest'] or 'none'}",
    ]
    for row in report["logs"].get("first_root_cause_candidates", [])[:3]:
        lines.append(f"  {row['first_timestamp']} {row['category']}: {row['message']}")
    lines.extend([
        "FLOW",
        f"  {report['flow']['status']}; reuse {report['flow'].get('helper', 'existing analyzer')}",
        "STATE BOUNDARY",
        f"  {runtime['state_rule']}",
    ])
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a PEKAT project directory without modifying it.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--runtime", action="store_true", help="read process command lines and test the configured local TCP port")
    parser.add_argument("--probe-http", action="store_true", help="send one explicit HEAD / probe to the configured localhost port")
    parser.add_argument("--flow", action="store_true", help="reuse the bundled safe FLOW/database analyzer")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.probe_http and not args.runtime:
        parser.error("--probe-http requires --runtime so the extra live check is explicit")
    report = diagnose_project(args.project, runtime=args.runtime, probe_http=args.probe_http, include_flow=args.flow)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
