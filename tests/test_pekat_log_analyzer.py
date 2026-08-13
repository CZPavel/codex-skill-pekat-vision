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
