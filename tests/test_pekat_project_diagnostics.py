import json
from pathlib import Path

from pekat_project_diagnostics import diagnose_project, render


def test_read_only_project_inventory_and_log_summary(tmp_path: Path):
    project = tmp_path / "DemoProject"
    (project / "database").mkdir(parents=True)
    (project / "database_old").mkdir()
    (project / "logs").mkdir()
    (project / "database" / "running.db").write_bytes(b"state")
    (project / "config-basler.yaml").write_text("camera: demo", encoding="utf-8")
    (project / "pekat_package.json").write_text(
        json.dumps({
            "name": "Demo", "version": "4.0.1", "port": 8100,
            "gpuIndex": 0, "cpuIndex": 2, "autoStart": False,
        }),
        encoding="utf-8",
    )
    (project / "logs" / "output.log").write_text(
        "SERVER - 2026-08-13 11:00:00,000 - runtime - ERROR - Model not loaded before inference\n",
        encoding="utf-8",
    )

    report = diagnose_project(project)

    assert report["read_only"] is True
    assert report["project"]["name"] == "Demo"
    assert report["project"]["version"] == "4.0.1"
    assert report["project"]["configured_port"] == 8100
    assert report["filesystem"]["database_old"] is True
    assert report["filesystem"]["images"] is False
    assert report["filesystem"]["running_db_present"] is True
    assert report["filesystem"]["running_db_interpretation"] == "state_file_only_not_process_liveness"
    assert report["runtime"]["requested"] is False
    assert report["runtime"]["configured_port"] == "not_requested"
    assert report["logs"]["recent_error_records"] == 1
    assert report["camera"]["stored_configuration_files"][0]["path"] == "config-basler.yaml"
    assert "not proof of a live process" in render(report)


def test_missing_and_invalid_optional_metadata_is_reported(tmp_path: Path):
    project = tmp_path / "Empty"
    project.mkdir()
    report = diagnose_project(project)
    assert report["project"]["name"] == "Empty"
    assert report["project"]["package_error"] == "pekat_package.json not found"
    assert report["logs"]["count"] == 0
    assert report["flow"]["status"] == "not_requested"

    (project / "pekat_package.json").write_text("[]", encoding="utf-8")
    invalid = diagnose_project(project)
    assert invalid["project"]["package_error"] == "pekat_package.json root is not an object"
