from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class ContentPilotException(Exception):
    """Base exception class for domain and application errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class EntityNotFoundException(ContentPilotException):
    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(
            message=f"{entity_name} with ID '{entity_id}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedException(ContentPilotException):
    def __init__(self, message: str = "Invalid credentials or token expired") -> None:
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(ContentPilotException):
    def __init__(self, message: str = "Permission denied for this workspace action") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )


async def contentpilot_exception_handler(request: Request, exc: ContentPilotException) -> JSONResponse:
    """Global handler converting ContentPilot exceptions into standardized API JSON envelopes."""
    logger.warning(
        "Application exception caught",
        code=exc.code,
        message=exc.message,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "errors": exc.details or [],
            "meta": {
                "path": request.url.path
            }
        }
    )
