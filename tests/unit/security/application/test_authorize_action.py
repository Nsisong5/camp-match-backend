import pytest
from unittest.mock import AsyncMock
import uuid

from camp_match.modules.security.application.ports.inbound import AuthorizationRequest
from camp_match.modules.security.application.use_cases.authorize_action import AuthorizeActionUseCase
from camp_match.modules.security.domain.value_objects import (
    AuthorizationOutcome,
    Permission,
    Role,
)
from camp_match.shared_kernel.domain.identifiers import EntityId

@pytest.fixture
def mock_role_repo():
    return AsyncMock()

@pytest.fixture
def mock_profile_provider():
    return AsyncMock()

@pytest.fixture
def use_case(mock_role_repo, mock_profile_provider):
    return AuthorizeActionUseCase(mock_role_repo, mock_profile_provider)

@pytest.fixture
def identity_id():
    return EntityId.from_string(str(uuid.uuid4()))

@pytest.mark.asyncio
async def test_role_scoped_permission_allowed(use_case, mock_role_repo, mock_profile_provider, identity_id):
    mock_role_repo.get_assigned_roles.return_value = frozenset([Role.ADMIN])
    mock_profile_provider.get_profile_type.return_value = None
    
    request = AuthorizationRequest(identity_id, Permission.ADMIN_USERS_MANAGE)
    decision = await use_case.execute(request)
    
    assert decision.outcome == AuthorizationOutcome.ALLOWED

@pytest.mark.asyncio
async def test_missing_permission_denied(use_case, mock_role_repo, mock_profile_provider, identity_id):
    mock_role_repo.get_assigned_roles.return_value = frozenset([Role.STUDENT])
    mock_profile_provider.get_profile_type.return_value = None
    
    request = AuthorizationRequest(identity_id, Permission.ADMIN_USERS_MANAGE)
    decision = await use_case.execute(request)
    
    assert decision.outcome == AuthorizationOutcome.DENIED

@pytest.mark.asyncio
async def test_ownership_scoped_matching_owner_allowed(use_case, mock_role_repo, mock_profile_provider, identity_id):
    mock_role_repo.get_assigned_roles.return_value = frozenset([Role.STUDENT])
    mock_profile_provider.get_profile_type.return_value = None
    
    request = AuthorizationRequest(identity_id, Permission.EXAMPLE_TEST_PERMISSION, resource_owner_id=identity_id)
    decision = await use_case.execute(request)
    
    assert decision.outcome == AuthorizationOutcome.ALLOWED

@pytest.mark.asyncio
async def test_ownership_scoped_mismatched_owner_denied(use_case, mock_role_repo, mock_profile_provider, identity_id):
    mock_role_repo.get_assigned_roles.return_value = frozenset([Role.STUDENT])
    mock_profile_provider.get_profile_type.return_value = None
    other_id = EntityId.from_string(str(uuid.uuid4()))
    
    request = AuthorizationRequest(identity_id, Permission.EXAMPLE_TEST_PERMISSION, resource_owner_id=other_id)
    decision = await use_case.execute(request)
    
    assert decision.outcome == AuthorizationOutcome.DENIED

@pytest.mark.asyncio
async def test_ownership_scoped_admin_bypass_allowed(use_case, mock_role_repo, mock_profile_provider, identity_id):
    mock_role_repo.get_assigned_roles.return_value = frozenset([Role.ADMIN])
    mock_profile_provider.get_profile_type.return_value = None
    other_id = EntityId.from_string(str(uuid.uuid4()))
    
    request = AuthorizationRequest(identity_id, Permission.EXAMPLE_TEST_PERMISSION, resource_owner_id=other_id)
    decision = await use_case.execute(request)
    
    assert decision.outcome == AuthorizationOutcome.ALLOWED

@pytest.mark.asyncio
async def test_ownership_scoped_missing_context_invalid(use_case, mock_role_repo, mock_profile_provider, identity_id):
    mock_role_repo.get_assigned_roles.return_value = frozenset([Role.STUDENT])
    mock_profile_provider.get_profile_type.return_value = None
    
    request = AuthorizationRequest(identity_id, Permission.EXAMPLE_TEST_PERMISSION, resource_owner_id=None)
    decision = await use_case.execute(request)
    
    assert decision.outcome == AuthorizationOutcome.INVALID_CONTEXT
