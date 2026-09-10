"""Bounded, read-only PEKAT log parsing and incident forensics."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

HEADER = re.compile(
    r"^(?P<component>.+?)\s+-\s+(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:[.,]\d+)?)"
    r"\s+-\s+(?P<logger>.+?)\s+-\s+(?P<severity>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+-\s+(?P<message>.*)$"
)
TERMINAL_EXCEPTION = re.compile(r"^(?P<type>[A-Za-z_][\w.]*(?:Error|Exception|Warning))(?::\s*(?P<message>.*))?$")
SESSION_START = re.compile(r"(?i)\b(project server|server startup|starting (?:project|server)|application startup)\b")
WINDOWS_PATH = re.compile(r"(?i)(?:[a-z]:\\|\\\\)[^\r\n\t\"']+")
POSIX_PATH = re.compile(r"(?<!\w)/(?:[^\s/:]+/)+[^\s:;,]+")
TOKEN = re.compile(r"(?i)\b(?P<key>token|password|secret|api[_-]?key)\s*[:=]\s*(?P<value>[^\s,;]+)")
UUID = re.compile(r"(?i)\b[0-9a-f]{8}-[0-9a-f-]{27,}\b")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
IDENTITIES = {
    "module_ids": re.compile(r"(?i)\bmodule(?:id)?\s*[:=#]?\s*(\d+)\b"),
    "model_ids": re.compile(r"(?i)\bmodel(?:id)?\s*[:=#]?\s*(\d+)\b"),
    "ports": re.compile(r"(?i)\bport\s*[:=#]?\s*(\d{2,5})\b"),
    "pids": re.compile(r"(?i)\bpid\s*[:=#]?\s*(\d+)\b"),
}
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024

CATEGORY_PATTERNS = {
    "camera": ("camera", "genicam", "grab", "acquisition", "no camera connections", "camera search"),
    "model": ("model not loaded", "loading model", "inference", "classifier model", "detector model"),
    "filesystem": ("image saver", "root folder", "does not exist", "permission denied", "invalid path"),
    "code_flow": ("error analyzing image", "traceback", "sourcecode", "code module", "flow", "syntaxerror"),
    "network": ("connection refused", "connection reset", "timed out", "timeout", "http error", "socket"),
    "project_start": ("project server", "server startup", "address already in use", "startup failed"),
    "folder_source": ("started monitoring folder", "folder watcher", "watcher"),
}
SECONDARY_PATTERNS = ("camera is not initialized", "no grab result", "grab error", "model is not loaded yet")


@dataclass(frozen=True)
class Record:
    path: str
    line: int
    component: str
    timestamp: str
    logger: str
    severity: str
    message: str
    continuation: tuple[str, ...]

    @property
    def full_text(self) -> str:
        return "\n".join((self.message, *self.continuation)).strip()


def sanitize_text(value: str) -> str:
    value = TOKEN.sub(lambda match: f"{match.group('key')}=<redacted>", value)
    value = WINDOWS_PATH.sub("<path>", value)
    value = POSIX_PATH.sub("<path>", value)
    value = UUID.sub("<uuid>", value)
    return IPV4.sub("<ip>", value)


def _safe_source(path: str) -> str:
    source = Path(path)
    return f"{source.parent.name}/{source.name}" if source.parent.name else source.name


def discover_logs(target: Path) -> list[Path]:
    target = target.expanduser().resolve()
    if target.is_file():
        return [target]
    if not target.is_dir():
        raise ValueError(f"log target does not exist: {target}")
    logs_dir = target / "logs" if (target / "logs").is_dir() else target
    files = sorted(
        (path for path in logs_dir.glob("output.log*") if path.is_file()),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
    )
    if not files:
        files = sorted((path for path in logs_dir.glob("*.log") if path.is_file()), key=lambda path: path.name)
    if not files:
        raise ValueError(f"no PEKAT log files found in: {logs_dir}")
    return files


def parse_file(path: Path) -> tuple[list[Record], list[dict[str, Any]]]:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"log exceeds {MAX_FILE_BYTES} byte limit: {path}")
    records: list[Record] = []
    unparsed: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def finish() -> None:
        nonlocal current
        if current is not None:
            records.append(Record(**current))
            current = None

    for number, line in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), start=1):
        match = HEADER.match(line)
        if match:
            finish()
            values = match.groupdict()
            current = {
                "path": str(path), "line": number, "component": values["component"].strip(),
                "timestamp": values["timestamp"], "logger": values["logger"].strip(),
                "severity": values["severity"], "message": values["message"].strip(), "continuation": (),
            }
        elif current is not None:
            current["continuation"] = (*current["continuation"], line)
        elif line.strip():
            unparsed.append({"source": _safe_source(str(path)), "line": number, "text": sanitize_text(line[:500])})
    finish()
    return records, unparsed


def terminal_exception(text: str) -> str | None:
    for line in reversed(text.splitlines()):
        match = TERMINAL_EXCEPTION.match(line.strip())
        if match:
            return f"{match.group('type')}: {match.group('message') or ''}".rstrip(": ")
    return None


def normalize_error(record: Record) -> str:
    value = sanitize_text(terminal_exception(record.full_text) or record.message)
    value = re.sub(r"(?i)\b0x[0-9a-f]+\b", "<hex>", value)
    value = re.sub(r"\b\d+\b", "<n>", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def classify(text: str) -> str:
    lowered = text.lower()
    scores = {name: sum(token in lowered for token in tokens) for name, tokens in CATEGORY_PATTERNS.items()}
    category, score = max(scores.items(), key=lambda item: item[1])
    return category if score else "unknown"


def recommended_check(category: str) -> str:
    return {
        "camera": "Read provider/discovery/initialization state, then correlate the first acquisition failure.",
        "model": "Read module modelId, registry row and artifact existence before inference readiness.",
        "filesystem": "Read configured path existence, permissions and free space without creating or deleting paths.",
        "code_flow": "Inspect the first traceback and correlated FLOW module; do not change FLOW to reproduce it.",
        "network": "Read process ownership and listening endpoint separately from application result semantics.",
        "project_start": "Read package identity, process command line, port ownership and first startup error.",
        "folder_source": "Read watched path, permissions and arrival timestamps.",
        "unknown": "Inspect surrounding records and correlate only identities explicitly present in evidence.",
    }[category]


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace(",", "."))


def _identities(records: list[Record]) -> dict[str, list[int]]:
    found: dict[str, set[int]] = {key: set() for key in IDENTITIES}
    for record in records:
        for key, pattern in IDENTITIES.items():
            found[key].update(int(value) for value in pattern.findall(record.full_text))
    return {key: sorted(values) for key, values in found.items() if values}


def _sessions(records: list[Record]) -> list[dict[str, Any]]:
    starts = [index for index, record in enumerate(records) if SESSION_START.search(record.full_text)]
    if not starts:
        return []
    rows = []
    for number, start in enumerate(starts, start=1):
        stop = starts[number] if number < len(starts) else len(records)
        selected = records[start:stop]
        rows.append({
            "session": number, "first": selected[0].timestamp, "last": selected[-1].timestamp,
            "record_count": len(selected), "error_count": sum(r.severity in {"ERROR", "CRITICAL"} for r in selected),
            "derivation": "explicit_start_marker",
        })
    return rows


def analyze_log_target(
    target: Path, *, max_families: int = 10, severities: Iterable[str] | None = None,
    component: str | None = None, incident_family: str | None = None,
    since: str | None = None, until: str | None = None, last_session: bool = False,
) -> dict[str, Any]:
    paths = discover_logs(target)
    if sum(path.stat().st_size for path in paths) > MAX_TOTAL_BYTES:
        raise ValueError(f"selected logs exceed {MAX_TOTAL_BYTES} byte total limit")
    records: list[Record] = []
    unparsed: list[dict[str, Any]] = []
    for path in paths:
        parsed, remainder = parse_file(path)
        records.extend(parsed)
        unparsed.extend(remainder)
    records.sort(key=lambda item: (_timestamp(item.timestamp), item.path, item.line))
    sessions = _sessions(records)
    selected = records
    if last_session and sessions:
        selected = [record for record in selected if _timestamp(record.timestamp) >= _timestamp(sessions[-1]["first"])]
    severity_set = {value.upper() for value in severities or []}
    unknown_severities = severity_set - {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if unknown_severities:
        raise ValueError(f"unsupported severity: {', '.join(sorted(unknown_severities))}")
    if severity_set:
        selected = [record for record in selected if record.severity in severity_set]
    if component:
        needle = component.casefold()
        selected = [record for record in selected if needle in record.component.casefold() or needle in record.logger.casefold()]
    if since:
        selected = [record for record in selected if _timestamp(record.timestamp) >= _timestamp(since)]
    if until:
        selected = [record for record in selected if _timestamp(record.timestamp) <= _timestamp(until)]
    errors = [record for record in selected if record.severity in {"ERROR", "CRITICAL"}]
    families: dict[str, list[Record]] = {}
    for record in errors:
        families.setdefault(normalize_error(record), []).append(record)
    if incident_family:
        needle = incident_family.casefold()
        families = {signature: items for signature, items in families.items() if needle in signature}
    ordered = sorted(families.items(), key=lambda item: (-len(item[1]), _timestamp(item[1][0].timestamp), item[0]))
    incidents = []
    for signature, items in ordered[:max_families]:
        first, last = items[0], items[-1]
        evidence = sanitize_text(first.full_text)
        category = classify(first.full_text)
        secondary = any(token in first.full_text.lower() for token in SECONDARY_PATTERNS)
        incidents.append({
            "signature": signature, "count": len(items), "first_timestamp": first.timestamp,
            "last_timestamp": last.timestamp, "first_file": _safe_source(first.path), "first_line": first.line,
            "component": first.component, "logger": first.logger, "message": sanitize_text(first.message),
            "terminal_exception": sanitize_text(terminal_exception(first.full_text) or "") or None,
            "category": category, "likely_secondary": secondary,
            "supporting_evidence": evidence[:2000], "evidence_level": "OFFLINE_PARSED_ARTIFACT",
            "confidence": "medium" if not secondary else "low",
            "recommended_next_check": recommended_check(category),
        })
    roots = sorted(incidents, key=lambda row: (row["likely_secondary"], row["first_timestamp"], -row["count"]))[:3]
    cascades = [row for row in incidents if row["likely_secondary"]]
    repeated_cascades = [row for row in cascades if row["count"] > 1]
    return {
        "schema": "pekat-log-forensics/0.2", "target": "<selected-target>",
        "format_scope": "PEKAT-style header parsed; exact semantic evidence is anchored on 4.0.3",
        "files": [_safe_source(str(path)) for path in paths],
        "range": {"first": selected[0].timestamp if selected else None, "last": selected[-1].timestamp if selected else None},
        "scope": {"severities": sorted(severity_set), "component": component, "incident_family": incident_family,
                  "since": since, "until": until, "last_session": last_session},
        "sessions": sessions, "record_count": len(selected),
        "severity_counts": dict(sorted(Counter(item.severity for item in selected).items())),
        "error_records": len(errors), "unique_error_families": len(families),
        "unique_incident_families": len(families), "top_error_families": incidents, "incidents": incidents,
        "first_root_cause_candidates": roots, "root_cause_candidates": roots,
        "repeated_secondary_errors": repeated_cascades, "cascade_symptoms": cascades,
        "affected_identities": _identities(selected), "unparsed_line_count": len(unparsed),
        "unparsed_samples": unparsed[:5],
        "unknowns": ["Root-cause ranking is heuristic; correlation and first ERROR are not proof of causality."],
        "evidence_level": "OFFLINE_PARSED_ARTIFACT", "read_only": True,
    }


def render(report: dict[str, Any]) -> str:
    lines = ["SESSION / RANGE", f"  files: {len(report['files'])}",
             f"  first: {report['range']['first'] or 'unknown'}", f"  last: {report['range']['last'] or 'unknown'}",
             f"  records/errors: {report['record_count']}/{report['error_records']}", "TOP ERROR FAMILIES"]
    for row in report["incidents"]:
        suffix = " [likely cascade]" if row["likely_secondary"] else ""
        lines.append(f"  {row['count']}x {row['category']}: {row['message']}{suffix}")
    if not report["incidents"]:
        lines.append("  none")
    lines.append("FIRST ROOT-CAUSE CANDIDATES (HEURISTIC)")
    lines.extend(f"  {row['first_timestamp']} {row['category']}: {row['message']}" for row in report["root_cause_candidates"])
    lines.append("REPEATED SECONDARY ERRORS")
    repeated = report["repeated_secondary_errors"]
    lines.extend(f"  {row['count']}x {row['category']}: {row['message']}" for row in repeated)
    if not repeated:
        lines.append("  none")
    subsystems = sorted({row["category"] for row in report["root_cause_candidates"]})
    lines.append(f"LIKELY SUBSYSTEM: {', '.join(subsystems) if subsystems else 'unknown'}")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze PEKAT logs without modifying the project.")
    parser.add_argument("target", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-families", type=int, default=10)
    parser.add_argument("--severity", action="append", dest="severities", help="repeatable severity filter")
    parser.add_argument("--component", help="case-insensitive component/logger substring")
    parser.add_argument("--incident-family", help="normalized incident signature substring")
    parser.add_argument("--since", help="inclusive ISO-like timestamp")
    parser.add_argument("--until", help="inclusive ISO-like timestamp")
    parser.add_argument("--last-session", action="store_true", help="select the last explicitly marked session")
    args = parser.parse_args(argv)
    try:
        report = analyze_log_target(
            args.target, max_families=max(1, args.max_families), severities=args.severities,
            component=args.component, incident_family=args.incident_family, since=args.since,
            until=args.until, last_session=args.last_session,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
