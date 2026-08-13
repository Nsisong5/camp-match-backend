import pytest
from httpx import ASGITransport, AsyncClient

from camp_match.app import create_app


@pytest.mark.asyncio
async def test_health():
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
