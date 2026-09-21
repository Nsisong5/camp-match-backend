import pytest
from httpx import AsyncClient
from camp_match.shared_kernel.domain.identifiers import EntityId

async def create_authenticated_user(client: AsyncClient, email: str, profile_type: str) -> str:
    # 1. Register
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123"
    })
    
    # 2. Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    
    # 3. Create Profile
    await client.post("/api/v1/profiles", 
        json={
            "display_name": email.split("@")[0],
            "profile_type": profile_type
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return token

@pytest.fixture
async def scout_token(client: AsyncClient) -> str:
    return await create_authenticated_user(client, "scout@example.com", "SCOUT")

@pytest.fixture
async def student_token(client: AsyncClient) -> str:
    return await create_authenticated_user(client, "student@example.com", "STUDENT")

@pytest.fixture
async def another_scout_token(client: AsyncClient) -> str:
    return await create_authenticated_user(client, "scout2@example.com", "SCOUT")

@pytest.fixture
async def admin_token(client: AsyncClient, db_session) -> str:
    token = await create_authenticated_user(client, "admin@example.com", "SCOUT")
    # Manually promote to ADMIN in DB
    from camp_match.modules.identity.adapters.persistence.models import AccountModel
    from sqlalchemy import select
    
    result = await db_session.execute(select(AccountModel).where(AccountModel.email == "admin@example.com"))
    account = result.scalar_one()
    
    from camp_match.modules.security.adapters.persistence.models import SecurityUserRoleModel
    from camp_match.modules.security.domain.value_objects import Role
    
    admin_role = SecurityUserRoleModel(
        id=EntityId.new().value,
        identity_id=account.id,
        role=Role.ADMIN.name
    )
    db_session.add(admin_role)
    await db_session.commit()
    
    return token
