import ast
import json
from pathlib import Path

import pytest
from jsonschema import validate as validate_schema

from generate_code_module import ModuleSpec, ModuleSpecError

SOURCE = "def main(context, form=None):\n    values = form or {}\n    context['fixture_values'] = values\n"


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
    with pytest.raises(ModuleSpecError, match=r"main\(context, form=None\)"):
        ModuleSpec.from_mapping(bad)


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
