import pytest


@pytest.mark.asyncio
async def test_auth_flow_happy_path(client, db_session):
    # 1. Register
    reg_response = await client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "password123"})
    if reg_response.status_code != 201:
        print(reg_response.json())
    assert reg_response.status_code == 201
    user_id = reg_response.json()["id"]

    # 2. Login
    login_response = await client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # ... (repeat for other calls)

    # 3. /auth/me
    me_response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_response.status_code == 200
    assert me_response.json()["id"] == user_id

    # 4. Refresh
    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    
    # 5. Confirm old refresh token fails
    old_refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert old_refresh_response.status_code == 401 # Should be InvalidCredentials

    # 6. Logout with new refresh token
    logout_response = await client.post("/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert logout_response.status_code == 204
    
    # 7. Logout idempotent
    logout_again_response = await client.post("/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert logout_again_response.status_code == 204

@pytest.mark.asyncio
async def test_auth_unhappy_paths(client):
    # Duplicate registration
    await client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "password123"})
    reg_response = await client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert reg_response.status_code == 409
    
    # Login wrong password
    await client.post("/api/v1/auth/register", json={"email": "wrong@example.com", "password": "password123"})
    login_response = await client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrongpassword"})
    assert login_response.status_code == 401
    
    # Login nonexistent email
    login_response_nonexistent = await client.post("/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "password123"})
    assert login_response_nonexistent.status_code == 401
    
    # Assert bodies identical for anti-enumeration
    assert login_response.json() == login_response_nonexistent.json()
    
    # /auth/me no auth header
    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 401

    # /auth/me garbage token
    me_response_garbage = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})
    assert me_response_garbage.status_code == 401
