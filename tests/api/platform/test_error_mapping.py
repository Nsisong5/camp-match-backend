import pytest
from fastapi import FastAPI

from camp_match.platform.errors.http_error_handlers import register_error_handlers
from camp_match.shared_kernel.application.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


@pytest.fixture
def app():
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/test-validation")
    async def raise_validation():
        raise ValidationError("invalid input")

    @app.get("/test-unauthorized")
    async def raise_unauthorized():
        raise UnauthorizedError("unauthorized")

    @app.get("/test-forbidden")
    async def raise_forbidden():
        raise ForbiddenError("forbidden")

    @app.get("/test-not-found")
    async def raise_not_found():
        raise NotFoundError("not found")

    @app.get("/test-conflict")
    async def raise_conflict():
        raise ConflictError("conflict")

    @app.get("/test-500")
    async def raise_500():
        raise Exception("system failure")

    return app

@pytest.mark.asyncio
async def test_error_mapping(app):
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # ValidationError
        response = await ac.get("/test-validation")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"
        assert response.json()["error"]["message"] == "invalid input"

        # UnauthorizedError
        response = await ac.get("/test-unauthorized")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthorized_error"
        assert response.json()["error"]["message"] == "unauthorized"

        # ForbiddenError
        response = await ac.get("/test-forbidden")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden_error"
        assert response.json()["error"]["message"] == "forbidden"

        # NotFoundError
        response = await ac.get("/test-not-found")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found_error"
        assert response.json()["error"]["message"] == "not found"

        # ConflictError
        response = await ac.get("/test-conflict")
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "conflict_error"
        assert response.json()["error"]["message"] == "conflict"
