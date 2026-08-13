from fastapi import FastAPI
from camp_match.platform.errors.http_error_handlers import register_error_handlers

def create_app() -> FastAPI:
    app = FastAPI(title="Camp Match API", version="0.1.0")
    register_error_handlers(app)

    @app.get("/health", tags=["infrastructure"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app

