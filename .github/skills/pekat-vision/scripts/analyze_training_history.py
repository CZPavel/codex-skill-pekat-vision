"""Read-only, exact-4.0.3 PEKAT training-history inventory and interpretation."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

from analyze_flow_database import UnsafePickleError, restricted_loads

FAMILIES = {
    "detector": ("detectorModels.db", "detector"),
    "classifier": ("classifierModels.db", "classifier"),
    "supervised": ("supervisedModels.db", "supervised"),
    "anomaly": ("unsupervisedModels.db", "unsupervised"),
    "unsupervised": ("unsupervisedModels.db", "unsupervised"),
    "ocr": ("ocrModels.db", "ocr"),
}
BINARY_SUFFIXES = {".pt", ".pth", ".tm", ".npy", ".npz"}
MAX_STRUCTURED_BYTES = 16 * 1024 * 1024


def _rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        for key in ("models", "items", "data"):
            if isinstance(value.get(key), list):
                return [row for row in value[key] if isinstance(row, dict)]
        if all(isinstance(row, dict) for row in value.values()):
            return list(value.values())
    return []


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def parse_step_csv(path: Path) -> dict[str, Any]:
    if path.suffix.casefold() != ".csv":
        raise ValueError("training history parser accepts CSV only")
    if path.stat().st_size > MAX_STRUCTURED_BYTES:
        raise ValueError("training CSV exceeds safe size limit")
    rows = [row for row in csv.reader(path.read_text(encoding="utf-8-sig", errors="strict").splitlines()) if row]
    if not rows:
        return {"columns": [], "points": [], "header_present": False, "malformed_rows": [], "provenance": path.name}
    header_present = any(_number(cell) is None for cell in rows[0])
    columns = ([cell.strip() or f"column_{index + 1}" for index, cell in enumerate(rows[0])]
               if header_present else [f"column_{index + 1}" for index in range(len(rows[0]))])
    source_rows = rows[1:] if header_present else rows
    points: list[dict[str, float | int]] = []
    malformed: list[int] = []
    for row_number, row in enumerate(source_rows, start=2 if header_present else 1):
        if len(row) != len(columns) or any(_number(value) is None for value in row):
            malformed.append(row_number)
            continue
        point: dict[str, float | int] = {key: float(value) for key, value in zip(columns, row, strict=True)}
        point["step_index"] = len(points)
        points.append(point)
    return {
        "columns": columns, "points": points, "header_present": header_present,
        "malformed_rows": malformed, "provenance": path.name,
        "metric_semantics": "FIELD_NAME_ONLY" if header_present else "UNKNOWN_HEADERLESS_COLUMNS",
    }


def _artifact_inventory(model_dir: Path, project: Path) -> list[dict[str, Any]]:
    if not model_dir.is_dir():
        return []
    artifacts = []
    for path in sorted(model_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.casefold()
        row: dict[str, Any] = {
            "path": path.relative_to(project).as_posix(), "size": path.stat().st_size,
            "kind": "binary_model_or_array" if suffix in BINARY_SUFFIXES else "structured_or_other",
            "parsed": path.name == "step.csv", "deserialized": False,
        }
        if suffix == ".json":
            if path.stat().st_size > MAX_STRUCTURED_BYTES:
                row["parse_status"] = "size_limit"
            else:
                try:
                    value = json.loads(path.read_text(encoding="utf-8-sig"))
                    row["parsed"] = True
                    row["parse_status"] = "ok"
                    row["json_shape"] = ({"type": "object", "keys": sorted(value)[:100]}
                                         if isinstance(value, dict) else
                                         {"type": type(value).__name__, "length": len(value)}
                                         if isinstance(value, list) else {"type": type(value).__name__})
                except (OSError, UnicodeError, json.JSONDecodeError):
                    row["parse_status"] = "malformed_or_unreadable"
        artifacts.append(row)
    return artifacts


def _registry_history(model: dict[str, Any], database: str, model_id: Any) -> dict[str, Any] | None:
    raw = model.get("loss")
    if not isinstance(raw, list):
        return None
    points = [{"step_index": index, "loss": number} for index, item in enumerate(raw)
              if (number := _number(item)) is not None]
    return {
        "columns": ["step_index", "loss"], "points": points, "header_present": True,
        "malformed_count": len(raw) - len(points),
        "provenance": f"database/{database}#model[{model_id}].loss",
        "metric_semantics": "EXPLICIT_REGISTRY_FIELD",
    }


def _assert_exact_project(project: Path) -> dict[str, Any]:
    package_path = project / "pekat_package.json"
    if not project.is_dir() or not package_path.is_file():
        raise ValueError("expected a PEKAT project directory with pekat_package.json")
    try:
        package = json.loads(package_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid pekat_package.json: {exc}") from exc
    if not isinstance(package, dict) or str(package.get("version")) != "4.0.3":
        raise ValueError("training-history analyzer supports exact PEKAT 4.0.3 only")
    return package


def inspect_training_history(project: Path, family: str, model_id: int | None = None) -> dict[str, Any]:
    project = project.expanduser().resolve()
    package = _assert_exact_project(project)
    normalized_family = family.casefold()
    if normalized_family not in FAMILIES:
        raise ValueError(f"unsupported model family: {family}")
    database, folder = FAMILIES[normalized_family]
    db_path = project / "database" / database
    models = _rows(restricted_loads(db_path.read_bytes())) if db_path.is_file() else []
    if model_id is not None:
        models = [model for model in models if model.get("id") == model_id]
    output = []
    for model in models:
        current_id = model.get("id")
        model_dir = project / folder / "models" / str(current_id)
        histories = []
        registry = _registry_history(model, database, current_id)
        if registry is not None:
            histories.append(registry)
        csv_path = model_dir / "step.csv"
        if csv_path.is_file():
            histories.append(parse_step_csv(csv_path))
        params = model.get("trainingParams") if isinstance(model.get("trainingParams"), dict) else {}
        evaluation = model.get("evaluationResults") if isinstance(model.get("evaluationResults"), dict) else {}
        output.append({
            "family": "anomaly" if normalized_family == "unsupervised" else normalized_family,
            "model_id": current_id, "module_id": model.get("moduleId"),
            "name": model.get("name", model.get("label")), "status": model.get("status"),
            "creation_date": model.get("creationDate"), "finished_time": model.get("finishedTime"),
            "progress": model.get("progress"),
            "configured": params.get("config") if isinstance(params.get("config"), dict) else None,
            "training_image_count": len(model.get("trainingImages") or []),
            "test_image_count": len(model.get("testImages") or []),
            "evaluation_metrics": evaluation.get("metrics") if isinstance(evaluation.get("metrics"), dict) else None,
            "histories": histories, "artifacts": _artifact_inventory(model_dir, project),
            "provenance": {"registry": f"database/{database}", "artifact_root": f"{folder}/models/<model-id>"},
        })
    return {
        "schema": "pekat-training-history/0.1", "project": package.get("name", project.name),
        "version_scope": "4.0.3", "family": normalized_family, "models": output,
        "model_count": len(output), "read_only": True,
        "safety": {"weights_deserialized": False, "binary_sources": "inventory_only"},
        "unknowns": [
            "Metric cadence and semantics are unknown unless an explicit persisted field/header states them.",
            "Artifact existence does not establish a writer contract or runtime use.",
        ],
    }


def interpret_curves(train: list[float], validation: list[float], *, lower_is_better: bool = True) -> dict[str, Any]:
    """Classify deterministic curve shapes as compatible evidence, never proof."""
    if len(train) < 4 or len(validation) < 4 or len(train) != len(validation):
        code = "INSUFFICIENT_EVIDENCE"
        rationale = "Comparable train and validation series with at least four points are required."
        next_step = "Obtain a provenance-matched validation series; do not diagnose from training loss alone."
    else:
        sign = 1 if lower_is_better else -1
        train_delta = sign * (train[-1] - train[0])
        validation_delta = sign * (validation[-1] - validation[0])
        best_index = (min(range(len(validation)), key=validation.__getitem__) if lower_is_better
                      else max(range(len(validation)), key=validation.__getitem__))
        tail = validation[best_index:]
        reversals = sum((tail[i] - tail[i - 1]) * (tail[i - 1] - tail[i - 2]) < 0
                        for i in range(2, len(tail)))
        best_to_final = sign * (validation[-1] - validation[best_index])
        if reversals >= 2:
            code, rationale = "NOISY_VALIDATION", "Validation direction repeatedly reverses after its best point."
            next_step = "Check validation size, class balance, labels and acquisition consistency before retuning training."
        elif train_delta < 0 and best_index < len(validation) - 1 and best_to_final > 0:
            code = "OVERFITTING_COMPATIBLE"
            rationale = "Training improves while validation is worse after an earlier best point."
            next_step = "Check split representativeness and leakage; consider shorter training or early stopping next run."
        elif len(set(train)) == 1 and len(set(validation)) == 1:
            code = "PLATEAU_COMPATIBLE_WITH_UNDERFITTING"
            rationale = "Train and validation curves both remain flat without a widening gap."
            next_step = "Check data/annotation quality and model capacity; exact PEKAT parameter mapping may remain open."
        elif train_delta < 0 and validation_delta < 0:
            code = "STABLE_CONVERGENCE_COMPATIBLE"
            rationale = "Train and validation curves improve in the same direction."
            next_step = "Validate on an independent representative holdout and inspect per-class errors."
        else:
            code, rationale = "INDETERMINATE_PATTERN", "The curve directions do not support one bounded pattern."
            next_step = "Inspect provenance, metric definition and per-class examples before recommending a change."
    return {
        "classification": code, "claim_strength": "compatible evidence, not proof", "rationale": rationale,
        "recommended_next_read_only_test": next_step, "evidence_level": "OFFLINE_PARSED_ARTIFACT",
    }


def analyze_model_training(project: Path, family: str, model_id: int) -> dict[str, Any]:
    history = inspect_training_history(project, family, model_id)
    if not history["models"]:
        raise ValueError("model was not found in the selected family registry")
    model = history["models"][0]
    registry_loss = next((item for item in model["histories"] if "loss" in item.get("columns", [])), None)
    if not registry_loss or not registry_loss["points"]:
        interpretation = {
            "classification": "INSUFFICIENT_EVIDENCE", "claim_strength": "no curve diagnosis",
            "rationale": "No persisted provenance-matched validation curve is available.",
            "recommended_next_read_only_test": "Inspect final metrics, split integrity and family-specific artifacts.",
        }
    else:
        values = [point["loss"] for point in registry_loss["points"]]
        interpretation = {
            "classification": "TRAIN_LOSS_ONLY", "claim_strength": "descriptive only",
            "rationale": f"Persisted training loss contains {len(values)} points; validation divergence cannot be assessed.",
            "best_observed_step_index": min(range(len(values)), key=values.__getitem__),
            "best_observed_loss": min(values),
            "recommended_next_read_only_test": "Correlate independent evaluation metrics and verify train/test provenance.",
        }
    return {"history": history, "interpretation": interpretation, "read_only": True}


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only exact-4.0.3 PEKAT training-history analyzer")
    parser.add_argument("project", type=Path)
    parser.add_argument("--family", required=True, choices=sorted(FAMILIES))
    parser.add_argument("--model-id", type=int)
    parser.add_argument("--output", type=Path, help="write JSON outside the PEKAT project")
    args = parser.parse_args(argv)
    try:
        report = (analyze_model_training(args.project, args.family, args.model_id)
                  if args.model_id is not None else inspect_training_history(args.project, args.family))
        if args.output and _is_within(args.output, args.project):
            raise ValueError("output must be outside the PEKAT project")
    except (OSError, UnicodeError, ValueError, UnsafePickleError) as exc:
        parser.error(str(exc))
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.expanduser().resolve().write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
