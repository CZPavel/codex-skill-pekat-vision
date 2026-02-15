from __future__ import annotations

import argparse
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv

from thingworx_client import ThingWorxClient


def parse_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def parse_json_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def required_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise ValueError(f"Missing environment variable: {key}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal FIOT/ThingWorx REST connector.")
    parser.add_argument("--healthcheck", action="store_true", help="Run authenticated healthcheck call.")
    parser.add_argument("--write-property", action="store_true", help="Write one property value.")
    parser.add_argument("--invoke-service", action="store_true", help="Invoke one service.")
    parser.add_argument("--value", help="Value for --write-property (JSON or plain string).")
    parser.add_argument(
        "--service-payload",
        default="{}",
        help="JSON payload for --invoke-service. Default: {}",
    )
    return parser


def create_client() -> ThingWorxClient:
    base_url = required_env("THINGWORX_BASE_URL")
    app_key = required_env("THINGWORX_APP_KEY")
    timeout_seconds = float(os.getenv("THINGWORX_TIMEOUT_SECONDS", "10"))
    retries = int(os.getenv("THINGWORX_RETRIES", "3"))
    backoff_seconds = float(os.getenv("THINGWORX_BACKOFF_SECONDS", "0.5"))
    verify_tls = parse_bool(os.getenv("THINGWORX_VERIFY_TLS"), default=True)
    dry_run = parse_bool(os.getenv("THINGWORX_DRY_RUN"), default=True)

    client_cert = None
    cert_path = os.getenv("THINGWORX_CLIENT_CERT", "").strip()
    key_path = os.getenv("THINGWORX_CLIENT_KEY", "").strip()
    if cert_path and key_path:
        client_cert = (cert_path, key_path)
    elif cert_path:
        client_cert = cert_path

    return ThingWorxClient(
        base_url=base_url,
        app_key=app_key,
        timeout_seconds=timeout_seconds,
        retries=retries,
        backoff_seconds=backoff_seconds,
        verify_tls=verify_tls,
        client_cert=client_cert,
        dry_run=dry_run,
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    load_dotenv()
    args = build_parser().parse_args()

    if not (args.healthcheck or args.write_property or args.invoke_service):
        args.healthcheck = True

    thing_name = required_env("THINGWORX_THING")
    property_name = os.getenv("THINGWORX_PROPERTY", "DemoProperty")
    service_name = os.getenv("THINGWORX_SERVICE", "DemoService")

    client = create_client()

    if args.healthcheck:
        result = client.healthcheck(thing_name=thing_name)
        print("healthcheck:")
        print(json.dumps(result, indent=2, ensure_ascii=True))

    if args.write_property:
        if args.value is None:
            raise ValueError("Use --value with --write-property")
        value = parse_json_value(args.value)
        result = client.write_property(
            thing_name=thing_name,
            property_name=property_name,
            value=value,
        )
        print("write_property:")
        print(json.dumps(result, indent=2, ensure_ascii=True))

    if args.invoke_service:
        payload = parse_json_value(args.service_payload)
        if not isinstance(payload, dict):
            raise ValueError("--service-payload must be a JSON object")
        result = client.invoke_service(
            thing_name=thing_name,
            service_name=service_name,
            payload=payload,
        )
        print("invoke_service:")
        print(json.dumps(result, indent=2, ensure_ascii=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
