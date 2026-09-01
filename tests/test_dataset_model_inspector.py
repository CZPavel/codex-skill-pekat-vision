import json
import pickle
from pathlib import Path

import pytest

from analyze_flow_database import UnsafePickleError
from inspect_dataset_model import inspect_dataset_model


def write_project(root: Path, *, version: str = "4.0.3") -> Path:
    (root / "database").mkdir(parents=True)
    (root / "images").mkdir()
    (root / "pekat_package.json").write_text(json.dumps({"name": "synthetic", "version": version}), encoding="utf-8")
    (root / "database" / "images.db").write_bytes(pickle.dumps([{"id": 1, "tags": [10]}, {"id": 2, "tags": []}], protocol=4))
    (root / "database" / "tags.db").write_bytes(pickle.dumps([{"id": 10, "label": "ok"}], protocol=4))
    (root / "database" / "modules.db").write_bytes(pickle.dumps({"items": [{"id": 4, "type": "DETECTOR", "classNames": [{"id": 2, "label": "part"}], "imageRectangles": {"1": [{"id": 7, "classNameId": 2, "x": 1, "y": 2, "width": 3, "height": 4, "percent": True}], "2": []}}]}, protocol=4))
    (root / "database" / "detectorModels.db").write_bytes(pickle.dumps([{"id": 8, "name": "detector", "type": "DETECTOR", "trainingImages": [1], "testImages": [2], "trainingParams": {"config": {"TRAIN_RATIO": 80, "DATA_SPLIT_SEED": 0}}}], protocol=4))
    (root / "images" / "1.png").write_bytes(b"png")
    artifacts = root / "detector" / "models" / "8"
    artifacts.mkdir(parents=True)
    (artifacts / "data.json").write_text("{}", encoding="utf-8")
    return root


def test_inspector_reports_inventory_provenance_annotations_and_no_project_side_effect(tmp_path: Path) -> None:
    project = write_project(tmp_path / "project")
    before = {path.relative_to(project): path.stat().st_mtime_ns for path in project.rglob("*") if path.is_file()}
    report = inspect_dataset_model(project)
    after = {path.relative_to(project): path.stat().st_mtime_ns for path in project.rglob("*") if path.is_file()}
    assert before == after and report["read_only"] is True
    assert report["models"][0]["train_source_field"] == "trainingImages"
    assert [item["annotation_state"] for item in report["detector_annotation_states"]] == ["PRESENT_NONEMPTY", "PRESENT_EMPTY"]
    assert report["detector_annotations"][0]["class"]["label"] == "part"
    assert report["models"][0]["artifacts"][0]["path"] == "detector/models/8/data.json"
    assert {item["code"] for item in report["qa_findings"]} == {"missing_image_file"}


def test_inspector_rejects_unsupported_version_and_conflicting_aliases(tmp_path: Path) -> None:
    project = write_project(tmp_path / "project", version="4.0.1")
    with pytest.raises(ValueError, match="exact PEKAT 4.0.3"):
        inspect_dataset_model(project)
    (project / "pekat_package.json").write_text(json.dumps({"version": "4.0.3"}), encoding="utf-8")
    (project / "database" / "detectorModels.db").write_bytes(pickle.dumps([{"id": 8, "type": "DETECTOR", "trainingImages": [1], "trainImageIds": [2]}], protocol=4))
    report = inspect_dataset_model(project)
    assert report["models"][0]["train_image_ids"] == []
    assert report["qa_findings"][-1]["code"] == "ambiguous_split_field_alias"


def test_inspector_rejects_malformed_or_unsafe_pickle(tmp_path: Path) -> None:
    project = write_project(tmp_path / "project")
    (project / "database" / "images.db").write_bytes(b"cos\nsystem\n.")
    with pytest.raises(UnsafePickleError):
        inspect_dataset_model(project)
