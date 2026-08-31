import json
import pickle
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate as validate_schema

from analyze_flow_database import UnsafePickleError
from analyze_source_state_403 import analyze_source_state
from generate_code_module import ModuleSpec, ModuleSpecError


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".github" / "skills" / "pekat-vision"


def spec_403() -> dict:
    return json.loads((ROOT / "tests" / "fixtures" / "module_spec_4_0_3.json").read_text(encoding="utf-8"))


def test_exact_403_code_form_build_normalizes_known_fields(tmp_path: Path) -> None:
    payload = ModuleSpec.from_mapping(spec_403()).build_payload(epoch_ms=1700000000000)
    module = payload["module"]
    assert payload["version"] == "4.0.3" and payload["type"] == "CODE"
    assert module["gpuSettings"] == [] and module["softDeletedDate"] is None
    assert module["formValues"] == {"threshold": 43, "enabled": True, "mode": "B"}
    number = next(item for item in module["form"] if item["type"] == "number")
    assert number["defaultValue"] == "42" and number["min"] == "0" and number["max"] == "100"
    select = next(item for item in module["form"] if item["type"] == "select")
    assert select["defaultValue"] == "2"
    assert ModuleSpec.from_mapping(spec_403()).write(tmp_path / "module", epoch_ms=1700000000000).suffix == ".ptool"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda value: value.update(source_code="def main(context):\n    pass\n"), "main\\(context, form\\)"),
        (lambda value: value["form"].__setitem__(0, {"type": "date", "formKey": "x", "label": "X", "defaultValue": "x", "visibility": ""}), "unsupported form type"),
        (lambda value: value["form"][0].update(visibility="conditional"), "visibility"),
        (lambda value: value["form"][1].pop("min"), "requires min and max"),
        (lambda value: value["form"][3].update(options=""), "requires semicolon-separated"),
        (lambda value: value.update(form_values={"unknown": 1}), "unknown keys"),
    ],
)
def test_exact_403_rejects_outside_accepted_subset(change, message: str) -> None:
    value = spec_403()
    change(value)
    with pytest.raises(ModuleSpecError, match=message):
        ModuleSpec.from_mapping(value)


def test_exact_403_schema_requires_visibility_and_numeric_number_bounds() -> None:
    schema = json.loads((SKILL / "references" / "module_spec.schema.json").read_text(encoding="utf-8"))
    validate_schema(spec_403(), schema)
    invalid = spec_403()
    invalid["form"][1]["min"] = "0"
    with pytest.raises(ValidationError):
        validate_schema(invalid, schema)


def test_source_state_helper_is_read_only_and_version_gated(tmp_path: Path) -> None:
    project = tmp_path / "fixture"
    database = project / "database"
    database.mkdir(parents=True)
    (project / "pekat_package.json").write_text(json.dumps({"version": "4.0.3", "port": 8070}), encoding="utf-8")
    camera = {"provider": "folder", "currentCamera": None, "cameraStatus": "camera.status.notAvailable", "cameraIsRunning": False, "imageFolderWatcher": {"folderPath": "synthetic", "simulationMode": False, "analyzeExisting": True, "autoDelete": False}}
    running = {"processing": True, "save": False}
    (database / "camera.db").write_bytes(pickle.dumps(camera, protocol=4))
    (database / "running.db").write_bytes(pickle.dumps(running, protocol=4))
    report = analyze_source_state(project)
    assert report["read_only"] is True
    assert report["stored_persistent_evidence"]["analyze_incoming"] is True
    assert report["stored_persistent_evidence"]["auto_capture_save"] is False
    assert report["runtime_checks"]["camera_acquisition"] == "unknown_live_state"
    (project / "pekat_package.json").write_text(json.dumps({"version": "4.0.1"}), encoding="utf-8")
    with pytest.raises(ValueError, match="exact PEKAT 4.0.3"):
        analyze_source_state(project)
    (project / "pekat_package.json").write_text(json.dumps({"version": "4.0.3"}), encoding="utf-8")
    (database / "camera.db").write_bytes(b"cos\nsystem\n.")
    with pytest.raises(UnsafePickleError):
        analyze_source_state(project)


def test_backported_safety_knowledge_is_explicit() -> None:
    source = (SKILL / "references" / "source-state-pekat403.md").read_text(encoding="utf-8")
    gate = (SKILL / "references" / "flow-database-projects.md").read_text(encoding="utf-8")
    workflow = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for value in ("running.processing", "running.save", "UNSUPPORTED_CONTRACT_GAP", "notAvailable", "project-wide"):
        assert value in source
    for value in ("valueType=\"boolean\"", "NOT_EQUAL", "multi-rule", "not a public\nwriter"):
        assert value in gate
    assert "Read/schema evidence != runtime evidence != writer contract" in workflow
