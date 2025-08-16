"""Requests module.

Commonly used functions for requests are here.
"""

from typing import Literal

import aiohttp
import requests

from src.common.logger import log_error


DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def safe_request(
    url: str,
    json: dict | None = None,
    headers: dict = DEFAULT_HEADERS,
    method: Literal["get", "post"] = "post",
    **kwargs,
) -> dict:
    """Safe request."""
    try:
        response = requests.request(method, url, headers=headers, json=json, **kwargs)
        response.raise_for_status()
        result = response.json()
        assert result["success"], result["message"]
        return result["data"]
    except Exception as e:
        log_error(f"Request failed: {e}")
        return {}


async def async_safe_request(
    session: aiohttp.ClientSession,
    url: str,
    json: dict | None = None,
    headers: dict = DEFAULT_HEADERS,
    method: Literal["get", "post"] = "post",
    **kwargs,
) -> dict:
    """Asynchronous safe request."""
    try:
        async with session.request(
            method, url, json=json, headers=headers, **kwargs
        ) as response:
            response.raise_for_status()
            result = await response.json()
            assert result["success"], result["message"]
            return result["data"]
    except Exception as e:
        log_error(f"Request failed: {e}")
        return {}
