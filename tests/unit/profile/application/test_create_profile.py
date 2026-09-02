from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from camp_match.modules.profile.application.errors import (
    ProfileAlreadyExists,
    UnauthorizedProfileAccess,
)
from camp_match.modules.profile.application.ports.inbound import CreateProfileRequest
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.modules.profile.application.use_cases.create_profile import CreateProfileUseCase
from camp_match.modules.profile.domain.value_objects import ProfileType
from camp_match.shared_kernel.domain.identifiers import EntityId
from tests.support.fixed_clock import FixedClock
from tests.support.profile_fakes import FakeIdentityProvider, FakeProfileRepository


@pytest.mark.asyncio
async def test_create_profile_success():
    repo = FakeProfileRepository()
    idp = FakeIdentityProvider()
    event_bus = AsyncMock()
    clock = FixedClock(datetime(2026, 1, 1))
    uow = AsyncMock(spec=UnitOfWork)
    
    identity_id = EntityId.new()
    idp.set_identity(AsyncMock(id=identity_id, email="test@example.com", status="ACTIVE"))
    
    use_case = CreateProfileUseCase(repo, idp, event_bus, clock, uow)
    
    request = CreateProfileRequest(
        identity_id=identity_id,
        display_name="Test User",
        profile_type=ProfileType.STUDENT,
        student_details={"university_name": "Uni"}
    )
    
    response = await use_case.execute(request)
    
    assert response.identity_id == identity_id
    assert response.display_name == "Test User"
    assert response.profile_type == ProfileType.STUDENT
    assert await repo.get_by_identity_id(identity_id) is not None
    event_bus.publish.assert_called_once()

@pytest.mark.asyncio
async def test_create_profile_blocked_by_inactive_identity():
    repo = FakeProfileRepository()
    idp = FakeIdentityProvider()
    event_bus = AsyncMock()
    clock = FixedClock(datetime(2026, 1, 1))
    uow = AsyncMock(spec=UnitOfWork)
    
    identity_id = EntityId.new()
    idp.set_identity(AsyncMock(id=identity_id, email="test@example.com", status="SUSPENDED"))
    
    use_case = CreateProfileUseCase(repo, idp, event_bus, clock, uow)
    
    request = CreateProfileRequest(
        identity_id=identity_id,
        display_name="Test User",
        profile_type=ProfileType.STUDENT,
    )
    
    with pytest.raises(UnauthorizedProfileAccess):
        await use_case.execute(request)

@pytest.mark.asyncio
async def test_create_profile_duplicate_rejection():
    repo = FakeProfileRepository()
    idp = FakeIdentityProvider()
    event_bus = AsyncMock()
    clock = FixedClock(datetime(2026, 1, 1))
    uow = AsyncMock(spec=UnitOfWork)
    
    identity_id = EntityId.new()
    idp.set_identity(AsyncMock(id=identity_id, email="test@example.com", status="ACTIVE"))
    
    # Pre-add profile
    request = CreateProfileRequest(
        identity_id=identity_id,
        display_name="Test User",
        profile_type=ProfileType.STUDENT,
        student_details={"university_name": "Uni"}
    )
    
    use_case = CreateProfileUseCase(repo, idp, event_bus, clock, uow)
    await use_case.execute(request)
    
    # Try adding again
    with pytest.raises(ProfileAlreadyExists):
        await use_case.execute(request)
