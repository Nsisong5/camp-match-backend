from datetime import UTC, datetime

import pytest

from camp_match.modules.identity.application.ports.inbound import UpdateStatusRequest
from camp_match.modules.identity.application.use_cases.disable_account import DisableAccountUseCase
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.events import AccountDisabled
from camp_match.modules.identity.domain.value_objects import AccountStatus, EmailAddress
from camp_match.shared_kernel.domain.identifiers import EntityId
from tests.support.fixed_clock import FixedClock
from tests.support.identity_fakes import FakeEventBus, FakeIdentityRepository, FakeUnitOfWork


@pytest.mark.asyncio
@pytest.mark.unit
async def test_disable_account_success():
    repo = FakeIdentityRepository()
    bus = FakeEventBus()
    uow = FakeUnitOfWork()
    clock = FixedClock(datetime.now(UTC))
    account_id = EntityId.new()
    account = UserAccount.register(
        id=account_id,
        email=EmailAddress("test@example.com"),
        password_hash="hash",
        created_at=clock.now(),
    )
    await repo.add(account)

    use_case = DisableAccountUseCase(repo, clock, bus, uow)
    request = UpdateStatusRequest(identity_id=str(account_id))

    response = await use_case.execute(request)

    assert response.status == "DISABLED"
    assert account.status == AccountStatus.DISABLED
    assert uow.committed is True
    assert any(isinstance(e, AccountDisabled) for e in bus.events)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_disable_account_noop():
    repo = FakeIdentityRepository()
    bus = FakeEventBus()
    uow = FakeUnitOfWork()
    clock = FixedClock(datetime.now(UTC))
    account_id = EntityId.new()
    account = UserAccount.register(
        id=account_id,
        email=EmailAddress("test@example.com"),
        password_hash="hash",
        created_at=clock.now(),
    )
    account.disable()
    await repo.add(account)

    use_case = DisableAccountUseCase(repo, clock, bus, uow)
    request = UpdateStatusRequest(identity_id=str(account_id))

    response = await use_case.execute(request)

    assert response.status == "DISABLED"
    assert uow.committed is False  # Should not have committed if no change
    assert len(bus.events) == 0  # Should not have published event
