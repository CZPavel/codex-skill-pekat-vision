import base64
import json

from scripts.rest_api_client_demo import _build_url, parse_response


class DummyResponse:
    def __init__(self, content=b"", headers=None, json_payload=None):
        self.content = content
        self.headers = headers or {}
        self._json_payload = json_payload

    def json(self):
        if self._json_payload is None:
            raise ValueError("json payload is not set")
        return self._json_payload


def test_parse_response_context_mode():
    response = DummyResponse(json_payload={"result": True})
    parsed = parse_response(response, response_type="context", context_in_body=False)
    assert parsed.image_bytes is None
    assert parsed.context["result"] is True


def test_parse_response_context_in_body():
    image = b"\x89PNGfake"
    context = {"result": False, "data": "lot-17"}
    payload = image + json.dumps(context).encode("utf-8")
    response = DummyResponse(content=payload, headers={"ImageLen": str(len(image))})

    parsed = parse_response(response, response_type="annotated_image", context_in_body=True)
    assert parsed.image_bytes == image
    assert parsed.context == context


def test_parse_response_context_in_header():
    image = b"\x89PNGfake2"
    context = {"result": True, "count": 3}
    encoded = base64.b64encode(json.dumps(context).encode("utf-8")).decode("ascii")
    response = DummyResponse(content=image, headers={"ContextBase64utf": encoded})

    parsed = parse_response(response, response_type="image", context_in_body=False)
    assert parsed.image_bytes == image
    assert parsed.context == context


def test_build_url_with_flags_and_data():
    url = _build_url(
        "127.0.0.1",
        8000,
        "analyze_raw_image",
        "context",
        data="line A",
        context_in_body=True,
        extra_query={"height": 512, "width": 640},
    )
    assert url.startswith("http://127.0.0.1:8000/analyze_raw_image?")
    assert "response_type=context" in url
    assert "data=line+A" in url
    assert "height=512" in url
    assert "width=640" in url
    assert "context_in_body" in url
