from datetime import UTC, datetime

import pytest

from camp_match.modules.identity.application.errors import (
    IdentityAlreadyExists,
    InvalidAuthenticationRequest,
)
from camp_match.modules.identity.application.ports.inbound import RegistrationRequest
from camp_match.modules.identity.application.use_cases.register_account import (
    RegisterAccountUseCase,
)
from camp_match.modules.identity.domain.events import UserRegistered
from tests.support.fixed_clock import FixedClock
from tests.support.identity_fakes import (
    FakeEventBus,
    FakeIdentityRepository,
    FakePasswordHasher,
    FakeUnitOfWork,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_register_account_success():
    repo = FakeIdentityRepository()
    hasher = FakePasswordHasher()
    now = datetime.now(UTC)
    clock = FixedClock(now)
    bus = FakeEventBus()
    uow = FakeUnitOfWork()

    use_case = RegisterAccountUseCase(repo, hasher, clock, bus, uow)
    request = RegistrationRequest(email="test@example.com", raw_password="password123")

    response = await use_case.execute(request)

    assert response.email == "test@example.com"
    assert response.status == "ACTIVE"
    assert response.created_at == now
    assert uow.committed is True
    assert any(isinstance(e, UserRegistered) for e in bus.events)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_register_account_duplicate_email():
    repo = FakeIdentityRepository()
    hasher = FakePasswordHasher()
    clock = FixedClock(datetime.now(UTC))
    bus = FakeEventBus()
    uow = FakeUnitOfWork()

    use_case = RegisterAccountUseCase(repo, hasher, clock, bus, uow)
    request = RegistrationRequest(email="test@example.com", raw_password="password123")

    # Register once
    await use_case.execute(request)

    # Try again
    with pytest.raises(IdentityAlreadyExists):
        await use_case.execute(request)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_register_account_invalid_email():
    repo = FakeIdentityRepository()
    hasher = FakePasswordHasher()
    clock = FixedClock(datetime.now(UTC))
    bus = FakeEventBus()
    uow = FakeUnitOfWork()

    use_case = RegisterAccountUseCase(repo, hasher, clock, bus, uow)
    request = RegistrationRequest(email="invalid-email", raw_password="password123")

    with pytest.raises(InvalidAuthenticationRequest):
        await use_case.execute(request)
