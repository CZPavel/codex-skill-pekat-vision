from pathlib import Path

from analyze_pekat_log import analyze_log_target, parse_file, render


def _line(timestamp: str, severity: str, message: str) -> str:
    return f"SERVER - {timestamp} - pekat.runtime - {severity} - {message}"


def test_single_error_is_reported_as_one_root_candidate(tmp_path: Path):
    log = tmp_path / "output.log"
    log.write_text(
        _line("2026-08-13 07:00:00,000", "ERROR", "Project server startup failed") + "\n",
        encoding="utf-8",
    )
    report = analyze_log_target(log)
    assert report["error_records"] == 1
    assert report["unique_error_families"] == 1
    assert report["first_root_cause_candidates"][0]["category"] == "project_start"


def test_groups_multiline_and_normalized_duplicate_errors(tmp_path: Path):
    log = tmp_path / "output.log"
    log.write_text(
        "orphan malformed line\n"
        + _line("2026-08-13 08:00:00,000", "ERROR", "Error analyzing image")
        + "\nTraceback (most recent call last):\n"
        + '  File "C:\\projects\\demo\\tool.py", line 7, in main\n'
        + "ValueError: bad čidlo 17\n"
        + _line("2026-08-13 08:00:01,000", "ERROR", "Error analyzing image")
        + "\nTraceback (most recent call last):\n"
        + '  File "C:\\projects\\demo\\tool.py", line 91, in main\n'
        + "ValueError: bad čidlo 42\n",
        encoding="utf-8",
    )

    records, unparsed = parse_file(log)
    report = analyze_log_target(log)

    assert len(records) == 2
    assert records[0].continuation[-1] == "ValueError: bad čidlo 17"
    assert len(unparsed) == 1
    assert report["error_records"] == 2
    assert report["unique_error_families"] == 1
    family = report["top_error_families"][0]
    assert family["count"] == 2
    assert family["terminal_exception"] == "ValueError: bad čidlo 17"
    assert family["category"] == "code_flow"
    assert report["unparsed_line_count"] == 1
    output = render(report)
    assert "TOP ERROR FAMILIES" in output
    assert "REPEATED SECONDARY ERRORS" in output
    assert "LIKELY SUBSYSTEM" in output


def test_logger_sessions_filters_identities_and_sanitized_evidence(tmp_path: Path):
    log = tmp_path / "output.log.2026_09_09.log"
    log.write_text(
        "\n".join([
            _line("2026-09-09 10:00:00,000", "INFO", "Project server startup"),
            "SERVER - 2026-09-09 10:00:01,000 - runtime.camera - ERROR - ModuleId=7 failed at C:\\synthetic\\a.png",
            "ValueError: invalid sample 10 token=secret-value",
            "SERVER - 2026-09-09 10:00:02,000 - runtime.camera - ERROR - ModuleId=7 failed at C:\\synthetic\\b.png",
            "ValueError: invalid sample 11 token=other-value",
            _line("2026-09-09 11:00:00,000", "INFO", "Project server startup"),
            _line("2026-09-09 11:00:01,000", "ERROR", "TypeError: separate"),
        ]),
        encoding="utf-8-sig",
    )
    records, _ = parse_file(log)
    assert records[1].logger == "runtime.camera"
    report = analyze_log_target(tmp_path)
    assert len(report["sessions"]) == 2
    assert report["affected_identities"]["module_ids"] == [7]
    repeated = next(row for row in report["incidents"] if row["count"] == 2)
    assert repeated["first_timestamp"].endswith("01,000")
    assert repeated["last_timestamp"].endswith("02,000")
    assert "synthetic\\a.png" not in repeated["supporting_evidence"]
    assert "secret-value" not in repeated["supporting_evidence"]
    assert report["target"] == "<selected-target>"
    assert all(not Path(name).is_absolute() for name in report["files"])

    last = analyze_log_target(tmp_path, last_session=True, severities=["ERROR"], component="runtime")
    assert last["record_count"] == 1
    timed = analyze_log_target(tmp_path, since="2026-09-09 10:00:02", until="2026-09-09 10:00:02")
    assert timed["record_count"] == 1


def test_empty_log_is_a_valid_zero_record_report(tmp_path: Path):
    log = tmp_path / "output.log"
    log.write_text("", encoding="utf-8")
    report = analyze_log_target(log)
    assert report["record_count"] == 0
    assert report["incidents"] == []
    assert report["range"] == {"first": None, "last": None}


def test_rotated_project_logs_and_pm_style_daily_log_are_discovered(tmp_path: Path):
    project_logs = tmp_path / "project" / "logs"
    project_logs.mkdir(parents=True)
    (project_logs / "output.log").write_text(
        _line("2026-09-09 09:00:00,000", "INFO", "active"), encoding="utf-8"
    )
    (project_logs / "output.log.2026_09_08.log").write_text(
        _line("2026-09-08 09:00:00,000", "WARNING", "rotated"), encoding="utf-8"
    )
    assert len(analyze_log_target(tmp_path / "project")["files"]) == 2

    pm_logs = tmp_path / "pekat_vision" / "logger"
    pm_logs.mkdir(parents=True)
    (pm_logs / "starter_2026-09-09.log").write_text(
        _line("2026-09-09 09:00:00.000", "ERROR", "port=8070 collision at 192.0.2.8 secret=synthetic"),
        encoding="utf-8",
    )
    report = analyze_log_target(pm_logs)
    assert report["record_count"] == 1
    assert report["affected_identities"]["ports"] == [8070]
    assert "192.0.2.8" not in report["incidents"][0]["supporting_evidence"]
    assert "synthetic" not in report["incidents"][0]["supporting_evidence"]


def test_camera_chain_prefers_search_failure_over_secondary_init_noise(tmp_path: Path):
    log = tmp_path / "output.log"
    lines = [
        _line("2026-08-13 09:00:00,000", "ERROR", "Camera search failed: no camera connections"),
        _line("2026-08-13 09:00:01,000", "ERROR", "Camera is not initialized; grab error"),
        _line("2026-08-13 09:00:02,000", "ERROR", "Camera is not initialized; grab error"),
    ]
    log.write_bytes(("\n".join(lines) + "\ninvalid byte: ").encode("utf-8") + b"\xff\n")

    report = analyze_log_target(log)

    assert report["first_root_cause_candidates"][0]["message"].startswith("Camera search failed")
    secondary = next(row for row in report["top_error_families"] if "not initialized" in row["message"])
    assert secondary["likely_secondary"] is True
    assert secondary["count"] == 2
    assert secondary["category"] == "camera"


def test_model_and_filesystem_categories_are_separate(tmp_path: Path):
    log = tmp_path / "output.log"
    log.write_text(
        _line("2026-08-13 10:00:00,000", "ERROR", "Model is not loaded before inference")
        + "\n"
        + _line("2026-08-13 10:00:01,000", "ERROR", "Image saver root folder does not exist")
        + "\n",
        encoding="utf-8",
    )
    categories = {row["category"] for row in analyze_log_target(log)["top_error_families"]}
    assert categories == {"model", "filesystem"}
