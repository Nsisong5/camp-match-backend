import pytest
from fastapi import status
from camp_match.modules.security.domain.value_objects import Role
from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.shared_kernel.domain.identifiers import EntityId

@pytest.mark.asyncio
async def test_university_creation_unauthenticated(client):
    response = await client.post(
        "/api/v1/universities",
        json={"official_name": "Unauth Uni", "institution_type": "UNIVERSITY", "state_region": "NY"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_university_creation_forbidden(client, db_session):
    # Register a regular user (STUDENT role by default usually, but let's be explicit)
    await client.post("/api/v1/auth/register", json={"email": "student@example.com", "password": "password123"})
    
    login_resp = await client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.post(
        "/api/v1/universities",
        json={"official_name": "Forbidden Uni", "institution_type": "UNIVERSITY", "state_region": "NY"},
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_university_creation_allowed_for_admin(client, db_session):
    # Register
    reg_resp = await client.post("/api/v1/auth/register", json={"email": "admin-auth@example.com", "password": "password123"})
    admin_id = reg_resp.json()["id"]

    # Assign ADMIN role
    role_repo = SqlAlchemyRoleRepository(db_session)
    await role_repo.assign_role(EntityId.from_string(admin_id), Role.ADMIN)
    await db_session.commit()

    # Login
    login_resp = await client.post("/api/v1/auth/login", json={"email": "admin-auth@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/universities",
        json={"official_name": "Allowed Uni", "institution_type": "UNIVERSITY", "state_region": "NY"},
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
