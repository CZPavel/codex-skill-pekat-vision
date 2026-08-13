"""Read-only PEKAT project log analyzer using only the Python standard library."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HEADER = re.compile(
    r"^(?P<component>[^\r\n]+?)\s+-\s+"
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+-\s+"
    r"(?P<logger>[^\r\n]+?)\s+-\s+"
    r"(?P<severity>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+-\s+"
    r"(?P<message>.*)$"
)
TERMINAL_EXCEPTION = re.compile(r"^(?P<type>[A-Za-z_][\w.]*(?:Error|Exception)):\s*(?P<message>.*)$")
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024

CATEGORY_PATTERNS = {
    "camera": (
        "camera", "genicam", "grab", "acquisition", "no camera connections",
        "camera is not initialized", "camera search", "selected camera",
    ),
    "model": ("model not loaded", "model is not loaded", "loading model", "inference", "classifier model", "detector model"),
    "filesystem": ("image saver", "root folder", "does not exist", "permission denied", "disk", "invalid path", "filenotfounderror"),
    "code_flow": ("error analyzing image", "traceback", "sourcecode", "code module", "flow", "syntaxerror"),
    "network": ("connection refused", "connection reset", "timed out", "timeout", "http error", "socket", "network"),
    "project_start": ("project server", "server startup", "address already in use", "port is already", "startup failed", "failed to start"),
    "folder_source": ("started monitoring folder", "folder watcher", "watcher"),
}
SECONDARY_PATTERNS = (
    "camera is not initialized", "no grab result", "grab error", "model is not loaded yet",
)


@dataclass(frozen=True)
class Record:
    path: str
    line: int
    component: str
    timestamp: str
    severity: str
    message: str
    continuation: tuple[str, ...]

    @property
    def full_text(self) -> str:
        return "\n".join((self.message, *self.continuation)).strip()


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
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"log exceeds {MAX_FILE_BYTES} byte limit: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    records: list[Record] = []
    unparsed: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def finish() -> None:
        nonlocal current
        if current is not None:
            records.append(Record(**current))
            current = None

    for number, line in enumerate(text.splitlines(), start=1):
        match = HEADER.match(line)
        if match:
            finish()
            values = match.groupdict()
            current = {
                "path": str(path),
                "line": number,
                "component": values["component"].strip(),
                "timestamp": values["timestamp"],
                "severity": values["severity"],
                "message": values["message"].strip(),
                "continuation": (),
            }
        elif current is not None:
            current["continuation"] = (*current["continuation"], line)
        elif line.strip():
            unparsed.append({"path": str(path), "line": number, "text": line[:500]})
    finish()
    return records, unparsed


def terminal_exception(text: str) -> str | None:
    for line in reversed(text.splitlines()):
        match = TERMINAL_EXCEPTION.match(line.strip())
        if match:
            return f"{match.group('type')}: {match.group('message')}".strip()
    return None


def normalize_error(record: Record) -> str:
    value = terminal_exception(record.full_text) or record.message
    value = re.sub(r"[A-Za-z]:\\[^\r\n]+", "<path>", value)
    value = re.sub(r"/(?:[^\s/:]+/)+[^\s:]+", "<path>", value)
    value = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<uuid>", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0x[0-9a-f]+\b", "<hex>", value, flags=re.IGNORECASE)
    value = re.sub(r"\b\d+\b", "<n>", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def classify(text: str) -> str:
    lowered = text.lower()
    scores = {name: sum(token in lowered for token in tokens) for name, tokens in CATEGORY_PATTERNS.items()}
    category, score = max(scores.items(), key=lambda item: item[1])
    return category if score else "unknown"


def recommended_check(category: str) -> str:
    return {
        "camera": "Check provider creation, device discovery, persisted selection, initialization, then acquisition/grab in that order.",
        "model": "Check model path/ID, load start, load completion and readiness before inference.",
        "filesystem": "Check configured path existence, permissions and free space; do not create or delete production paths automatically.",
        "code_flow": "Inspect the first user-Code/FLOW traceback and module context; do not change FLOW before the first cause is identified.",
        "network": "Check owner process, host/port and bounded transport failure separately from a valid NOK result.",
        "project_start": "Check exact project metadata, process command line, configured/listening port and the first startup error.",
        "folder_source": "Check watched source path, permissions and whether new input files are arriving.",
        "unknown": "Inspect surrounding records and correlate the timestamp with project, process, camera, model and filesystem state.",
    }[category]


def analyze_log_target(target: Path, *, max_families: int = 10) -> dict[str, Any]:
    paths = discover_logs(target)
    total = sum(path.stat().st_size for path in paths)
    if total > MAX_TOTAL_BYTES:
        raise ValueError(f"selected logs exceed {MAX_TOTAL_BYTES} byte total limit")
    records: list[Record] = []
    unparsed: list[dict[str, Any]] = []
    for path in paths:
        parsed, remainder = parse_file(path)
        records.extend(parsed)
        unparsed.extend(remainder)
    records.sort(key=lambda item: (item.timestamp, item.path, item.line))
    errors = [item for item in records if item.severity in {"ERROR", "CRITICAL"}]
    families: dict[str, list[Record]] = {}
    for item in errors:
        families.setdefault(normalize_error(item), []).append(item)
    ordered = sorted(families.items(), key=lambda item: (-len(item[1]), item[1][0].timestamp, item[0]))
    family_rows = []
    for signature, items in ordered[:max_families]:
        first = items[0]
        terminal = terminal_exception(first.full_text)
        text = first.full_text
        category = classify(text)
        family_rows.append({
            "signature": signature,
            "count": len(items),
            "first_timestamp": first.timestamp,
            "first_file": first.path,
            "first_line": first.line,
            "message": first.message,
            "terminal_exception": terminal,
            "category": category,
            "likely_secondary": any(token in text.lower() for token in SECONDARY_PATTERNS),
            "recommended_next_check": recommended_check(category),
        })
    root_candidates = sorted(
        family_rows,
        key=lambda row: (row["likely_secondary"], row["first_timestamp"], -row["count"]),
    )[:3]
    return {
        "target": str(Path(target).expanduser().resolve()),
        "files": [str(path) for path in paths],
        "range": {
            "first": records[0].timestamp if records else None,
            "last": records[-1].timestamp if records else None,
        },
        "record_count": len(records),
        "severity_counts": dict(sorted(Counter(item.severity for item in records).items())),
        "error_records": len(errors),
        "unique_error_families": len(families),
        "top_error_families": family_rows,
        "first_root_cause_candidates": root_candidates,
        "repeated_secondary_errors": [row for row in family_rows if row["likely_secondary"] and row["count"] > 1],
        "unparsed_line_count": len(unparsed),
        "unparsed_samples": unparsed[:5],
        "read_only": True,
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "SESSION / RANGE",
        f"  files: {len(report['files'])}",
        f"  first: {report['range']['first'] or 'unknown'}",
        f"  last: {report['range']['last'] or 'unknown'}",
        f"  records/errors: {report['record_count']}/{report['error_records']}",
        "TOP ERROR FAMILIES",
    ]
    if not report["top_error_families"]:
        lines.append("  none")
    for row in report["top_error_families"]:
        suffix = " [likely secondary]" if row["likely_secondary"] else ""
        lines.append(f"  {row['count']}x {row['category']}: {row['message']}{suffix}")
        if row["terminal_exception"]:
            lines.append(f"    terminal: {row['terminal_exception']}")
    lines.append("FIRST ROOT-CAUSE CANDIDATES")
    for row in report["first_root_cause_candidates"]:
        lines.append(f"  {row['first_timestamp']} {row['category']}: {row['message']}")
    lines.append("REPEATED SECONDARY ERRORS")
    if not report["repeated_secondary_errors"]:
        lines.append("  none")
    for row in report["repeated_secondary_errors"]:
        lines.append(f"  {row['count']}x {row['category']}: {row['message']}")
    subsystems = sorted({row["category"] for row in report["first_root_cause_candidates"]})
    lines.append(f"LIKELY SUBSYSTEM: {', '.join(subsystems) if subsystems else 'unknown'}")
    lines.append("RECOMMENDED NEXT CHECK")
    seen: set[str] = set()
    for row in report["first_root_cause_candidates"]:
        check = row["recommended_next_check"]
        if check not in seen:
            lines.append(f"  - {check}")
            seen.add(check)
    if report["unparsed_line_count"]:
        lines.append(f"UNPARSED LINES: {report['unparsed_line_count']} (retained as samples; not discarded)")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Group and classify PEKAT output.log errors without modifying the project.")
    parser.add_argument("target", type=Path, help="output.log, logs directory, or project directory")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--max-families", type=int, default=10)
    args = parser.parse_args(argv)
    report = analyze_log_target(args.target, max_families=max(1, args.max_families))
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
