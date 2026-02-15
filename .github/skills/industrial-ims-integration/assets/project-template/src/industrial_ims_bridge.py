#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Tuple
from urllib import error, request

JsonDict = Dict[str, Any]
PostFn = Callable[[str, JsonDict, Dict[str, str], float], Tuple[int, str]]


@dataclass(frozen=True)
class IntegrationConfig:
    mode: str
    endpoint: str
    timeout_seconds: float
    max_retries: int
    backoff_seconds: float
    dry_run: bool
    ims_programview: str
    ims_database: str
    ims_transaction: str


def _env_bool(value: str, default: bool) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    return default


def load_config(env: Mapping[str, str] | None = None) -> IntegrationConfig:
    source = env if env is not None else os.environ
    return IntegrationConfig(
        mode=source.get("INTEGRATION_MODE", "zos_connect"),
        endpoint=source.get("IMS_ENDPOINT", "").strip(),
        timeout_seconds=float(source.get("IMS_TIMEOUT_SECONDS", "10")),
        max_retries=int(source.get("IMS_MAX_RETRIES", "3")),
        backoff_seconds=float(source.get("IMS_BACKOFF_SECONDS", "0.5")),
        dry_run=_env_bool(source.get("IMS_DRY_RUN", "true"), default=True),
        ims_programview=source.get("IMS_PROGRAMVIEW", "").strip(),
        ims_database=source.get("IMS_DATABASE", "").strip(),
        ims_transaction=source.get("IMS_TRANSACTION", "").strip(),
    )


def normalize_ot_payload(payload: JsonDict) -> JsonDict:
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dict.")
    normalized = dict(payload)
    normalized["tag"] = normalized.get("tag") or normalized.get("asset") or "unknown.tag"
    normalized.setdefault("quality", "UNKNOWN")
    normalized.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    normalized.setdefault("correlation_id", str(uuid.uuid4()))
    return normalized


def map_ot_to_ims_request(payload: JsonDict, config: IntegrationConfig) -> JsonDict:
    normalized = normalize_ot_payload(payload)
    return {
        "programView": config.ims_programview or normalized.get("programView", "UNSPECIFIED"),
        "databaseName": config.ims_database or normalized.get("databaseName", ""),
        "transaction": config.ims_transaction or normalized.get("transaction", ""),
        "otData": {
            "tag": normalized["tag"],
            "value": normalized.get("value"),
            "quality": normalized["quality"],
            "timestamp": normalized["timestamp"],
        },
        "correlationId": normalized["correlation_id"],
    }


def default_post_json(url: str, payload: JsonDict, headers: Dict[str, str], timeout_seconds: float) -> Tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return int(response.status), raw
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return int(exc.code), raw


def send_with_retry(
    config: IntegrationConfig,
    request_payload: JsonDict,
    post_fn: PostFn = default_post_json,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> JsonDict:
    if config.mode != "zos_connect":
        return {
            "status": "not_implemented",
            "mode": config.mode,
            "message": "Only zos_connect mode is implemented in this MVP.",
        }

    if config.dry_run:
        return {"status": "dry_run", "request": request_payload}
    if not config.endpoint:
        raise ValueError("IMS_ENDPOINT must be configured for non-dry-run mode.")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Correlation-ID": request_payload["correlationId"],
    }
    attempts = config.max_retries + 1

    for attempt in range(1, attempts + 1):
        try:
            status_code, response_body = post_fn(
                config.endpoint,
                request_payload,
                headers,
                config.timeout_seconds,
            )
        except (TimeoutError, error.URLError, ConnectionError) as exc:
            if attempt >= attempts:
                raise RuntimeError(f"HTTP call failed after {attempt} attempts: {exc}") from exc
            sleep_fn(config.backoff_seconds * (2 ** (attempt - 1)))
            continue

        if status_code == 429 or status_code >= 500:
            if attempt >= attempts:
                return {
                    "status": "error",
                    "http_status": status_code,
                    "attempts": attempt,
                    "body": response_body,
                }
            sleep_fn(config.backoff_seconds * (2 ** (attempt - 1)))
            continue

        if status_code >= 400:
            return {
                "status": "error",
                "http_status": status_code,
                "attempts": attempt,
                "body": response_body,
            }

        return {
            "status": "ok",
            "http_status": status_code,
            "attempts": attempt,
            "body": response_body,
        }

    raise RuntimeError("Unexpected retry loop exit.")


def process_ot_payload(
    payload: JsonDict,
    config: IntegrationConfig | None = None,
    post_fn: PostFn = default_post_json,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> JsonDict:
    active_config = config if config is not None else load_config()
    ims_request = map_ot_to_ims_request(payload, active_config)
    result = send_with_retry(active_config, ims_request, post_fn=post_fn, sleep_fn=sleep_fn)
    result["correlation_id"] = ims_request["correlationId"]
    return result


def _load_payload(args: argparse.Namespace) -> JsonDict:
    if args.payload_json:
        return json.loads(args.payload_json)
    if args.payload_file:
        return json.loads(args.payload_file.read_text(encoding="utf-8-sig"))
    raise ValueError("Either --payload-json or --payload-file is required.")


def main() -> int:
    parser = argparse.ArgumentParser(description="OT to IMS connector MVP.")
    parser.add_argument("--payload-json", help="JSON payload string from OT source.")
    parser.add_argument("--payload-file", type=Path, help="Path to payload JSON file.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Force non-dry-run execution regardless of IMS_DRY_RUN env value.",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args)
        config = load_config()
        if args.execute:
            config = replace(config, dry_run=False)
        result = process_ot_payload(payload, config=config)
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(json.dumps({"status": "error", "message": str(exc)}))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"ok", "dry_run", "not_implemented"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
