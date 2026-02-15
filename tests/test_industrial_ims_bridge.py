from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import industrial_ims_bridge as bridge  # noqa: E402


def _config(dry_run: bool) -> bridge.IntegrationConfig:
    return bridge.IntegrationConfig(
        mode="zos_connect",
        endpoint="https://example.test/ims",
        timeout_seconds=1.0,
        max_retries=3,
        backoff_seconds=0.0,
        dry_run=dry_run,
        ims_programview="PSB01",
        ims_database="DB01",
        ims_transaction="TRN01",
    )


def test_normalize_ot_payload_adds_defaults() -> None:
    normalized = bridge.normalize_ot_payload({"value": 123})
    assert normalized["tag"] == "unknown.tag"
    assert normalized["quality"] == "UNKNOWN"
    assert "timestamp" in normalized
    assert "correlation_id" in normalized


def test_map_ot_to_ims_request_keeps_quality_timestamp() -> None:
    mapped = bridge.map_ot_to_ims_request(
        {"tag": "line.a.temp", "value": 55.0, "quality": "GOOD", "timestamp": "2026-02-15T12:00:00Z"},
        _config(dry_run=True),
    )
    assert mapped["programView"] == "PSB01"
    assert mapped["otData"]["quality"] == "GOOD"
    assert mapped["otData"]["timestamp"] == "2026-02-15T12:00:00Z"
    assert "correlationId" in mapped


def test_retry_then_success() -> None:
    calls: list[int] = []

    def fake_post(_url: str, _payload: dict, _headers: dict, _timeout: float) -> tuple[int, str]:
        calls.append(1)
        if len(calls) < 3:
            raise TimeoutError("timeout")
        return 200, '{"ok":true}'

    result = bridge.process_ot_payload(
        {"tag": "line.a.temp", "value": 55.0, "quality": "GOOD"},
        config=_config(dry_run=False),
        post_fn=fake_post,
        sleep_fn=lambda _seconds: None,
    )
    assert result["status"] == "ok"
    assert result["attempts"] == 3


def test_dry_run_skips_network_call() -> None:
    called: list[bool] = []

    def fake_post(_url: str, _payload: dict, _headers: dict, _timeout: float) -> tuple[int, str]:
        called.append(True)
        return 200, "{}"

    result = bridge.process_ot_payload(
        {"tag": "line.a.temp", "value": 10},
        config=_config(dry_run=True),
        post_fn=fake_post,
    )
    assert result["status"] == "dry_run"
    assert called == []
