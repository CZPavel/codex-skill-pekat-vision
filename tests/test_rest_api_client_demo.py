import base64
import json
from unittest.mock import Mock

import pytest
import requests

from rest_api_client_demo import PekatRestError, _build_url, analyze_png, parse_response

PNG = b"\x89PNG\r\n\x1a\nmock"


def response(*, payload=None, content=b"", headers=None):
    item = Mock()
    item.content = content
    item.headers = headers or {}
    item.json.return_value = payload
    item.raise_for_status.return_value = None
    return item


def test_png_binary_contract_and_success():
    session = Mock()
    session.post.return_value = response(payload={"result": True})
    assert analyze_png(PNG, session=session).context["result"] is True
    _, kwargs = session.post.call_args
    assert kwargs["data"] == PNG
    assert kwargs["headers"] == {"Content-Type": "application/octet-stream"}
    assert kwargs["timeout"] == (3.0, 20.0)


@pytest.mark.parametrize(
    ("error", "message"),
    [(requests.Timeout(), "timed out"), (requests.ConnectionError(), "unavailable")],
)
def test_transport_failures(error, message):
    session = Mock()
    session.post.side_effect = error
    with pytest.raises(PekatRestError, match=message):
        analyze_png(PNG, session=session)


def test_http_error():
    item = response(payload={})
    item.status_code = 503
    item.raise_for_status.side_effect = requests.HTTPError(response=item)
    session = Mock(post=Mock(return_value=item))
    with pytest.raises(PekatRestError, match="503"):
        analyze_png(PNG, session=session)


def test_invalid_json():
    item = response()
    item.json.side_effect = ValueError("bad json")
    session = Mock(post=Mock(return_value=item))
    with pytest.raises(PekatRestError, match="invalid JSON"):
        analyze_png(PNG, session=session)


def test_response_modes_and_url_encoding():
    context = {"result": True}
    encoded = base64.b64encode(json.dumps(context).encode()).decode()
    parsed = parse_response(response(content=b"image", headers={"ContextBase64utf": encoded}), "image", False)
    assert parsed.image_bytes == b"image"
    assert parsed.context == context
    url = _build_url("localhost", 8080, "analyze_raw_image", data="line A", extra_query={"height": 10, "width": 20})
    assert "data=line+A" in url and "height=10" in url and "width=20" in url
