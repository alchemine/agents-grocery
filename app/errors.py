from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import application


@application.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Not found"},
        )
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={"success": False, "message": "Method not allowed"},
        )
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={"success": False, "message": "Too many requests"},
        )
    if exc.status_code == 500:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Internal server error, {exc.detail}",
            },
        )

    # Default handling for other HTTP errors
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )


@application.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Data validation failed",
            "errors": exc.errors(),
        },
    )
