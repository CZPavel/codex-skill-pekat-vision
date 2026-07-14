import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / ".github" / "skills" / "pekat-vision"
PRIVATE_IP = re.compile(r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b")


def test_skill_contains_only_expected_resource_types():
    allowed = {".md", ".py", ".yaml", ".json", ".pmodule", ".ptool"}
    for path in SKILL.rglob("*"):
        if "__pycache__" in path.parts:
            continue
        if path.is_file():
            assert path.suffix.lower() in allowed, path
            assert path.name not in {"CHANGELOG.md", "project_context.md"}


def test_no_private_data_or_unsafe_tls_setting():
    forbidden = ["verify" + "=False", "Confluence_credentials", "API token atlassian"]
    for path in SKILL.rglob("*"):
        if "__pycache__" in path.parts:
            continue
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert not PRIVATE_IP.search(text), path
        assert not any(value.lower() in text.lower() for value in forbidden), path
    python_text = "\n".join(path.read_text(encoding="utf-8") for path in (SKILL / "scripts").glob("*.py"))
    assert "module_item" not in python_text


def test_schema_and_golden_suite_are_valid():
    schema = json.loads((SKILL / "references" / "module_spec.schema.json").read_text(encoding="utf-8"))
    assert schema["title"] == "PEKAT Code ModuleSpec"
    golden = yaml.safe_load((REPO / "tests" / "fixtures" / "golden_questions.yaml").read_text(encoding="utf-8"))
    assert golden["count"] == 48
    assert len(golden["cases"]) == 48

    required = {
        "id",
        "variant",
        "category",
        "question",
        "expected_document_ids",
        "expected_version",
        "safety_conditions",
        "expected_answer",
    }
    identifiers = []
    category_variants: dict[str, set[int]] = {}
    reference_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".yaml", ".py"}
    )
    for case in golden["cases"]:
        assert required == set(case), case.get("id")
        assert all(case[field] for field in required), case["id"]
        assert case["expected_version"] == "route_from_question"
        assert all(document_id in reference_text for document_id in case["expected_document_ids"])
        identifiers.append(case["id"])
        category_variants.setdefault(case["category"], set()).add(case["variant"])

    assert len(identifiers) == len(set(identifiers))
    assert set(category_variants) == {
        "abi",
        "barcode",
        "camera",
        "form319",
        "form401",
        "global",
        "iodd",
        "mxreset",
        "plcwrite",
        "rest",
        "result",
        "unknownver",
    }
    assert all(variants == {1, 2, 3, 4} for variants in category_variants.values())


def test_representative_adversarial_cases_are_present():
    text = (REPO / "tests" / "fixtures" / "golden_questions.yaml").read_text(encoding="utf-8").lower()
    assert "globaldata" in text
    assert "process-data map" in text
    assert "production plc" in text
