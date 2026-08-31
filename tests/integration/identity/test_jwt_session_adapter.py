import pytest
from datetime import datetime, timedelta, timezone
from camp_match.modules.identity.adapters.security.jwt_session import JwtAuthenticationSessionAdapter
from camp_match.modules.identity.application.errors import InvalidCredentials
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.config.settings import get_settings, Settings
from sqlalchemy import select
from camp_match.modules.identity.adapters.persistence.models import RefreshTokenModel

@pytest.fixture
def settings():
    return get_settings()

@pytest.mark.integration
async def test_issue_and_decode_access_token(db_session, settings):
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    tokens = await adapter.issue_tokens(identity_id)
    
    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.token_type == "bearer"
    
    decoded_id = await adapter.decode_access_token(tokens.access_token)
    assert decoded_id == identity_id

@pytest.mark.integration
async def test_refresh_token_rotation(db_session, settings):
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    tokens = await adapter.issue_tokens(identity_id)
    old_refresh_token = tokens.refresh_token
    
    # Wait a bit to ensure iat (seconds) changes
    import asyncio
    await asyncio.sleep(1.1)
    
    new_tokens = await adapter.refresh(old_refresh_token)
    
    assert new_tokens.access_token != tokens.access_token
    assert new_tokens.refresh_token != tokens.refresh_token
    
    # Old token should be revoked
    with pytest.raises(InvalidCredentials):
        await adapter.refresh(old_refresh_token)

@pytest.mark.integration
async def test_revoke_token(db_session, settings):
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    tokens = await adapter.issue_tokens(identity_id)
    
    await adapter.revoke(tokens.refresh_token)
    
    with pytest.raises(InvalidCredentials):
        await adapter.refresh(tokens.refresh_token)

@pytest.mark.integration
async def test_revoke_is_idempotent(db_session, settings):
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    tokens = await adapter.issue_tokens(identity_id)
    
    await adapter.revoke(tokens.refresh_token)
    await adapter.revoke(tokens.refresh_token) # Should not raise

@pytest.mark.integration
async def test_decode_expired_token(db_session, settings):
    # Shorten expiry for test
    custom_settings = Settings(
        jwt_secret_key=settings.jwt_secret_key,
        jwt_access_token_expire_minutes=-1 # already expired
    )
    adapter = JwtAuthenticationSessionAdapter(db_session, custom_settings)
    identity_id = EntityId.new()
    
    tokens = await adapter.issue_tokens(identity_id)
    
    with pytest.raises(InvalidCredentials):
        await adapter.decode_access_token(tokens.access_token)

@pytest.mark.integration
async def test_decode_tampered_token(db_session, settings):
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    tokens = await adapter.issue_tokens(identity_id)
    tampered_token = tokens.access_token[:-5] + "aaaaa"
    
    with pytest.raises(InvalidCredentials):
        await adapter.decode_access_token(tampered_token)

@pytest.mark.integration
async def test_refresh_token_expired(db_session, settings):
    adapter = JwtAuthenticationSessionAdapter(db_session, settings)
    identity_id = EntityId.new()
    
    # Manually create an expired token in DB
    from hashlib import sha256
    import secrets
    raw_token = secrets.token_urlsafe(48)
    token_hash = sha256(raw_token.encode()).hexdigest()
    
    expired_token = RefreshTokenModel(
        id=EntityId.new().value,
        account_id=identity_id.value,
        token_hash=token_hash,
        issued_at=datetime.now(timezone.utc) - timedelta(days=40),
        expires_at=datetime.now(timezone.utc) - timedelta(days=10),
    )
    db_session.add(expired_token)
    await db_session.flush()
    
    with pytest.raises(InvalidCredentials):
        await adapter.refresh(raw_token)
