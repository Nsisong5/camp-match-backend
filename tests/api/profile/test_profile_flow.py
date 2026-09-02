import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.api
@pytest.mark.asyncio
async def test_profile_flow_happy_path(client: AsyncClient, db_session):
    # 1. Register & Login Identity
    reg_response = await client.post("/api/v1/auth/register", json={"email": "student@example.com", "password": "password123"})
    assert reg_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "password123"})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Create Student Profile
    create_response = await client.post(
        "/api/v1/profiles",
        headers=auth_headers,
        json={
            "display_name": "Student A",
            "profile_type": "STUDENT",
            "student_details": {"university_name": "UI"}
        }
    )
    assert create_response.status_code == 201
    profile_id = create_response.json()["id"]

    # 3. GET /me
    me_response = await client.get("/api/v1/profiles/me", headers=auth_headers)
    assert me_response.status_code == 200
    assert me_response.json()["display_name"] == "Student A"

    # 4. Update core fields
    update_response = await client.patch("/api/v1/profiles/me", headers=auth_headers, json={"display_name": "Student A Updated"})
    assert update_response.status_code == 200
    assert update_response.json()["display_name"] == "Student A Updated"

    # 5. Update Student fields
    update_student_response = await client.patch("/api/v1/profiles/me/student", headers=auth_headers, json={"department": "CS"})
    assert update_student_response.status_code == 200
    assert update_student_response.json()["student_details"]["department"] == "CS"

    # 6. GET Public Profile (via second account)
    reg2_response = await client.post("/api/v1/auth/register", json={"email": "scout@example.com", "password": "password123"})
    assert reg2_response.status_code == 201
    login2_response = await client.post("/api/v1/auth/login", json={"email": "scout@example.com", "password": "password123"})
    assert login2_response.status_code == 200
    auth_headers2 = {"Authorization": f"Bearer {login2_response.json()['access_token']}"}

    public_response = await client.get(f"/api/v1/profiles/{profile_id}", headers=auth_headers2)
    assert public_response.status_code == 200
    assert public_response.json()["display_name"] == "Student A Updated"

@pytest.mark.api
@pytest.mark.asyncio
async def test_profile_unhappy_paths(client: AsyncClient, db_session):
    # Setup for 409
    reg_response = await client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert reg_response.status_code == 201
    login_response = await client.post("/api/v1/auth/login", json={"email": "dup@example.com", "password": "password123"})
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    
    await client.post("/api/v1/profiles", headers=auth_headers, json={"display_name": "A", "profile_type": "STUDENT"})
    
    # 409 on second create
    dup_response = await client.post("/api/v1/profiles", headers=auth_headers, json={"display_name": "B", "profile_type": "STUDENT"})
    assert dup_response.status_code == 409

    # 422 on wrong profile type update
    wrong_update_response = await client.patch("/api/v1/profiles/me/scout", headers=auth_headers, json={"business_name": "X"})
    assert wrong_update_response.status_code == 422 # Domain logic in use case raises ValueError -> 422

    # 404 on GET /me with no profile
    reg3_response = await client.post("/api/v1/auth/register", json={"email": "none@example.com", "password": "password123"})
    assert reg3_response.status_code == 201
    login3_response = await client.post("/api/v1/auth/login", json={"email": "none@example.com", "password": "password123"})
    assert login3_response.status_code == 200
    auth_headers3 = {"Authorization": f"Bearer {login3_response.json()['access_token']}"}
    
    none_response = await client.get("/api/v1/profiles/me", headers=auth_headers3)
    assert none_response.status_code == 404
