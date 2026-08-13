import pytest
from httpx import ASGITransport, AsyncClient

from camp_match.app import create_app


@pytest.mark.asyncio
async def test_request_id_header():
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response1 = await ac.get("/health")
        response2 = await ac.get("/health")

    assert "X-Request-ID" in response1.headers
    assert "X-Request-ID" in response2.headers

    request_id1 = response1.headers["X-Request-ID"]
    request_id2 = response2.headers["X-Request-ID"]

    assert request_id1 != request_id2


@pytest.mark.asyncio
async def test_provided_request_id_is_passed_through():
    app = create_app()
    custom_id = "my-custom-id"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Request-ID": custom_id},
    ) as ac:
        response = await ac.get("/health")

    assert response.headers["X-Request-ID"] == custom_id
