from fastapi import FastAPI

from camp_match.config.settings import get_settings
from camp_match.platform.errors.http_error_handlers import register_error_handlers
from camp_match.platform.logging.middleware import RequestIDMiddleware
from camp_match.platform.logging.setup import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(title="Camp Match API", version="0.1.0")
    app.add_middleware(RequestIDMiddleware)
    register_error_handlers(app)

    @app.get("/health", tags=["infrastructure"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
