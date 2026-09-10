import pickle
from pathlib import Path

import pytest

from analyze_training_history import inspect_training_history, interpret_curves, parse_step_csv


def _project(tmp_path: Path, *, version: str = "4.0.3") -> Path:
    project = tmp_path / "fixture-project"
    (project / "database").mkdir(parents=True)
    (project / "pekat_package.json").write_text(
        '{"name":"fixture","version":"' + version + '"}', encoding="utf-8"
    )
    return project


def test_family_history_reads_safe_sources_and_only_inventories_weights(tmp_path: Path):
    project = _project(tmp_path)
    model_dir = project / "detector" / "models" / "42"
    model_dir.mkdir(parents=True)
    model = {
        "id": 42, "moduleId": 7, "name": "synthetic", "status": "COMPLETED",
        "loss": [3.0, 2.0, "bad", 1.0], "trainingImages": [1, 2], "testImages": [3],
        "trainingParams": {"config": {"ITERS": 4}},
    }
    (project / "database" / "detectorModels.db").write_bytes(pickle.dumps([model], protocol=4))
    (model_dir / "step.csv").write_text("epoch,box\n0,3\n1,2\n", encoding="utf-8")
    (model_dir / "best.pt").write_bytes(b"not-deserialized")
    (model_dir / "metadata.json").write_text('{"kind":"fixture"}', encoding="utf-8")

    report = inspect_training_history(project, "detector", 42)
    item = report["models"][0]
    assert report["version_scope"] == "4.0.3"
    assert item["training_image_count"] == 2
    assert item["histories"][0]["malformed_count"] == 1
    assert item["histories"][0]["provenance"].endswith("model[42].loss")
    weight = next(row for row in item["artifacts"] if row["path"].endswith("best.pt"))
    assert weight["deserialized"] is False
    assert report["safety"]["weights_deserialized"] is False


def test_csv_headerless_and_malformed_rows_keep_provenance(tmp_path: Path):
    path = tmp_path / "step.csv"
    path.write_text("1,2\n2,bad\n3,4\n", encoding="utf-8-sig")
    parsed = parse_step_csv(path)
    assert parsed["metric_semantics"] == "UNKNOWN_HEADERLESS_COLUMNS"
    assert parsed["malformed_rows"] == [2]
    assert parsed["provenance"] == "step.csv"


@pytest.mark.parametrize(
    ("train", "validation", "expected"),
    [
        ([5, 4, 3, 2, 1], [5, 3, 2, 3, 4], "OVERFITTING_COMPATIBLE"),
        ([5, 5, 5, 5], [6, 6, 6, 6], "PLATEAU_COMPATIBLE_WITH_UNDERFITTING"),
        ([5, 4, 3, 2], [6, 5, 4, 3], "STABLE_CONVERGENCE_COMPATIBLE"),
        ([5, 4], [6, 5], "INSUFFICIENT_EVIDENCE"),
    ],
)
def test_curve_interpretation_is_guarded(train, validation, expected):
    result = interpret_curves(train, validation)
    assert result["classification"] == expected
    assert "proof" in result["claim_strength"]


def test_non_403_project_and_binary_csv_are_rejected(tmp_path: Path):
    project = _project(tmp_path, version="4.0.4")
    with pytest.raises(ValueError, match="exact PEKAT 4.0.3"):
        inspect_training_history(project, "detector")
    binary = tmp_path / "weights.pt"
    binary.write_bytes(b"binary")
    with pytest.raises(ValueError, match="CSV only"):
        parse_step_csv(binary)


def test_family_specific_missing_curves_are_not_normalized(tmp_path: Path):
    project = _project(tmp_path)
    cases = {
        "classifier": ("classifierModels.db", "classifier"),
        "anomaly": ("unsupervisedModels.db", "unsupervised"),
        "ocr": ("ocrModels.db", "ocr"),
    }
    for family, (database, folder) in cases.items():
        (project / "database" / database).write_bytes(pickle.dumps([{"id": 1, "progress": 0.5}], protocol=4))
        report = inspect_training_history(project, family, 1)
        assert report["models"][0]["histories"] == []
        assert report["models"][0]["artifacts"] == []
        assert report["models"][0]["provenance"]["artifact_root"].startswith(folder)


def test_supervised_headerless_five_columns_remain_unknown(tmp_path: Path):
    project = _project(tmp_path)
    model_dir = project / "supervised" / "models" / "9"
    model_dir.mkdir(parents=True)
    (project / "database" / "supervisedModels.db").write_bytes(pickle.dumps([{"id": 9}], protocol=4))
    (model_dir / "step.csv").write_text("1,2,3,4,5\n2,3,4,5,6\n", encoding="utf-8")
    history = inspect_training_history(project, "supervised", 9)["models"][0]["histories"][0]
    assert history["columns"] == ["column_1", "column_2", "column_3", "column_4", "column_5"]
    assert history["metric_semantics"] == "UNKNOWN_HEADERLESS_COLUMNS"


def test_data_json_is_metadata_not_training_history(tmp_path: Path):
    project = _project(tmp_path)
    model_dir = project / "detector" / "models" / "4"
    model_dir.mkdir(parents=True)
    (project / "database" / "detectorModels.db").write_bytes(pickle.dumps([{"id": 4}], protocol=4))
    (model_dir / "data.json").write_text("{malformed", encoding="utf-8")
    model = inspect_training_history(project, "detector", 4)["models"][0]
    assert model["histories"] == []
    assert model["artifacts"][0]["parse_status"] == "malformed_or_unreadable"
