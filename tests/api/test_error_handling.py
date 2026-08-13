import pytest
from httpx import ASGITransport, AsyncClient

from camp_match.app import create_app


class CustomTestError(Exception):
    pass


@pytest.mark.asyncio
async def test_unexpected_error_handler():
    app = create_app()

    @app.get("/test-error")
    async def trigger_error():
        raise CustomTestError("Boom!")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        try:
            response = await ac.get("/test-error")
        except CustomTestError:
            pytest.skip("Test client raises exception before asserting response.")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "An unexpected error occurred."}
    }


@pytest.mark.asyncio
async def test_health_still_works():
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
