from unittest.mock import AsyncMock

import pytest

from camp_match.modules.profile.application.errors import ProfileNotFound
from camp_match.modules.profile.application.ports.inbound import ProfileResponse
from camp_match.modules.security.adapters.profile.profile_provider import InProcessProfileProvider
from camp_match.modules.security.domain.value_objects import Role
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.mark.asyncio
async def test_in_process_profile_provider_maps_student():
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = ProfileResponse(
        id="p1",
        identity_id="i1",
        profile_type="STUDENT",
        display_name="Student",
        completeness_percentage=100,
        bio=None,
        phone_number=None,
        avatar_url=None,
        student_details={},
        scout_details=None,
    )
    provider = InProcessProfileProvider(mock_use_case)
    identity_id = EntityId.from_string("550e8400-e29b-41d4-a716-446655440000")
    
    result = await provider.get_profile_type(identity_id)
    
    assert result == Role.STUDENT.name

@pytest.mark.asyncio
async def test_in_process_profile_provider_maps_scout():
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = ProfileResponse(
        id="p1",
        identity_id="i1",
        profile_type="SCOUT",
        display_name="Scout",
        completeness_percentage=100,
        bio=None,
        phone_number=None,
        avatar_url=None,
        student_details=None,
        scout_details={},
    )
    provider = InProcessProfileProvider(mock_use_case)
    identity_id = EntityId.from_string("550e8400-e29b-41d4-a716-446655440000")
    
    result = await provider.get_profile_type(identity_id)
    
    assert result == Role.SCOUT.name

@pytest.mark.asyncio
async def test_in_process_profile_provider_returns_none_when_not_found():
    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = ProfileNotFound("Not found")
    provider = InProcessProfileProvider(mock_use_case)
    identity_id = EntityId.from_string("550e8400-e29b-41d4-a716-446655440000")
    
    result = await provider.get_profile_type(identity_id)
    
    assert result is None
