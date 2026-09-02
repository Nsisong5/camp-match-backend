import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from camp_match.shared_kernel.application.errors import (
    ApplicationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

logger = structlog.get_logger()


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", path=str(request.url), error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            },
        )

    async def handle_application_error(request: Request, exc: ApplicationError, status_code: int) -> JSONResponse:
        code = exc.code or _to_snake_case(type(exc).__name__)
        logger.warning(
            "application_error", 
            code=code, 
            path=str(request.url)
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": code,
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        return await handle_application_error(request, exc, 422)

    @app.exception_handler(UnauthorizedError)
    async def handle_unauthorized_error(request: Request, exc: UnauthorizedError) -> JSONResponse:
        return await handle_application_error(request, exc, 401)

    @app.exception_handler(ForbiddenError)
    async def handle_forbidden_error(request: Request, exc: ForbiddenError) -> JSONResponse:
        return await handle_application_error(request, exc, 403)

    @app.exception_handler(NotFoundError)
    async def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
        return await handle_application_error(request, exc, 404)

    @app.exception_handler(ConflictError)
    async def handle_conflict_error(request: Request, exc: ConflictError) -> JSONResponse:
        return await handle_application_error(request, exc, 409)

def _to_snake_case(name: str) -> str:
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
