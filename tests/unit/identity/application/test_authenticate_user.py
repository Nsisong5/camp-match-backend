from datetime import UTC, datetime

import pytest

from camp_match.modules.identity.application.errors import (
    AccountDisabled,
    AccountSuspended,
    InvalidCredentials,
)
from camp_match.modules.identity.application.ports.inbound import AuthenticationRequest
from camp_match.modules.identity.application.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
)
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import EmailAddress
from camp_match.shared_kernel.domain.identifiers import EntityId
from tests.support.identity_fakes import (
    FakeAuthenticationSessionPort,
    FakeIdentityRepository,
    FakePasswordHasher,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_authenticate_user_success():
    repo = FakeIdentityRepository()
    hasher = FakePasswordHasher()
    session_port = FakeAuthenticationSessionPort()

    email = EmailAddress("test@example.com")
    pwd_hash = hasher.hash("password123")
    account = UserAccount.register(
        id=EntityId.new(),
        email=email,
        password_hash=pwd_hash,
        created_at=datetime.now(UTC),
    )
    await repo.add(account)

    use_case = AuthenticateUserUseCase(repo, hasher, session_port)
    request = AuthenticationRequest(email="test@example.com", raw_password="password123")

    response = await use_case.execute(request)

    assert response.access_token.startswith("access_")
    assert response.token_type == "bearer"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_authenticate_user_invalid_email_or_password():
    repo = FakeIdentityRepository()
    hasher = FakePasswordHasher()
    session_port = FakeAuthenticationSessionPort()

    use_case = AuthenticateUserUseCase(repo, hasher, session_port)

    # Unknown email
    with pytest.raises(InvalidCredentials):
        req = AuthenticationRequest(email="unknown@example.com", raw_password="any")
        await use_case.execute(req)

    # Wrong password
    email = EmailAddress("test@example.com")
    account = UserAccount.register(
        id=EntityId.new(),
        email=email,
        password_hash=hasher.hash("correct"),
        created_at=datetime.now(UTC),
    )
    await repo.add(account)

    with pytest.raises(InvalidCredentials):
        req = AuthenticationRequest(email="test@example.com", raw_password="wrong")
        await use_case.execute(req)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_authenticate_user_blocked_status():
    repo = FakeIdentityRepository()
    hasher = FakePasswordHasher()
    session_port = FakeAuthenticationSessionPort()
    use_case = AuthenticateUserUseCase(repo, hasher, session_port)

    # Suspended
    acc1 = UserAccount.register(
        id=EntityId.new(),
        email=EmailAddress("susp@example.com"),
        password_hash=hasher.hash("pwd"),
        created_at=datetime.now(UTC),
    )
    acc1.suspend()
    await repo.add(acc1)
    with pytest.raises(AccountSuspended):
        req = AuthenticationRequest(email="susp@example.com", raw_password="pwd")
        await use_case.execute(req)

    # Disabled
    acc2 = UserAccount.register(
        id=EntityId.new(),
        email=EmailAddress("dis@example.com"),
        password_hash=hasher.hash("pwd"),
        created_at=datetime.now(UTC),
    )
    acc2.disable()
    await repo.add(acc2)
    with pytest.raises(AccountDisabled):
        req = AuthenticationRequest(email="dis@example.com", raw_password="pwd")
        await use_case.execute(req)
