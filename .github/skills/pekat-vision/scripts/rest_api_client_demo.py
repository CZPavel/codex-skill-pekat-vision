"""Demo client for PEKAT Vision REST API.

Supported endpoints:
- POST /analyze_image
- POST /analyze_raw_image
- GET /ping
- GET /stop
- GET /last_image

This module follows response handling used by current `pekat-vision-sdk`.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import numpy as np
import requests


ALLOWED_RESPONSE_TYPES = {"context", "image", "annotated_image", "heatmap"}


@dataclass
class Result:
    image_bytes: Optional[bytes]
    context: Dict[str, Any]


def _build_url(
    host: str,
    port: int,
    endpoint: str,
    response_type: str = "context",
    *,
    data: Optional[str] = None,
    context_in_body: bool = False,
    extra_query: Optional[Dict[str, Any]] = None,
) -> str:
    if response_type not in ALLOWED_RESPONSE_TYPES:
        raise ValueError(f"Unsupported response_type: {response_type}")

    query_parts = [f"response_type={quote_plus(response_type)}"]

    if data is not None:
        query_parts.append(f"data={quote_plus(data)}")

    if extra_query:
        for key, value in extra_query.items():
            query_parts.append(f"{quote_plus(str(key))}={quote_plus(str(value))}")

    if context_in_body:
        # PEKAT accepts this as a query flag without explicit value.
        query_parts.append("context_in_body")

    return f"http://{host}:{port}/{endpoint}?{'&'.join(query_parts)}"


def parse_response(response: requests.Response, response_type: str, context_in_body: bool) -> Result:
    """Parse PEKAT response for both context transport modes."""
    if response_type == "context":
        return Result(None, response.json())

    if context_in_body:
        image_len_str = response.headers.get("ImageLen")
        if not image_len_str:
            return Result(None, response.json())

        image_len = int(image_len_str)
        image_bytes = response.content[:image_len]
        context_json = response.content[image_len:].decode("utf-8")
        return Result(image_bytes, json.loads(context_json))

    image_bytes = response.content
    context_base64 = response.headers.get("ContextBase64utf")
    if context_base64 is None:
        return Result(None, response.json())

    context_json = base64.b64decode(context_base64)
    return Result(image_bytes, json.loads(context_json))


def analyze_image_bytes(
    host: str,
    port: int,
    image_bytes: bytes,
    *,
    response_type: str = "context",
    data: Optional[str] = None,
    context_in_body: bool = False,
    timeout_s: float = 5.0,
) -> Result:
    url = _build_url(
        host,
        port,
        "analyze_image",
        response_type,
        data=data,
        context_in_body=context_in_body,
    )
    response = requests.post(
        url,
        data=image_bytes,
        headers={"Content-Type": "application/octet-stream"},
        timeout=timeout_s,
    )
    response.raise_for_status()
    return parse_response(response, response_type, context_in_body)


def analyze_image_png_path(
    host: str,
    port: int,
    png_path: str,
    *,
    response_type: str = "context",
    data: Optional[str] = None,
    context_in_body: bool = False,
    timeout_s: float = 5.0,
) -> Result:
    image_bytes = Path(png_path).read_bytes()
    return analyze_image_bytes(
        host,
        port,
        image_bytes,
        response_type=response_type,
        data=data,
        context_in_body=context_in_body,
        timeout_s=timeout_s,
    )


def analyze_raw_numpy(
    host: str,
    port: int,
    image: np.ndarray,
    *,
    response_type: str = "context",
    data: Optional[str] = None,
    context_in_body: bool = False,
    bayer: Optional[str] = None,
    timeout_s: float = 5.0,
) -> Result:
    height, width = image.shape[:2]
    extra_query: Dict[str, Any] = {"height": height, "width": width}
    if bayer is not None:
        extra_query["bayer"] = bayer

    url = _build_url(
        host,
        port,
        "analyze_raw_image",
        response_type,
        data=data,
        context_in_body=context_in_body,
        extra_query=extra_query,
    )
    response = requests.post(
        url,
        data=image.tobytes(),
        headers={"Content-Type": "application/octet-stream"},
        timeout=timeout_s,
    )
    response.raise_for_status()
    return parse_response(response, response_type, context_in_body)


def last_image(
    host: str,
    port: int,
    *,
    response_type: str = "image",
    context_in_body: bool = False,
    timeout_s: float = 5.0,
) -> Result:
    url = _build_url(
        host,
        port,
        "last_image",
        response_type,
        context_in_body=context_in_body,
    )
    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    return parse_response(response, response_type, context_in_body)


def ping(host: str, port: int, timeout_s: float = 5.0) -> bool:
    try:
        requests.get(f"http://{host}:{port}/ping", timeout=timeout_s).raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def stop(host: str, port: int, key: Optional[str] = None, timeout_s: float = 5.0) -> requests.Response:
    url = f"http://{host}:{port}/stop"
    if key:
        url = f"{url}?key={quote_plus(key)}"
    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    return response


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8000

    print("Ping:", ping(HOST, PORT))

    # Example 1: PNG bytes
    # result = analyze_image_png_path(
    #     HOST, PORT, "test.png", response_type="annotated_image", data="lineA", context_in_body=False
    # )
    # print("Flow result:", result.context.get("result"))

    # Example 2: Raw numpy
    # import cv2
    # img = cv2.imread("test.png")
    # result = analyze_raw_numpy(HOST, PORT, img, response_type="context", context_in_body=True)
    # print("Context keys:", list(result.context.keys()))
