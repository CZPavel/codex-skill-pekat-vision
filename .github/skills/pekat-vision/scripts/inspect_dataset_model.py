"""Read-only exact-4.0.3 PEKAT dataset and Detector-model inventory.

This standalone helper reads only allowlisted primitive/container Pickle
registries through the bundled restricted reader.  It never loads weights,
opens PEKAT, or writes project files.

Adapted from verified PEKAT Assistant pure/offline logic, public standalone
implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_flow_database import UnsafePickleError, restricted_loads

MODEL_DATABASES = {
    "classifierModels.db": "Classifier",
    "detectorModels.db": "Detector",
    "ocrModels.db": "OCR",
    "supervisedModels.db": "Supervised",
    "unsupervisedModels.db": "Unsupervised",
}
ALLOWED_DATABASES = {"images.db", "tags.db", "modules.db", *MODEL_DATABASES}
MAX_ARTIFACT_HASH_BYTES = 1_000_000


def _rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict) and isinstance(value.get("items"), list):
        return [item for item in value["items"] if isinstance(item, dict)]
    return []


def _ids(value: Any) -> list[int]:
    return [item for item in value if isinstance(item, int) and not isinstance(item, bool)] if isinstance(value, list) else []


def _finite(value: Any) -> int | float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def _load(project: Path, filename: str) -> Any | None:
    if filename not in ALLOWED_DATABASES:
        raise ValueError(f"database is not allowlisted: {filename}")
    path = project / "database" / filename
    return restricted_loads(path.read_bytes()) if path.is_file() else None


def _split(model: dict[str, Any], names: tuple[str, ...]) -> tuple[list[int], str | None, list[str]]:
    observed = [(name, _ids(model[name])) for name in names if name in model]
    if not observed:
        return [], None, []
    selected_name, selected = observed[0]
    conflicts = [name for name, ids in observed[1:] if ids != selected]
    return ([], None, [selected_name, *conflicts]) if conflicts else (selected, selected_name, [])


def _annotation_inventory(modules: Any, image_ids: list[int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rectangles: list[dict[str, Any]] = []
    states: list[dict[str, Any]] = []
    for module in _rows(modules):
        if module.get("type") != "DETECTOR" or not isinstance(module.get("id"), int) or isinstance(module["id"], bool):
            continue
        module_id = module["id"]
        classes = {item.get("id"): item.get("label") for item in _rows(module.get("classNames"))}
        mapping = module.get("imageRectangles")
        if not isinstance(mapping, dict):
            continue
        for image_id in dict.fromkeys(image_ids):
            keys = [(key, value) for key, value in mapping.items() if key == image_id or key == str(image_id)]
            state = "AMBIGUOUS_KEY" if len(keys) > 1 else "ABSENT" if not keys else "PRESENT_EMPTY" if isinstance(keys[0][1], list) and not keys[0][1] else "PRESENT_NONEMPTY" if isinstance(keys[0][1], list) else "INVALID_VALUE"
            states.append({"module_id": module_id, "image_id": image_id, "annotation_state": state})
        for raw_image_id, items in mapping.items():
            try:
                image_id = int(raw_image_id)
            except (TypeError, ValueError):
                continue
            if isinstance(raw_image_id, bool) or not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                geometry = {key: _finite(item.get(key)) for key in ("x", "y", "width", "height")}
                rectangle_id = item.get("id")
                if not isinstance(rectangle_id, int) or isinstance(rectangle_id, bool) or any(value is None for value in geometry.values()):
                    continue
                class_id = item.get("classNameId")
                rectangles.append({"module_id": module_id, "image_id": image_id, "rectangle_id": rectangle_id, "class": {"id": class_id, "label": classes.get(class_id)}, "geometry": geometry, "percent": item.get("percent") is True})
    return rectangles, states


def _detector_artifacts(project: Path, model_id: int) -> list[dict[str, Any]]:
    root = project / "detector" / "models" / str(model_id)
    if not root.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        size = path.stat().st_size
        rows.append({"path": path.relative_to(project).as_posix(), "size": size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if size <= MAX_ARTIFACT_HASH_BYTES else None})
    return rows


def inspect_dataset_model(project: Path) -> dict[str, Any]:
    """Return a bounded exact-4.0.3 inventory without modifying ``project``."""
    package_path = project / "pekat_package.json"
    if not project.is_dir() or not package_path.is_file():
        raise ValueError("expected a PEKAT project directory with pekat_package.json")
    try:
        package = json.loads(package_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid pekat_package.json: {exc}") from exc
    if not isinstance(package, dict) or str(package.get("version")) != "4.0.3":
        raise ValueError("dataset/model inspector supports exact PEKAT 4.0.3 only")
    images, tags, modules = _rows(_load(project, "images.db")), _rows(_load(project, "tags.db")), _load(project, "modules.db")
    image_ids = [item["id"] for item in images if isinstance(item.get("id"), int) and not isinstance(item["id"], bool)]
    image_set = set(image_ids)
    physical = {path.stem for path in (project / "images").glob("*") if path.is_file()} if (project / "images").is_dir() else set()
    tag_ids = {item.get("id") for item in tags if isinstance(item.get("id"), int) and not isinstance(item["id"], bool)}
    tag_counts: Counter[int] = Counter()
    findings: list[dict[str, Any]] = []
    image_rows = []
    for image in images:
        refs = _ids(image.get("tags"))
        image_rows.append({"id": image.get("id"), "tag_ids": refs, "physical_present": str(image.get("id")) in physical})
        for tag_id in refs:
            if tag_id in tag_ids:
                tag_counts[tag_id] += 1
            else:
                findings.append({"code": "unknown_tag_reference", "image_id": image.get("id"), "tag_id": tag_id})
        if isinstance(image.get("id"), int) and str(image["id"]) not in physical:
            findings.append({"code": "missing_image_file", "image_id": image["id"]})
    for image_id in sorted(physical - {str(item) for item in image_set}):
        findings.append({"code": "orphan_image_file", "image_id": image_id})
    findings.extend({"code": "duplicate_image_id", "image_id": item} for item, count in Counter(image_ids).items() if count > 1)
    model_rows: list[dict[str, Any]] = []
    for filename, model_type in MODEL_DATABASES.items():
        for model in _rows(_load(project, filename)):
            train, train_field, train_ambiguity = _split(model, ("trainImageIds", "trainingImageIds", "trainingImages"))
            test, test_field, test_ambiguity = _split(model, ("testImageIds", "testingImageIds", "testImages"))
            model_id = model.get("id")
            row = {"id": model_id, "name": model.get("label", model.get("name")), "model_type": model_type, "status": model.get("status"), "module_id": model.get("moduleId"), "train_image_ids": train, "test_image_ids": test, "train_source_field": train_field, "test_source_field": test_field, "train_count": len(train), "test_count": len(test), "split_field_ambiguity": {"train": train_ambiguity, "test": test_ambiguity}}
            if model_type == "Detector" and isinstance(model_id, int) and not isinstance(model_id, bool):
                params = model.get("trainingParams")
                row["training_config"] = params.get("config") if isinstance(params, dict) and isinstance(params.get("config"), dict) else None
                row["artifacts"] = _detector_artifacts(project, model_id)
            model_rows.append(row)
            for split, ambiguity in row["split_field_ambiguity"].items():
                if ambiguity:
                    findings.append({"code": "ambiguous_split_field_alias", "model_id": model_id, "split": split, "fields": ambiguity})
            overlap, missing = sorted(set(train) & set(test)), sorted((set(train) | set(test)) - image_set)
            if overlap:
                findings.append({"code": "train_test_overlap", "model_id": model_id, "image_ids": overlap})
            if missing:
                findings.append({"code": "missing_dataset_image_reference", "model_id": model_id, "image_ids": missing})
    rectangles, states = _annotation_inventory(modules, image_ids)
    return {"schema": "pekat-dataset-model-read/0.1", "read_only": True, "version_scope": "4.0.3", "project": {"name": package.get("name", project.name), "version": package.get("version")}, "images": {"count": len(images), "physical_count": len(physical), "records": image_rows, "tag_distribution": dict(sorted(tag_counts.items()))}, "tags": [{"id": item.get("id"), "label": item.get("label", item.get("name"))} for item in tags], "models": model_rows, "detector_annotations": rectangles, "detector_annotation_states": states, "qa_findings": findings, "limitations": ["Completed-model train/test fields are read-only training provenance, not an editable membership API.", "Detector ABSENT/PRESENT_EMPTY/PRESENT_NONEMPTY is a serialized read distinction; backend inverse semantics are unknown.", "Model weights are never loaded; artifacts over 1 MB are not hashed.", "No annotation, training, model lifecycle, tag, image, or project writer is exposed."]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only exact-4.0.3 PEKAT dataset/model inspector")
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, help="write JSON report outside the project")
    args = parser.parse_args(argv)
    try:
        report = inspect_dataset_model(args.project)
    except (OSError, ValueError, UnsafePickleError) as exc:
        parser.error(str(exc))
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
