import time
import asyncio

from fastapi import Request
from fastapi.responses import JSONResponse

from app import application


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
