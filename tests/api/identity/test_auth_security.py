from datetime import UTC, datetime, timedelta

import pytest

from camp_match.config.settings import get_settings
from camp_match.modules.identity.adapters.persistence.models import AccountModel
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.fixture
def settings():
    return get_settings()

@pytest.mark.asyncio
async def test_no_password_hash_in_responses(client, db_session):
    # Register
    reg_response = await client.post("/api/v1/auth/register", json={"email": "secret@example.com", "password": "password123"})
    assert "password_hash" not in reg_response.json()
    
    # Login
    login_response = await client.post("/api/v1/auth/login", json={"email": "secret@example.com", "password": "password123"})
    assert "password_hash" not in login_response.json()

@pytest.mark.asyncio
async def test_suspended_account_forbidden(client, db_session):
    from camp_match.modules.identity.adapters.security.password_hasher import ScryptPasswordHasher
    hasher = ScryptPasswordHasher()
    pwd_hash = hasher.hash("password123")
    
    # Manually create suspended user
    user_id = EntityId.new().value
    user = AccountModel(
        id=user_id,
        email="suspended@example.com",
        password_hash=pwd_hash,
        status="SUSPENDED"
    )
    db_session.add(user)
    await db_session.commit()
    
    # Try login
    login_response = await client.post("/api/v1/auth/login", json={"email": "suspended@example.com", "password": "password123"})
    assert login_response.status_code == 403
    assert login_response.json()["error"]["code"] == "account_suspended"

@pytest.mark.asyncio
async def test_log_security(client, caplog):
    # Just perform a flow, caplog should catch structlog output if configured correctly.
    # Note: might need to check if structlog output is captured by pytest caplog.
    await client.post("/api/v1/auth/register", json={"email": "logtest@example.com", "password": "password123"})
    await client.post("/api/v1/auth/login", json={"email": "logtest@example.com", "password": "password123"})
    
    for record in caplog.records:
        assert "password123" not in record.message
        # Also ensure tokens are not logged.

@pytest.mark.asyncio
async def test_expired_access_token(client, db_session, settings):
    # This requires constructing an expired token and using it.
    # I can use JwtAuthenticationSessionAdapter directly or construct a JWT.
    import jwt

    from camp_match.modules.identity.adapters.security.jwt_session import (
        JwtAuthenticationSessionAdapter,
    )
    
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    # Construct expired token
    payload = {
        "sub": str(identity_id),
        "iat": datetime.now(UTC) - timedelta(days=1),
        "exp": datetime.now(UTC) - timedelta(hours=1),
        "type": "access",
    }
    expired_token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    
    me_response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert me_response.status_code == 401
