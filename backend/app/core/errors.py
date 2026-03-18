from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, code: str, message: str, details: Any | None = None, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
            "request_id": _request_id(request),
        },
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": exc.detail,
                "details": None,
            },
            "request_id": _request_id(request),
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
            },
            "request_id": _request_id(request),
        },
    )

