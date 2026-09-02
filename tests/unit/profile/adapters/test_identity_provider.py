from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from camp_match.modules.identity.application.ports.inbound import GetIdentityById, IdentityResponse
from camp_match.modules.profile.adapters.identity.identity_provider import InProcessIdentityProvider
from camp_match.shared_kernel.application.errors import NotFoundError
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.mark.asyncio
async def test_get_identity_found():
    mock_use_case = AsyncMock(spec=GetIdentityById)
    identity_id = EntityId.new()
    expected_response = IdentityResponse(
        id=str(identity_id),
        email="test@example.com",
        status="active",
        created_at=datetime.utcnow()
    )
    mock_use_case.execute.return_value = expected_response
    
    provider = InProcessIdentityProvider(mock_use_case)
    result = await provider.get_identity(identity_id)
    
    assert result is not None
    assert result.id == identity_id
    assert result.email == "test@example.com"
    assert result.status == "active"
    mock_use_case.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_identity_not_found():
    mock_use_case = AsyncMock(spec=GetIdentityById)
    mock_use_case.execute.side_effect = NotFoundError("Identity not found")
    
    provider = InProcessIdentityProvider(mock_use_case)
    result = await provider.get_identity(EntityId.new())
    
    assert result is None
    mock_use_case.execute.assert_called_once()
