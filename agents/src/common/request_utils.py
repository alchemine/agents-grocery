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
    return_data: bool = False,
    **kwargs,
) -> dict:
    """Safe request."""
    try:
        response = requests.request(method, url, headers=headers, json=json, **kwargs)
        response.raise_for_status()
        response_json = response.json()
        if return_data:
            assert response_json["success"], response_json["message"]
            result = response_json["data"]
        else:
            result = response_json
        return result
    except Exception:
        log_error(f"API request has been failed: {url}")
        raise


async def async_safe_request(
    session: aiohttp.ClientSession,
    url: str,
    json: dict | None = None,
    headers: dict = DEFAULT_HEADERS,
    method: Literal["get", "post"] = "post",
    return_data: bool = False,
    **kwargs,
) -> dict:
    """Asynchronous safe request."""
    try:
        async with session.request(
            method, url, json=json, headers=headers, **kwargs
        ) as response:
            response.raise_for_status()
        response_json = await response.json()
        if return_data:
            assert response_json["success"], response_json["message"]
            result = response_json["data"]
        else:
            result = response_json
        return result
    except Exception:
        log_error(f"API request has been failed: {url}")
        raise
