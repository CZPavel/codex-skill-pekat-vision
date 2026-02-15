from __future__ import annotations

import logging
import time
from typing import Any

import requests


class ThingWorxClient:
    """Minimal ThingWorx REST client with timeout/retry/logging and optional mTLS."""

    def __init__(
        self,
        base_url: str,
        app_key: str,
        timeout_seconds: float = 10.0,
        retries: int = 3,
        backoff_seconds: float = 0.5,
        verify_tls: bool = True,
        client_cert: str | tuple[str, str] | None = None,
        dry_run: bool = False,
        logger: logging.Logger | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_key = app_key
        self.timeout_seconds = timeout_seconds
        self.retries = max(retries, 0)
        self.backoff_seconds = max(backoff_seconds, 0.0)
        self.verify_tls = verify_tls
        self.client_cert = client_cert
        self.dry_run = dry_run
        self.logger = logger or logging.getLogger(__name__)

        self.session = requests.Session()

    def _headers(self, has_body: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "appKey": self.app_key,
            "x-thingworx-session": "false",
        }
        if has_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _decode(self, response: requests.Response) -> Any:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type.lower():
            return response.json()
        return {"status_code": response.status_code, "text": response.text}

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"

        if self.dry_run:
            self.logger.info("DRY-RUN %s %s", method, url)
            return {
                "dry_run": True,
                "method": method,
                "url": url,
                "params": params or {},
                "payload": payload or {},
            }

        attempts = self.retries + 1
        for attempt in range(1, attempts + 1):
            try:
                started = time.monotonic()
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=self._headers(has_body=payload is not None),
                    params=params,
                    json=payload,
                    timeout=self.timeout_seconds,
                    verify=self.verify_tls,
                    cert=self.client_cert,
                )
                elapsed_ms = int((time.monotonic() - started) * 1000)
                self.logger.info("%s %s -> %s (%sms)", method, path, response.status_code, elapsed_ms)

                retryable_status = response.status_code in (429, 500, 502, 503, 504)
                if retryable_status and attempt < attempts:
                    sleep_seconds = self.backoff_seconds * (2 ** (attempt - 1))
                    self.logger.warning(
                        "Retryable HTTP status %s on attempt %s/%s, retry in %.2fs",
                        response.status_code,
                        attempt,
                        attempts,
                        sleep_seconds,
                    )
                    time.sleep(sleep_seconds)
                    continue

                response.raise_for_status()
                return self._decode(response)
            except (requests.Timeout, requests.ConnectionError) as exc:
                if attempt >= attempts:
                    raise
                sleep_seconds = self.backoff_seconds * (2 ** (attempt - 1))
                self.logger.warning(
                    "Network error on attempt %s/%s: %s. Retry in %.2fs",
                    attempt,
                    attempts,
                    exc,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)

        raise RuntimeError("Unexpected retry loop exit")

    def healthcheck(self, thing_name: str) -> Any:
        """Basic authenticated check against target Thing."""
        return self._request("GET", f"/Thingworx/Things/{thing_name}")

    def write_property(self, thing_name: str, property_name: str, value: Any) -> Any:
        """
        Property write skeleton.
        Adjust payload shape if your ThingWorx version/entity expects another format.
        """
        return self._request(
            "PUT",
            f"/Thingworx/Things/{thing_name}/Properties/{property_name}",
            payload={property_name: value},
        )

    def invoke_service(
        self,
        thing_name: str,
        service_name: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """Service invocation skeleton."""
        return self._request(
            "POST",
            f"/Thingworx/Things/{thing_name}/Services/{service_name}",
            payload=payload or {},
        )
