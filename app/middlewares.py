import time
import json
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Dict, List, Tuple, Callable, Awaitable

import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Scope, Message
from starlette.responses import Response, StreamingResponse
from starlette.background import BackgroundTasks

from app import application
from src.common.logger import log_api


REQUEST_TIMEOUT_ERROR = 60


# Adding a middleware returning a 504 error if the request processing time is above a certain threshold
@application.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        if "/chat/" in request.url.path:
            start_time = time.time()
            return await asyncio.wait_for(
                call_next(request), timeout=REQUEST_TIMEOUT_ERROR
            )
        else:
            return await call_next(request)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"success": False, "message": "Server timeout"},
        )


class RequestWithBody(Request):
    def __init__(self, scope: Scope, body: bytes) -> None:
        super().__init__(scope, self._receive)
        self._body = body
        self._body_returned = False

    async def _receive(self) -> Message:
        if self._body_returned:
            return {"type": "http.disconnect"}
        else:
            self._body_returned = True
            return {"type": "http.request", "body": self._body, "more_body": False}


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom middleware for request and response logging"""

    async def _get_response_params(
        self, response: StreamingResponse
    ) -> Tuple[bytes, Dict[str, str], int]:
        """Merge all streaming response chunks"""
        response_byte_chunks: List[bytes] = []
        response_status: List[int] = []
        response_headers: List[Dict[str, str]] = []

        async def send(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_status.append(message["status"])
                response_headers.append(
                    {k.decode("utf8"): v.decode("utf8") for k, v in message["headers"]}
                )
            else:
                response_byte_chunks.append(message["body"])

        await response.stream_response(send)
        content = b"".join(response_byte_chunks)
        return content, response_headers[0], response_status[0]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[StreamingResponse]],
    ) -> Response:
        # 1. Store request body in a variable and generate new request as it is consumed.
        request_body_bytes = await request.body()
        request_with_body = RequestWithBody(request.scope, request_body_bytes)

        # 2. Store response body in a variable and generate new response as it is consumed.
        start_time = datetime.now()
        response = await call_next(request_with_body)
        end_time = datetime.now()
        response_content_bytes, response_headers, response_status = (
            await self._get_response_params(response)
        )

        # 3. If there is no request body handle exception, otherwise convert bytes to JSON.
        try:
            req_body = json.loads(request_body_bytes)
        except JSONDecodeError:
            req_body = {}
        try:
            # Use response_content_bytes(merged) instead of response.body(streaming)
            resp_body = json.loads(response_content_bytes)
        except JSONDecodeError:
            resp_body = {}

        # 4. Construct log data
        log_data = {
            "ip": request.client.host,
            "port": request.client.port,
            "method": request.method,
            "path": request.url.path,
            "agent": dict(request.headers.items())["user-agent"],
            "request_body": req_body,
            "response_body": resp_body,
            "response_status": response.status_code,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "elapsed_secs": (end_time - start_time).total_seconds(),
        }

        # 5. Log as a background task
        new_response = Response(
            response_content_bytes, response_status, response_headers
        )
        new_response.background = BackgroundTasks()

        # Preserve existing background tasks
        if hasattr(response, "background") and response.background:
            for task in response.background.tasks:
                new_response.background.add_task(
                    task["func"], *task["args"], **task["kwargs"]
                )
        new_response.background.add_task(log_api, log_data)

        # 6. Finally, return the newly instantiated response values
        return new_response
