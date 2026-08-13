"""Offline PEKAT FLOW analyzer with a non-executing restricted Pickle reader.

The observed PEKAT 3.19.3/4.x ``*.db`` format is Pickle protocol 4.  This
module never calls pickle.load(s): it interprets only primitive/container
opcodes and rejects object construction, persistent IDs, extensions, and
external buffers.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pickletools
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable

MAX_DB_BYTES = 64 * 1024 * 1024
MAX_OPCODES = 2_000_000
BANNED_OPCODES = {
    "GLOBAL", "STACK_GLOBAL", "REDUCE", "BUILD", "OBJ", "INST",
    "NEWOBJ", "NEWOBJ_EX", "EXT1", "EXT2", "EXT4", "PERSID",
    "BINPERSID", "NEXT_BUFFER", "READONLY_BUFFER",
}


class UnsafePickleError(ValueError):
    """Raised when a DB is unsafe, unsupported, malformed, or too large."""


_MARK = object()


def _take_mark(stack: list[Any]) -> tuple[int, list[Any]]:
    for index in range(len(stack) - 1, -1, -1):
        if stack[index] is _MARK:
            return index, stack[index + 1 :]
    raise UnsafePickleError("pickle MARK not found")


def restricted_loads(data: bytes) -> Any:
    """Decode a protocol-4 primitive/container Pickle without executing it."""
    if len(data) > MAX_DB_BYTES:
        raise UnsafePickleError(f"DB exceeds {MAX_DB_BYTES} byte safety limit")
    stack: list[Any] = []
    memo: dict[int, Any] = {}
    protocol: int | None = None
    stopped = False

    try:
        operations = pickletools.genops(data)
        for count, (opcode, arg, position) in enumerate(operations, start=1):
            if count > MAX_OPCODES:
                raise UnsafePickleError("pickle opcode limit exceeded")
            name = opcode.name
            if name in BANNED_OPCODES:
                raise UnsafePickleError(f"dangerous pickle opcode {name} at {position}")
            if name == "PROTO":
                protocol = int(arg)
                if protocol != 4:
                    raise UnsafePickleError(f"expected Pickle protocol 4, found {protocol}")
            elif name == "FRAME":
                continue
            elif name == "MARK":
                stack.append(_MARK)
            elif name in {"NONE", "NEWFALSE", "NEWTRUE"}:
                stack.append({"NONE": None, "NEWFALSE": False, "NEWTRUE": True}[name])
            elif name in {
                "INT", "BININT", "BININT1", "BININT2", "LONG", "LONG1", "LONG4",
                "FLOAT", "BINFLOAT", "STRING", "BINSTRING", "SHORT_BINSTRING",
                "UNICODE", "BINUNICODE", "SHORT_BINUNICODE", "BINUNICODE8",
                "BINBYTES", "SHORT_BINBYTES", "BINBYTES8", "BYTEARRAY8",
            }:
                stack.append(arg)
            elif name == "EMPTY_LIST":
                stack.append([])
            elif name == "EMPTY_DICT":
                stack.append({})
            elif name == "EMPTY_TUPLE":
                stack.append(())
            elif name == "EMPTY_SET":
                stack.append(set())
            elif name == "APPEND":
                item = stack.pop()
                if not stack or not isinstance(stack[-1], list):
                    raise UnsafePickleError("APPEND target is not a list")
                stack[-1].append(item)
            elif name == "APPENDS":
                mark, items = _take_mark(stack)
                if mark == 0 or not isinstance(stack[mark - 1], list):
                    raise UnsafePickleError("APPENDS target is not a list")
                stack[mark - 1].extend(items)
                del stack[mark:]
            elif name == "SETITEM":
                value = stack.pop()
                key = stack.pop()
                if not stack or not isinstance(stack[-1], dict):
                    raise UnsafePickleError("SETITEM target is not a dict")
                stack[-1][key] = value
            elif name == "SETITEMS":
                mark, items = _take_mark(stack)
                if mark == 0 or not isinstance(stack[mark - 1], dict) or len(items) % 2:
                    raise UnsafePickleError("invalid SETITEMS payload")
                target = stack[mark - 1]
                for index in range(0, len(items), 2):
                    target[items[index]] = items[index + 1]
                del stack[mark:]
            elif name == "ADDITEMS":
                mark, items = _take_mark(stack)
                if mark == 0 or not isinstance(stack[mark - 1], set):
                    raise UnsafePickleError("ADDITEMS target is not a set")
                stack[mark - 1].update(items)
                del stack[mark:]
            elif name in {"TUPLE", "FROZENSET"}:
                mark, items = _take_mark(stack)
                del stack[mark:]
                stack.append(tuple(items) if name == "TUPLE" else frozenset(items))
            elif name in {"TUPLE1", "TUPLE2", "TUPLE3"}:
                size = int(name[-1])
                if len(stack) < size:
                    raise UnsafePickleError(f"invalid {name} stack")
                items = stack[-size:]
                del stack[-size:]
                stack.append(tuple(items))
            elif name == "MEMOIZE":
                if not stack:
                    raise UnsafePickleError("MEMOIZE with empty stack")
                memo[len(memo)] = stack[-1]
            elif name in {"PUT", "BINPUT", "LONG_BINPUT"}:
                if not stack:
                    raise UnsafePickleError(f"{name} with empty stack")
                memo[int(arg)] = stack[-1]
            elif name in {"GET", "BINGET", "LONG_BINGET"}:
                try:
                    stack.append(memo[int(arg)])
                except KeyError as exc:
                    raise UnsafePickleError(f"unknown memo index {arg}") from exc
            elif name == "POP":
                if not stack:
                    raise UnsafePickleError("POP with empty stack")
                stack.pop()
            elif name == "POP_MARK":
                mark, _ = _take_mark(stack)
                del stack[mark:]
            elif name == "DUP":
                if not stack:
                    raise UnsafePickleError("DUP with empty stack")
                stack.append(stack[-1])
            elif name == "STOP":
                stopped = True
                break
            else:
                raise UnsafePickleError(f"unsupported pickle opcode {name} at {position}")
    except (ValueError, UnicodeDecodeError) as exc:
        if isinstance(exc, UnsafePickleError):
            raise
        raise UnsafePickleError(f"malformed pickle: {exc}") from exc

    if protocol != 4 or not stopped or len(stack) != 1 or stack[0] is _MARK:
        raise UnsafePickleError("incomplete or malformed Pickle protocol 4 stream")
    return stack[0]


def parse_flow_sort(
    sequence: Any, module_index: dict[int, dict[str, Any]], *, _depth: int = 0
) -> dict[str, Any]:
    """Parse the observed recursive modules.sort grammar into a FLOW AST."""
    if _depth > 128:
        raise ValueError("modules.sort nesting exceeds safety limit")
    if not isinstance(sequence, list):
        raise ValueError("modules.sort must be a list")
    nodes: list[dict[str, Any]] = []
    for node in sequence:
        if isinstance(node, bool):
            raise ValueError("boolean is not a valid module ID")
        if isinstance(node, int):
            record = module_index.get(node)
            nodes.append({
                "kind": "module",
                "id": node,
                "type": record.get("type") if record else None,
                "label": record.get("label") if record else None,
                "missing_record": record is None,
            })
        elif isinstance(node, list):
            nodes.append({
                "kind": "parallel",
                "branches": [
                    parse_flow_sort(branch, module_index, _depth=_depth + 1) for branch in node
                ],
            })
        else:
            raise ValueError(f"unsupported modules.sort node: {node!r}")
    return {"kind": "sequence", "nodes": nodes}


def flow_ids(sequence: Any, *, _depth: int = 0) -> list[int]:
    if _depth > 128:
        raise ValueError("modules.sort nesting exceeds safety limit")
    result: list[int] = []
    if not isinstance(sequence, list):
        return result
    for node in sequence:
        if isinstance(node, int) and not isinstance(node, bool):
            result.append(node)
        elif isinstance(node, list):
            for branch in node:
                result.extend(flow_ids(branch, _depth=_depth + 1))
    return result


def module_execution_state(record: dict[str, Any], in_flow: bool) -> str:
    if record.get("softDeletedDate") is not None:
        return "soft_deleted"
    if in_flow and record.get("isActive") is False:
        return "disabled"
    if in_flow:
        return "active_candidate"
    return "historical_or_unreferenced"


def _literal_key(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


class _CodeVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.context_reads: set[str] = set()
        self.context_writes: set[str] = set()
        self.globaldata_reads: set[str] = set()
        self.globaldata_writes: set[str] = set()
        self.global_aliases: set[str] = set()
        self.side_effects: set[str] = set()
        self.imports: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.imports.add(item.name)
            self._classify_import(item.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        name = node.module or ""
        self.imports.add(name)
        self._classify_import(name)
        self.generic_visit(node)

    def _classify_import(self, name: str) -> None:
        if name.startswith(("requests", "urllib", "httpx", "socket", "pekat_communication")):
            self.side_effects.add("network_or_cross_pekat")
        if name.startswith(("snap7", "pymodbus")):
            self.side_effects.add("plc_or_fieldbus")

    def visit_Assign(self, node: ast.Assign) -> None:
        is_global = False
        if isinstance(node.value, ast.Subscript) and isinstance(node.value.value, ast.Name):
            is_global = node.value.value.id == "context" and _literal_key(node.value.slice) == "globalData"
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            is_global = (
                isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "context"
                and node.value.func.attr == "get"
                and bool(node.value.args)
                and _literal_key(node.value.args[0]) == "globalData"
            )
        if is_global:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.global_aliases.add(target.id)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        key = _literal_key(node.slice)
        if isinstance(node.value, ast.Name) and key is not None:
            if node.value.id == "context":
                (self.context_writes if isinstance(node.ctx, ast.Store) else self.context_reads).add(key)
            elif node.value.id in self.global_aliases:
                (self.globaldata_writes if isinstance(node.ctx, ast.Store) else self.globaldata_reads).add(key)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            owner = node.func.value
            attr = node.func.attr
            if isinstance(owner, ast.Name) and owner.id == "context" and attr == "get" and node.args:
                key = _literal_key(node.args[0])
                if key is not None:
                    self.context_reads.add(key)
            if isinstance(owner, ast.Name) and owner.id in self.global_aliases and attr == "get" and node.args:
                key = _literal_key(node.args[0])
                if key is not None:
                    self.globaldata_reads.add(key)
            if attr in {"post", "put", "patch", "delete", "send", "sendall", "connect"}:
                self.side_effects.add("network_write_or_connection")
            if attr in {"imwrite", "write_text", "write_bytes", "unlink", "remove", "rename"}:
                self.side_effects.add("filesystem_write")
            if attr in {"update_global_data_async", "add_client_to_pekat"}:
                self.side_effects.add("cross_pekat")
        elif isinstance(node.func, ast.Name) and node.func.id == "open":
            mode = _literal_key(node.args[1]) if len(node.args) > 1 else None
            if mode is None or any(flag in mode for flag in "wax+"):
                self.side_effects.add("filesystem_write_or_unknown_open")
        self.generic_visit(node)


def analyze_code(source: Any) -> dict[str, Any]:
    if not isinstance(source, str):
        return {"syntax": "missing", "context_reads": [], "context_writes": [],
                "globaldata_reads": [], "globaldata_writes": [], "imports": [], "side_effects": []}
    visitor = _CodeVisitor()
    try:
        visitor.visit(ast.parse(source))
        syntax = "valid"
    except SyntaxError as exc:
        syntax = f"invalid: line {exc.lineno}: {exc.msg}"
    return {
        "syntax": syntax,
        "context_reads": sorted(visitor.context_reads),
        "context_writes": sorted(visitor.context_writes),
        "globaldata_reads": sorted(visitor.globaldata_reads),
        "globaldata_writes": sorted(visitor.globaldata_writes),
        "imports": sorted(visitor.imports),
        "side_effects": sorted(visitor.side_effects),
    }


def _safe_value(value: Any, depth: int = 0) -> Any:
    if depth > 6:
        return "<depth-limit>"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, (list, tuple)):
        return [_safe_value(item, depth + 1) for item in value[:200]]
    if isinstance(value, dict):
        return {str(key): _safe_value(item, depth + 1) for key, item in list(value.items())[:200]}
    return repr(value)


@dataclass
class ProjectSource:
    names: list[str]
    read: Callable[[str], bytes]


def _directory_source(path: Path) -> ProjectSource:
    base = path
    if path.name in {"database", "database_old"}:
        base = path.parent
    files = sorted((item for item in base.rglob("*") if item.is_file()), key=lambda item: item.as_posix())
    names = [item.relative_to(base).as_posix() for item in files]
    return ProjectSource(names, lambda name: (base / PurePosixPath(name)).read_bytes())


def _zip_source(path: Path) -> tuple[ProjectSource, zipfile.ZipFile]:
    archive = zipfile.ZipFile(path)
    if archive.testzip() is not None:
        archive.close()
        raise ValueError("ZIP CRC test failed")
    files = [info for info in archive.infolist() if not info.is_dir()]
    if sum(info.file_size for info in files) > 512 * 1024 * 1024:
        archive.close()
        raise ValueError("ZIP uncompressed size exceeds 512 MiB safety limit")
    for info in files:
        p = PurePosixPath(info.filename)
        if p.is_absolute() or ".." in p.parts:
            archive.close()
            raise ValueError(f"unsafe ZIP path: {info.filename}")
    return ProjectSource([info.filename for info in files], archive.read), archive


def _find_layer_prefixes(names: list[str]) -> dict[str, str]:
    found: dict[str, str] = {}
    for name in names:
        parts = PurePosixPath(name).parts
        for index, part in enumerate(parts):
            if part in {"database", "database_old"} and index + 1 < len(parts):
                found.setdefault(part, "/".join(parts[: index + 1]) + "/")
    if not found and any(PurePosixPath(name).name == "modules.db" for name in names):
        found["database"] = ""
    # Current/live data must be reported before historical data on every OS.
    return {name: found[name] for name in ("database", "database_old") if name in found}


def _explicit_project_metadata(source: ProjectSource) -> list[dict[str, Any]]:
    """Read only small explicit JSON metadata; never infer from a DB field."""
    result: list[dict[str, Any]] = []
    for name in source.names:
        if PurePosixPath(name).name.lower() != "pekat_package.json":
            continue
        data = source.read(name)
        if len(data) > 1024 * 1024:
            result.append({"path": name, "error": "metadata exceeds 1 MiB safety limit"})
            continue
        try:
            value = json.loads(data.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            result.append({"path": name, "error": f"invalid JSON metadata: {exc}"})
            continue
        selected: dict[str, Any] = {}
        if isinstance(value, dict):
            for key in ("version", "pekatVersion", "pekat_version", "appVersion", "build"):
                if key in value and isinstance(value[key], (str, int, float)):
                    selected[key] = value[key]
        result.append({"path": name, "explicit_fields": selected})
    return result


def _flow_text(tree: dict[str, Any], indent: str = "") -> list[str]:
    lines: list[str] = []
    for node in tree["nodes"]:
        if node["kind"] == "module":
            label = node.get("label") or node.get("type") or "missing"
            lines.append(f"{indent}- [{node['id']}] {label}")
        else:
            lines.append(f"{indent}- Parallelism")
            for number, branch in enumerate(node["branches"], start=1):
                lines.append(f"{indent}  - Branch {number}" + (" (empty)" if not branch["nodes"] else ""))
                lines.extend(_flow_text(branch, indent + "    "))
    return lines


def _analyze_layer(source: ProjectSource, layer: str, prefix: str) -> dict[str, Any]:
    members = sorted(name for name in source.names if name.startswith(prefix))
    inventory = []
    for name in members:
        data = source.read(name)
        inventory.append({"name": PurePosixPath(name).name, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    modules_name = next((name for name in members if PurePosixPath(name).name == "modules.db"), None)
    if modules_name is None:
        return {"layer": layer, "inventory": inventory, "error": "modules.db not found"}
    modules = restricted_loads(source.read(modules_name))
    if not isinstance(modules, dict) or not isinstance(modules.get("items"), list):
        raise ValueError(f"{layer}/modules.db has unsupported top-level schema")
    sort = modules.get("sort", [])
    items = [item for item in modules["items"] if isinstance(item, dict)]
    index: dict[int, dict[str, Any]] = {}
    duplicate_ids: list[int] = []
    for item in items:
        module_id = item.get("id")
        if isinstance(module_id, int) and not isinstance(module_id, bool):
            if module_id in index:
                duplicate_ids.append(module_id)
            index[module_id] = item
    ids = flow_ids(sort)
    id_set = set(ids)
    tree = parse_flow_sort(sort, index)
    module_rows = []
    filters = []
    code_inventory = []
    for item in items:
        module_id = item.get("id")
        in_flow = module_id in id_set
        row = {
            "id": module_id,
            "type": item.get("type"),
            "label": item.get("label"),
            "in_flow": in_flow,
            "softDeletedDate": item.get("softDeletedDate"),
            "isActive_present": "isActive" in item,
            "isActive": item.get("isActive") if "isActive" in item else None,
            "execution_state": module_execution_state(item, in_flow),
        }
        module_rows.append(row)
        if str(item.get("type", "")).upper() == "CODE":
            code_inventory.append({**row, **analyze_code(item.get("sourceCode"))})
        if str(item.get("type", "")).upper() == "FILTER":
            filters.append({
                "id": module_id,
                "label": item.get("label"),
                "evalType": item.get("evalType"),
                "rules": _safe_value(item.get("rules", item.get("rule"))),
                "contextNode": _safe_value(item.get("contextNode")),
            })
    warnings = []
    missing = sorted(set(ids) - set(index))
    if missing:
        warnings.append(f"modules.sort references missing IDs: {missing}")
    if duplicate_ids:
        warnings.append(f"duplicate module IDs: {sorted(set(duplicate_ids))}")
    deleted_in_flow = sorted(
        item.get("id") for item in items
        if item.get("id") in id_set and item.get("softDeletedDate") is not None
    )
    if deleted_in_flow:
        warnings.append(f"soft-deleted IDs remain in modules.sort: {deleted_in_flow}")
    return {
        "layer": layer,
        "inventory": inventory,
        "modules_schema_keys": sorted(str(key) for key in modules),
        "flow_sort": _safe_value(sort),
        "flow_tree": tree,
        "flow_text": _flow_text(tree),
        "modules": module_rows,
        "filters": filters,
        "code_inventory": code_inventory,
        "warnings": warnings,
    }


def analyze_project(path: Path) -> dict[str, Any]:
    """Analyze a project directory, database directory, or project ZIP."""
    closeable: zipfile.ZipFile | None = None
    if path.is_dir():
        source = _directory_source(path)
        source_kind = "directory"
    elif zipfile.is_zipfile(path):
        source, closeable = _zip_source(path)
        source_kind = "zip"
    else:
        raise ValueError("input must be a project/database directory or ZIP")
    try:
        layers = _find_layer_prefixes(source.names)
        if "database" not in layers:
            raise ValueError("database/modules.db not found")
        report = {
            "source": str(path.resolve()),
            "source_kind": source_kind,
            "evidence_scope": "reverse_engineered_observed_schema_not_public_vendor_API",
            "explicit_project_metadata": _explicit_project_metadata(source),
            "database_layers": [
                _analyze_layer(source, layer, prefix) for layer, prefix in layers.items()
            ],
        }
        current = next((x for x in report["database_layers"] if x["layer"] == "database"), None)
        old = next((x for x in report["database_layers"] if x["layer"] == "database_old"), None)
        if current and old and "error" not in current and "error" not in old:
            current_hash = {x["name"]: x["sha256"] for x in current["inventory"]}
            old_hash = {x["name"]: x["sha256"] for x in old["inventory"]}
            report["migration_diff"] = {
                "database_old_role": "historical_or_pre_upgrade_evidence_not_live_flow",
                "same_flow_sort": current["flow_sort"] == old["flow_sort"],
                "identical_files": sorted(name for name in current_hash.keys() & old_hash.keys()
                                            if current_hash[name] == old_hash[name]),
                "changed_files": sorted(name for name in current_hash.keys() & old_hash.keys()
                                          if current_hash[name] != old_hash[name]),
                "current_only": sorted(current_hash.keys() - old_hash.keys()),
                "old_only": sorted(old_hash.keys() - current_hash.keys()),
            }
        return report
    finally:
        if closeable is not None:
            closeable.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Safely analyze PEKAT database FLOW offline")
    parser.add_argument("input", type=Path, help="project/database directory or ZIP")
    parser.add_argument("--output", type=Path, help="write UTF-8 JSON report")
    args = parser.parse_args(argv)
    try:
        report = analyze_project(args.input)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8", newline="\n")
        print(args.output)
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
