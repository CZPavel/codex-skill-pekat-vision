import json
import pickle
import zipfile

import pytest

from analyze_flow_database import (
    UnsafePickleError,
    analyze_code,
    analyze_project,
    module_execution_state,
    parse_flow_sort,
    restricted_loads,
)


class PicklePayload:
    pass


def module_db():
    return {
        "items": [
            {
                "id": 1,
                "type": "CODE",
                "label": "Set state",
                "softDeletedDate": None,
                "sourceCode": (
                    "import requests\n"
                    "def main(context):\n"
                    "    gd = context.get('globalData')\n"
                    "    context['flag'] = context.get('result')\n"
                    "    gd['counter'] = gd.get('counter', 0) + 1\n"
                ),
            },
            {
                "id": 2,
                "type": "FILTER",
                "label": "Gate",
                "softDeletedDate": None,
                "isActive": False,
                "evalType": "CONTEXT",
                "contextNode": {"path": "flag"},
                "rules": [{"operator": "EQUALS", "value": True}],
            },
            {"id": 3, "type": "DETECTOR", "label": "Detector", "softDeletedDate": None},
            {
                "id": 4,
                "type": "CODE",
                "label": "Deleted",
                "softDeletedDate": 1700000000,
                "isActive": True,
                "sourceCode": "def main(context):\n    pass\n",
            },
        ],
        "sort": [1, [[2, 3], []]],
        "filter": [],
        "lastUpdate": 1700000000000,
    }


def write_database(root, db, *, old=None):
    database = root / "database"
    database.mkdir(parents=True)
    (database / "modules.db").write_bytes(pickle.dumps(db, protocol=4))
    (database / "camera.db").write_bytes(pickle.dumps({"provider": "test"}, protocol=4))
    if old is not None:
        database_old = root / "database_old"
        database_old.mkdir()
        (database_old / "modules.db").write_bytes(pickle.dumps(old, protocol=4))
        (database_old / "camera.db").write_bytes(pickle.dumps({"provider": "old"}, protocol=4))


def test_restricted_reader_round_trips_primitives_only():
    value = {"items": [1, "text", None, True, 1.5, b"x"], "sort": [1, [[2], []]]}
    assert restricted_loads(pickle.dumps(value, protocol=4)) == value


def test_restricted_reader_rejects_dangerous_object_construction():
    with pytest.raises(UnsafePickleError, match="STACK_GLOBAL|NEWOBJ"):
        restricted_loads(pickle.dumps(PicklePayload(), protocol=4))


def test_restricted_reader_rejects_non_protocol_4():
    with pytest.raises(UnsafePickleError, match="protocol 4"):
        restricted_loads(pickle.dumps({"items": []}, protocol=3))


def test_modules_sort_parallelism_including_empty_branch():
    index = {1: {"type": "CODE", "label": "A"}, 2: {"type": "FILTER"}, 3: {"type": "CODE"}}
    tree = parse_flow_sort([1, [[2, 3], []]], index)
    parallel = tree["nodes"][1]
    assert parallel["kind"] == "parallel"
    assert [node["id"] for node in parallel["branches"][0]["nodes"]] == [2, 3]
    assert parallel["branches"][1]["nodes"] == []


def test_module_state_contract_handles_missing_isactive():
    assert module_execution_state({"softDeletedDate": None}, True) == "active_candidate"
    assert module_execution_state({"softDeletedDate": None, "isActive": False}, True) == "disabled"
    assert module_execution_state({"softDeletedDate": 1, "isActive": True}, False) == "soft_deleted"


def test_analyze_directory_reports_flow_states_filter_and_code(tmp_path):
    write_database(tmp_path, module_db())
    report = analyze_project(tmp_path)
    current = report["database_layers"][0]
    states = {row["id"]: row["execution_state"] for row in current["modules"]}
    assert states == {1: "active_candidate", 2: "disabled", 3: "active_candidate", 4: "soft_deleted"}
    assert current["filters"][0]["evalType"] == "CONTEXT"
    assert current["filters"][0]["contextNode"] == {"path": "flag"}
    code = current["code_inventory"][0]
    assert code["context_reads"] == ["globalData", "result"]
    assert code["context_writes"] == ["flag"]
    assert code["globaldata_reads"] == ["counter"]
    assert code["globaldata_writes"] == ["counter"]
    assert "network_or_cross_pekat" in code["side_effects"]
    assert "Branch 2 (empty)" in "\n".join(current["flow_text"])


def test_database_old_is_separate_and_diffed(tmp_path):
    old = module_db()
    current = module_db()
    current["items"][0]["label"] = "Migrated label"
    write_database(tmp_path, current, old=old)
    report = analyze_project(tmp_path)
    assert [layer["layer"] for layer in report["database_layers"]] == ["database", "database_old"]
    diff = report["migration_diff"]
    assert diff["database_old_role"].endswith("not_live_flow")
    assert diff["same_flow_sort"] is True
    assert diff["changed_files"] == ["camera.db", "modules.db"]


def test_analyze_database_zip_without_extraction(tmp_path):
    project = tmp_path / "project"
    write_database(project, module_db())
    archive = tmp_path / "project.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        for path in project.rglob("*"):
            if path.is_file():
                output.write(path, "wrapped/" + path.relative_to(project).as_posix())
        output.writestr("wrapped/pekat_package.json", json.dumps({"pekatVersion": "4.0.1"}))
    report = analyze_project(archive)
    assert report["source_kind"] == "zip"
    assert report["explicit_project_metadata"][0]["explicit_fields"] == {"pekatVersion": "4.0.1"}
    assert report["database_layers"][0]["flow_sort"] == [1, [[2, 3], []]]


def test_analyze_code_reports_invalid_syntax_without_execution():
    result = analyze_code("def main(:\n    pass")
    assert result["syntax"].startswith("invalid:")


def test_report_is_json_serializable(tmp_path):
    write_database(tmp_path, module_db())
    json.dumps(analyze_project(tmp_path))
