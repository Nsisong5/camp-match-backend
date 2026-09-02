import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.asyncio
async def test_profile_security(client: AsyncClient, db_session):
    # 1. Register & Login Student
    reg_response = await client.post("/api/v1/auth/register", json={"email": "security@example.com", "password": "password123"})
    assert reg_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json={"email": "security@example.com", "password": "password123"})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Create Student Profile with phone
    create_response = await client.post(
        "/api/v1/profiles",
        headers=auth_headers,
        json={
            "display_name": "Student A",
            "profile_type": "STUDENT",
            "phone_number": "+2348011112222",
            "student_details": {"university_name": "UI"}
        }
    )
    assert create_response.status_code == 201
    profile_id = create_response.json()["id"]

    # 3. Confirm phone_number is in /me but NOT in GET /profiles/{id}
    me_response = await client.get("/api/v1/profiles/me", headers=auth_headers)
    assert "phone_number" in me_response.json()
    assert me_response.json()["phone_number"] == "+2348011112222"

    public_response = await client.get(f"/api/v1/profiles/{profile_id}")
    assert "phone_number" not in public_response.json()

    # 4. Confirm Scout details DO appear in public
    reg2_response = await client.post("/api/v1/auth/register", json={"email": "scout2@example.com", "password": "password123"})
    assert reg2_response.status_code == 201
    login2_response = await client.post("/api/v1/auth/login", json={"email": "scout2@example.com", "password": "password123"})
    auth_headers2 = {"Authorization": f"Bearer {login2_response.json()['access_token']}"}
    
    create_scout_response = await client.post(
        "/api/v1/profiles",
        headers=auth_headers2,
        json={
            "display_name": "Scout B",
            "profile_type": "SCOUT",
            "scout_details": {"business_name": "Agency B", "business_description": "We find houses"}
        }
    )
    assert create_scout_response.status_code == 201
    scout_profile_id = create_scout_response.json()["id"]

    public_scout_response = await client.get(f"/api/v1/profiles/{scout_profile_id}")
    assert public_scout_response.status_code == 200
    scout_json = public_scout_response.json()
    assert "scout_details" in scout_json
    assert scout_json["scout_details"]["business_name"] == "Agency B"
    assert scout_json["scout_details"]["business_description"] == "We find houses"

    # 5. Confirm endpoints reject unauthorized requests
    protected_endpoints = [
        ("/api/v1/profiles", "POST"),
        ("/api/v1/profiles/me", "GET"),
        ("/api/v1/profiles/me", "PATCH"),
    ]
    for url, method in protected_endpoints:
        response = await client.request(method, url)
        assert response.status_code == 401
