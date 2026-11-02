import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.schemas import ErrorResponse
from core.errors import IngestionException

logger = logging.getLogger(__name__)


def error_response(
    request: Request, status_code: int, code: str, message: str, details=None
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    body = ErrorResponse(
        message=message, code=code, request_id=request_id, details=details
    )
    header = {"X-Request-ID": request_id} if request_id else None
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(exclude_none=True),
        headers=header,
    )


async def ingestion_error_handler(request: Request, exc: IngestionException):
    logger.warning("%s %s", exc.code, exc.message)
    return error_response(request, exc.status_code, exc.code, exc.message)


async def unhandled_error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception(
        "An unexpected error occurred %s %s",
        request.method,
        request.url.path,
        extra={"request_id": request_id},
    )

    return error_response(
        request, 500, "internal_error", "An unexpected error occurred"
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IngestionException, ingestion_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
