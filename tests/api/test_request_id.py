import pytest


@pytest.mark.asyncio
@pytest.mark.api
async def test_request_id_header(client):
    response1 = await client.get("/health")
    response2 = await client.get("/health")

    assert "X-Request-ID" in response1.headers
    assert "X-Request-ID" in response2.headers

    request_id1 = response1.headers["X-Request-ID"]
    request_id2 = response2.headers["X-Request-ID"]

    assert request_id1 != request_id2


@pytest.mark.asyncio
@pytest.mark.api
async def test_provided_request_id_is_passed_through(client):
    custom_id = "my-custom-id"
    response = await client.get("/health", headers={"X-Request-ID": custom_id})

    assert response.headers["X-Request-ID"] == custom_id
