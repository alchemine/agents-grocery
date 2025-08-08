import pytest
from unittest.mock import patch, MagicMock

import requests

from src.common.request_utils import safe_request, async_safe_request


class DummyAsyncResponse:
    def __init__(self, payload: dict, raise_error: Exception | None = None):
        self._payload = payload
        self._raise_error = raise_error

    async def __aenter__(self):
        if self._raise_error:
            raise self._raise_error
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        if self._raise_error:
            raise self._raise_error

    async def json(self):
        return self._payload


class DummySession:
    def __init__(self, payload: dict, raise_error: Exception | None = None):
        self._payload = payload
        self._raise_error = raise_error

    def request(self, method, url, json=None, headers=None, **kwargs):
        return DummyAsyncResponse(self._payload, self._raise_error)


def test_safe_request_returns_full_json_when_return_data_false():
    fake = {"success": True, "data": {"x": 1}, "message": "ok"}
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = fake

    with patch.object(requests, "request", return_value=mock_resp) as m:
        out = safe_request("http://example.com", method="get", return_data=False)
    assert out == fake


def test_safe_request_returns_data_when_return_data_true():
    fake = {"success": True, "data": {"x": 1}, "message": "ok"}
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = fake

    with patch.object(requests, "request", return_value=mock_resp):
        out = safe_request("http://example.com", method="get", return_data=True)
    assert out == {"x": 1}


def test_safe_request_raises_on_error():
    with patch.object(requests, "request", side_effect=requests.HTTPError("bad")):
        with pytest.raises(Exception):
            safe_request("http://example.com", method="get")


@pytest.mark.asyncio
async def test_async_safe_request_returns_full_json_when_return_data_false():
    payload = {"success": True, "data": {"y": 2}, "message": "ok"}
    session = DummySession(payload)
    out = await async_safe_request(session, "http://example.com", method="get")
    assert out == payload


@pytest.mark.asyncio
async def test_async_safe_request_returns_data_when_return_data_true():
    payload = {"success": True, "data": {"y": 2}, "message": "ok"}
    session = DummySession(payload)
    out = await async_safe_request(
        session, "http://example.com", method="get", return_data=True
    )
    assert out == {"y": 2}


@pytest.mark.asyncio
async def test_async_safe_request_raises_on_error():
    session = DummySession({}, raise_error=requests.HTTPError("bad"))
    with pytest.raises(Exception):
        await async_safe_request(session, "http://example.com", method="get")
