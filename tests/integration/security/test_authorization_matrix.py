from unittest.mock import AsyncMock

import pytest

from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.modules.security.application.ports.inbound import AuthorizationRequest
from camp_match.modules.security.application.use_cases.authorize_action import (
    AuthorizeActionUseCase,
)
from camp_match.modules.security.domain.value_objects import AuthorizationOutcome, Permission, Role
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.mark.asyncio
async def test_authorization_matrix(db_session):
    # Setup
    repo = SqlAlchemyRoleRepository(db_session)
    # Using a fake profile provider to simplify
    mock_profile_provider = AsyncMock()
    mock_profile_provider.get_profile_type.return_value = None
    
    use_case = AuthorizeActionUseCase(repo, mock_profile_provider)
    
    admin_id = EntityId.from_string("3f490d86-e84d-4337-a496-a4df4b2d8fb6")
    user_id = EntityId.from_string("8156b41b-e5cd-4810-8441-2eb7d947cac5")
    
    # 1. Assign ADMIN to admin_id
    await repo.assign_role(admin_id, Role.ADMIN)
    await db_session.commit()
    
    # 2. Test Admin can disable (requires ADMIN_USERS_MANAGE)
    # Note: ADMIN_USERS_MANAGE is role-scoped, so resource_owner_id is not needed.
    # Wait, Section 8 instructions say ADMIN_USERS_MANAGE is role-scoped.
    # The actual requirement for disable/reactivate in Chunk 10 says "require_permission(Permission.ADMIN_USERS_MANAGE)".
    # This aligns with it being role-scoped.
    
    request = AuthorizationRequest(admin_id, Permission.ADMIN_USERS_MANAGE)
    decision = await use_case.execute(request)
    assert decision.outcome == AuthorizationOutcome.ALLOWED
    
    # 3. Test User (non-admin) cannot disable
    request = AuthorizationRequest(user_id, Permission.ADMIN_USERS_MANAGE)
    decision = await use_case.execute(request)
    assert decision.outcome == AuthorizationOutcome.DENIED
