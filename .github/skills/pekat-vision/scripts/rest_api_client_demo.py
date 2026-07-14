"""Safe, testable PEKAT REST helpers for PNG and raw image analysis."""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests

ALLOWED_RESPONSE_TYPES = {"context", "image", "annotated_image", "heatmap"}


class PekatRestError(RuntimeError):
    """Normalized REST transport or payload error."""


@dataclass(slots=True)
class Result:
    image_bytes: bytes | None
    context: dict[str, Any]


def _build_url(
    host: str,
    port: int,
    endpoint: str,
    response_type: str = "context",
    *,
    data: str | None = None,
    context_in_body: bool = False,
    extra_query: dict[str, Any] | None = None,
) -> str:
    if response_type not in ALLOWED_RESPONSE_TYPES:
        raise ValueError(f"unsupported response_type: {response_type}")
    query: dict[str, Any] = {"response_type": response_type}
    if data is not None:
        query["data"] = data
    if context_in_body:
        query["context_in_body"] = "true"
    if extra_query:
        query.update(extra_query)
    return f"http://{host}:{int(port)}/{endpoint}?{urlencode(query)}"


def _dict_json(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise PekatRestError("PEKAT returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise PekatRestError("PEKAT returned an unexpected JSON shape")
    return payload


def parse_response(response: Any, response_type: str, context_in_body: bool) -> Result:
    if response_type == "context":
        return Result(None, _dict_json(response))
    if context_in_body:
        raw_length = response.headers.get("ImageLen")
        if raw_length is None:
            return Result(None, _dict_json(response))
        try:
            image_length = int(raw_length)
        except (TypeError, ValueError) as exc:
            raise PekatRestError("invalid ImageLen response header") from exc
        if image_length < 0 or image_length > len(response.content):
            raise PekatRestError("ImageLen exceeds response body")
        try:
            context = json.loads(response.content[image_length:].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PekatRestError("invalid context in response body") from exc
        if not isinstance(context, dict):
            raise PekatRestError("unexpected context shape")
        return Result(response.content[:image_length], context)
    encoded = response.headers.get("ContextBase64utf")
    if encoded is None:
        return Result(None, _dict_json(response))
    try:
        context = json.loads(base64.b64decode(encoded, validate=True).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PekatRestError("invalid ContextBase64utf response header") from exc
    if not isinstance(context, dict):
        raise PekatRestError("unexpected context shape")
    return Result(response.content, context)


def _post(url: str, body: bytes, response_type: str, context_in_body: bool, timeout: tuple[float, float], session: Any) -> Result:
    try:
        response = session.post(
            url,
            data=body,
            headers={"Content-Type": "application/octet-stream"},
            timeout=timeout,
        )
        response.raise_for_status()
        return parse_response(response, response_type, context_in_body)
    except requests.Timeout as exc:
        raise PekatRestError("PEKAT request timed out") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise PekatRestError(f"PEKAT HTTP error: {status}") from exc
    except requests.RequestException as exc:
        raise PekatRestError("PEKAT is unavailable") from exc


def analyze_png(
    png_bytes: bytes,
    *,
    host: str = "localhost",
    port: int = 8080,
    response_type: str = "context",
    data: str | None = None,
    context_in_body: bool = False,
    timeout: tuple[float, float] = (3.0, 20.0),
    session: Any = requests,
) -> Result:
    if not isinstance(png_bytes, bytes) or not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("png_bytes must contain a binary PNG")
    url = _build_url(host, port, "analyze_image", response_type, data=data, context_in_body=context_in_body)
    return _post(url, png_bytes, response_type, context_in_body, timeout, session)


def analyze_raw(
    image_bytes: bytes,
    *,
    height: int,
    width: int,
    host: str = "localhost",
    port: int = 8080,
    response_type: str = "context",
    bayer: str | None = None,
    timeout: tuple[float, float] = (3.0, 20.0),
    session: Any = requests,
) -> Result:
    if height <= 0 or width <= 0 or not image_bytes:
        raise ValueError("raw image dimensions and body must be non-empty")
    query: dict[str, Any] = {"height": height, "width": width}
    if bayer:
        query["bayer"] = bayer
    url = _build_url(host, port, "analyze_raw_image", response_type, extra_query=query)
    return _post(url, image_bytes, response_type, False, timeout, session)
