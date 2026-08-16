from datetime import UTC, datetime

import pytest

from camp_match.modules.identity.application.errors import IdentityNotFound
from camp_match.modules.identity.application.ports.inbound import IdentityQueryRequest
from camp_match.modules.identity.application.use_cases.get_identity import GetIdentityByIdUseCase
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import EmailAddress
from camp_match.shared_kernel.domain.identifiers import EntityId
from tests.support.identity_fakes import FakeIdentityRepository


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_identity_success():
    repo = FakeIdentityRepository()
    account_id = EntityId.new()
    account = UserAccount.register(
        id=account_id,
        email=EmailAddress("test@example.com"),
        password_hash="hash",
        created_at=datetime.now(UTC),
    )
    await repo.add(account)

    use_case = GetIdentityByIdUseCase(repo)
    request = IdentityQueryRequest(identity_id=str(account_id))

    response = await use_case.execute(request)

    assert response.id == str(account_id)
    assert response.email == "test@example.com"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_identity_not_found():
    repo = FakeIdentityRepository()
    use_case = GetIdentityByIdUseCase(repo)
    request = IdentityQueryRequest(identity_id=str(EntityId.new()))

    with pytest.raises(IdentityNotFound):
        await use_case.execute(request)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_identity_invalid_id():
    repo = FakeIdentityRepository()
    use_case = GetIdentityByIdUseCase(repo)
    request = IdentityQueryRequest(identity_id="not-a-uuid")

    with pytest.raises(IdentityNotFound):
        await use_case.execute(request)
