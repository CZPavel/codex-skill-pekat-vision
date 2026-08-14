import ast
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate as validate_schema

from generate_code_module import ModuleSpec, ModuleSpecError

SOURCE = "def main(context, form):\n    values = form if isinstance(form, dict) else {}\n    context['fixture_values'] = values\n"


def mapping(version):
    return {
        "target_version": version,
        "label": "All forms",
        "source_code": SOURCE,
        "form": [
            {"type": "text", "formKey": "caption", "label": "Caption", "defaultValue": "test"},
            {"type": "number", "formKey": "threshold", "label": "Threshold", "defaultValue": "5", "min": "0", "max": "10"},
            {"type": "checkbox", "formKey": "enabled", "label": "Enabled", "defaultValue": "true"},
            {"type": "select", "formKey": "mode", "label": "Mode", "defaultValue": "safe", "options": "safe;diagnostic"},
        ],
        "form_values": {"threshold": "6.5", "enabled": "false", "mode": "safe"},
    }


@pytest.mark.parametrize(("version", "extension"), [("3.19.3", ".pmodule"), ("4.0.1", ".ptool")])
def test_all_forms_version_extension_and_ids(version, extension, tmp_path):
    spec = ModuleSpec.from_mapping(mapping(version))
    path = spec.write(tmp_path / "module", epoch_ms=1700000000000)
    assert path.suffix == extension
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["version"] == version
    assert {item["type"] for item in payload["module"]["form"]} == {"text", "number", "checkbox", "select"}
    if version == "4.0.1":
        assert all(isinstance(item["visibility"], str) for item in payload["module"]["form"])
        assert all(item["visibility"] == "" for item in payload["module"]["form"])
    number_item = next(item for item in payload["module"]["form"] if item["type"] == "number")
    assert number_item["defaultValue"] == "5"
    assert payload["module"]["formValues"] == {"threshold": 6.5, "enabled": False, "mode": "safe"}
    ids = [payload["module"]["id"], *[item["id"] for item in payload["module"]["form"]]]
    assert len(ids) == len(set(ids)) and all(isinstance(value, int) for value in ids)
    ast.parse(payload["module"]["sourceCode"])


def test_unknown_form_value_and_wrong_entrypoint_are_rejected():
    bad = mapping("3.19.3")
    bad["form_values"] = {"unknown": 1}
    with pytest.raises(ModuleSpecError, match="unknown keys"):
        ModuleSpec.from_mapping(bad)
    bad = mapping("3.19.3")
    bad["source_code"] = "def main(context, module_item=None):\n    pass\n"
    with pytest.raises(ModuleSpecError, match=r"main\(context, form\)"):
        ModuleSpec.from_mapping(bad)


def test_version_aware_entrypoints_without_form():
    base = {"label": "No form", "form": [], "form_values": {}}
    ModuleSpec.from_mapping({**base, "target_version": "3.19.3", "source_code": "def main(context):\n    pass\n"})
    ModuleSpec.from_mapping({**base, "target_version": "3.19.3", "source_code": "def main(context, form):\n    pass\n"})
    ModuleSpec.from_mapping({**base, "target_version": "4.0.1", "source_code": "def main(context):\n    pass\n"})
    with pytest.raises(ModuleSpecError, match="without Form"):
        ModuleSpec.from_mapping({**base, "target_version": "4.0.1", "source_code": "def main(context, form):\n    pass\n"})


def test_select_accepts_observed_index_default():
    value = mapping("4.0.1")
    select = next(item for item in value["form"] if item["type"] == "select")
    select["defaultValue"] = "0"
    value["form_values"]["mode"] = "1"
    payload = ModuleSpec.from_mapping(value).build_payload(epoch_ms=1700000000000)
    selected = next(item for item in payload["module"]["form"] if item["type"] == "select")
    assert selected["defaultValue"] == "0"
    assert payload["module"]["formValues"]["mode"] == "1"


def test_distributed_fixtures_match_contract():
    fixture_dir = Path(__file__).resolve().parents[1] / ".github" / "skills" / "pekat-vision" / "assets" / "fixtures"
    fixtures = sorted(fixture_dir.iterdir())
    assert {path.suffix for path in fixtures} == {".pmodule", ".ptool"}
    for path in fixtures:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["type"] == "CODE"
        assert {item["type"] for item in payload["module"]["form"]} == {"text", "number", "checkbox", "select"}


def test_modulespec_json_schema_accepts_all_form_types():
    schema_path = Path(__file__).resolve().parents[1] / ".github" / "skills" / "pekat-vision" / "references" / "module_spec.schema.json"
    validate_schema(mapping("4.0.1"), json.loads(schema_path.read_text(encoding="utf-8")))


def test_401_visibility_rejects_boolean_and_unknown_expression():
    boolean_value = mapping("4.0.1")
    boolean_value["form"][0]["visibility"] = True
    with pytest.raises(ModuleSpecError, match="visibility must be a string"):
        ModuleSpec.from_mapping(boolean_value)

    expression_value = mapping("4.0.1")
    expression_value["form"][0]["visibility"] = "legacy_expression"
    with pytest.raises(ModuleSpecError, match="native-compatible empty string"):
        ModuleSpec.from_mapping(expression_value)

    schema_path = Path(__file__).resolve().parents[1] / ".github" / "skills" / "pekat-vision" / "references" / "module_spec.schema.json"
    with pytest.raises(ValidationError):
        validate_schema(expression_value, json.loads(schema_path.read_text(encoding="utf-8")))


def test_401_distributed_fixture_has_native_form_types_and_valid_source():
    path = Path(__file__).resolve().parents[1] / ".github" / "skills" / "pekat-vision" / "assets" / "fixtures" / "form_types_4_0_1.ptool"
    payload = json.loads(path.read_text(encoding="utf-8"))
    module = payload["module"]
    assert payload["version"] == "4.0.1"
    assert payload["type"] == "CODE"
    ast.parse(module["sourceCode"])
    keys = [item["formKey"] for item in module["form"]]
    ids = [module["id"], *[item["id"] for item in module["form"]]]
    assert set(keys) == {"caption", "threshold", "enabled", "mode"}
    assert len(keys) == len(set(keys))
    assert len(ids) == len(set(ids))
    assert all(isinstance(item["visibility"], str) and item["visibility"] == "" for item in module["form"])
    assert all(not isinstance(item["visibility"], bool) for item in module["form"])
    number_item = next(item for item in module["form"] if item["type"] == "number")
    select_item = next(item for item in module["form"] if item["type"] == "select")
    assert isinstance(number_item["min"], str) and isinstance(number_item["max"], str)
    assert isinstance(select_item["options"], str)
    assert set(module["formValues"]) <= set(keys)
