"""Validate ModuleSpec and generate a PEKAT .pmodule or .ptool file.

This tool only writes UTF-8 JSON. It never opens PEKAT or changes a project.
"""
from __future__ import annotations

import argparse
import ast
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_VERSIONS = {"3.19.3": ".pmodule", "4.0.1": ".ptool"}
FORM_TYPES = {"text", "number", "checkbox", "select"}
_id_lock = threading.Lock()
_last_id = 0


class ModuleSpecError(ValueError):
    """Raised when a ModuleSpec violates the verified export contract."""


def unique_epoch_ms() -> int:
    """Return a process-local monotonically unique epoch-millisecond integer."""
    global _last_id
    with _id_lock:
        value = int(time.time() * 1000)
        if value <= _last_id:
            value = _last_id + 1
        _last_id = value
        return value


def _string(value: Any, name: str, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise ModuleSpecError(f"{name} must be a string")
    if not allow_empty and not value.strip():
        raise ModuleSpecError(f"{name} must not be empty")
    return value


def _number(value: Any, name: str) -> int | float:
    if isinstance(value, bool):
        raise ModuleSpecError(f"{name} must be numeric, not boolean")
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = float(value.strip())
        except ValueError as exc:
            raise ModuleSpecError(f"{name} is not numeric") from exc
        return int(parsed) if parsed.is_integer() else parsed
    raise ModuleSpecError(f"{name} must be numeric")


def _boolean(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    raise ModuleSpecError(f"{name} must be boolean-compatible")


@dataclass(slots=True)
class FormItem:
    type: str
    formKey: str
    label: str
    defaultValue: Any
    visibility: str = ""
    min: str = ""
    max: str = ""
    options: str = ""
    id: int | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "FormItem":
        if not isinstance(value, dict):
            raise ModuleSpecError("form item must be an object")
        item = cls(
            type=_string(value.get("type"), "form.type", allow_empty=False).lower(),
            formKey=_string(value.get("formKey"), "form.formKey", allow_empty=False),
            label=_string(value.get("label"), "form.label", allow_empty=False),
            defaultValue=value.get("defaultValue"),
            visibility=_string(value.get("visibility", ""), "form.visibility"),
            min=str(value.get("min", "")),
            max=str(value.get("max", "")),
            options=_string(value.get("options", ""), "form.options"),
            id=value.get("id"),
        )
        item.validate()
        return item

    def validate(self) -> None:
        if self.type not in FORM_TYPES:
            raise ModuleSpecError(f"unsupported form type: {self.type}")
        if not self.formKey.replace("_", "a").isalnum() or self.formKey[0].isdigit():
            raise ModuleSpecError(f"invalid formKey: {self.formKey!r}")
        if self.id is not None and (not isinstance(self.id, int) or isinstance(self.id, bool)):
            raise ModuleSpecError("form.id must be an integer")
        if self.type == "text":
            self.defaultValue = "" if self.defaultValue is None else str(self.defaultValue)
        elif self.type == "number":
            self.defaultValue = _number(self.defaultValue, f"{self.formKey}.defaultValue")
            if self.min != "":
                _number(self.min, f"{self.formKey}.min")
            if self.max != "":
                _number(self.max, f"{self.formKey}.max")
            if self.min != "" and self.max != "" and float(self.min) > float(self.max):
                raise ModuleSpecError(f"{self.formKey}: min is greater than max")
        elif self.type == "checkbox":
            self.defaultValue = _boolean(self.defaultValue, f"{self.formKey}.defaultValue")
        elif self.type == "select":
            choices = [part.strip() for part in self.options.split(";") if part.strip()]
            if not choices:
                raise ModuleSpecError(f"{self.formKey}: select requires semicolon-separated options")
            self.options = ";".join(choices)
            self.defaultValue = str(self.defaultValue)
            if self.defaultValue not in choices:
                raise ModuleSpecError(f"{self.formKey}: defaultValue is not present in options")

    def normalize_value(self, value: Any) -> Any:
        if self.type == "number":
            return _number(value, self.formKey)
        if self.type == "checkbox":
            return _boolean(value, self.formKey)
        value = str(value)
        if self.type == "select" and value not in self.options.split(";"):
            raise ModuleSpecError(f"{self.formKey}: value is not present in options")
        return value

    def export(self, generated_id: int) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id if self.id is not None else generated_id,
            "type": self.type,
            "label": self.label,
            "formKey": self.formKey,
        }
        if self.type == "number":
            result.update({"min": self.min, "max": self.max})
        if self.type == "select":
            result["options"] = self.options
        result.update({"defaultValue": self.defaultValue, "visibility": self.visibility})
        return result


@dataclass(slots=True)
class ModuleSpec:
    target_version: str
    label: str
    source_code: str
    note: str = ""
    form: list[FormItem] = field(default_factory=list)
    form_values: dict[str, Any] = field(default_factory=dict)
    show_image_preview: bool = True
    is_active: bool = True
    module_id: int | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ModuleSpec":
        if not isinstance(value, dict):
            raise ModuleSpecError("ModuleSpec must be an object")
        raw_form = value.get("form", [])
        raw_values = value.get("form_values", {})
        if not isinstance(raw_form, list):
            raise ModuleSpecError("form must be a list")
        if not isinstance(raw_values, dict):
            raise ModuleSpecError("form_values must be an object")
        spec = cls(
            target_version=_string(value.get("target_version"), "target_version", allow_empty=False),
            label=_string(value.get("label"), "label", allow_empty=False),
            source_code=_string(value.get("source_code"), "source_code", allow_empty=False),
            note=_string(value.get("note", ""), "note"),
            form=[FormItem.from_mapping(item) for item in raw_form],
            form_values=raw_values,
            show_image_preview=_boolean(value.get("show_image_preview", True), "show_image_preview"),
            is_active=_boolean(value.get("is_active", True), "is_active"),
            module_id=value.get("module_id"),
        )
        spec.validate()
        return spec

    def validate(self) -> None:
        if self.target_version not in SUPPORTED_VERSIONS:
            raise ModuleSpecError(f"unsupported PEKAT version: {self.target_version}")
        if self.module_id is not None and (not isinstance(self.module_id, int) or isinstance(self.module_id, bool)):
            raise ModuleSpecError("module_id must be an integer")
        keys = [item.formKey for item in self.form]
        if len(keys) != len(set(keys)):
            raise ModuleSpecError("formKey values must be unique")
        unknown = sorted(set(self.form_values) - set(keys))
        if unknown:
            raise ModuleSpecError(f"form_values contains unknown keys: {unknown}")
        try:
            tree = ast.parse(self.source_code)
        except SyntaxError as exc:
            raise ModuleSpecError(f"source_code syntax error at line {exc.lineno}: {exc.msg}") from exc
        mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
        if len(mains) != 1:
            raise ModuleSpecError("source_code must define exactly one top-level main function")
        args = [arg.arg for arg in mains[0].args.args]
        if not args or args[0] != "context":
            raise ModuleSpecError("main first argument must be context")
        if self.form and (len(args) < 2 or args[1] != "form"):
            raise ModuleSpecError("modules with Form Editor items must use main(context, form=None)")

    @property
    def extension(self) -> str:
        return SUPPORTED_VERSIONS[self.target_version]

    def build_payload(self, *, epoch_ms: int | None = None) -> dict[str, Any]:
        base_id = unique_epoch_ms() if epoch_ms is None else epoch_ms
        if not isinstance(base_id, int) or isinstance(base_id, bool):
            raise ModuleSpecError("epoch_ms must be an integer")
        exported_form = [item.export(base_id + index + 1) for index, item in enumerate(self.form)]
        item_map = {item.formKey: item for item in self.form}
        values = {key: item_map[key].normalize_value(value) for key, value in self.form_values.items()}
        return {
            "type": "CODE",
            "module": {
                "label": self.label,
                "id": self.module_id if self.module_id is not None else base_id,
                "type": "CODE",
                "note": self.note,
                "gpuSettings": [],
                "softDeletedDate": None,
                "sourceCode": self.source_code,
                "form": exported_form,
                "formValues": values,
                "showImagePreview": self.show_image_preview,
                "editDate": base_id,
                "isActive": self.is_active,
            },
            "version": self.target_version,
        }

    def write(self, destination: Path, *, epoch_ms: int | None = None) -> Path:
        destination = destination.with_suffix(self.extension)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.build_payload(epoch_ms=epoch_ms), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
            newline="\n",
        )
        return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a validated PEKAT Code module")
    parser.add_argument("spec", type=Path, help="UTF-8 JSON ModuleSpec")
    parser.add_argument("--output", type=Path, required=True, help="Output path; extension is derived from version")
    args = parser.parse_args()
    spec = ModuleSpec.from_mapping(json.loads(args.spec.read_text(encoding="utf-8-sig")))
    print(spec.write(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
