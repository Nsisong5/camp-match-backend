import pytest
from httpx import ASGITransport, AsyncClient
from camp_match.app import create_app
from fastapi import FastAPI

@pytest.mark.asyncio
async def test_unexpected_error_handler():
    app = create_app()

    @app.get("/test-error")
    async def trigger_error():
        raise Exception("Boom!")

    # The exception will be caught by our handler, and thus NOT raised to AsyncClient.
    # Therefore, no try/except is needed around await ac.get().
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        response = await ac.get("/test-error")
    
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "An unexpected error occurred."}
    }

@pytest.mark.asyncio
async def test_health_still_works():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
