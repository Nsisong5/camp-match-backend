from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from camp_match.config.settings import get_settings
from camp_match.platform.db.session import create_engine, create_session_factory
from camp_match.platform.errors.http_error_handlers import register_error_handlers
from camp_match.platform.logging.middleware import RequestIDMiddleware
from camp_match.platform.logging.setup import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_logging(settings)
    engine = create_engine(settings)
    app.state.db_engine = engine
    app.state.db_session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Camp Match API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(RequestIDMiddleware)
    register_error_handlers(app)

    @app.get("/health", tags=["infrastructure"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
