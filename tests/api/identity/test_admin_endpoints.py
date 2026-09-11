import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from camp_match.modules.identity.adapters.api.dependencies import get_disable_account, get_identity_repository
from camp_match.modules.identity.adapters.api.router import router as identity_router
from camp_match.modules.identity.application.ports.inbound import IdentityResponse
from camp_match.modules.identity.application.use_cases.disable_account import DisableAccountUseCase
from camp_match.modules.security.adapters.api.dependencies import get_current_principal, require_permission
from camp_match.modules.security.application.use_cases.authorize_action import AuthorizeActionUseCase
from camp_match.modules.security.domain.value_objects import AuthorizationDecision, AuthorizationOutcome, Permission, Principal, Role
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId

# Set up FastAPI app for testing
app = FastAPI()
app.include_router(identity_router)

# Initialize app state
app.state.db_session_factory = MagicMock()

# Mock Authorization/Security dependencies
mock_principal = Principal.create(EntityId.new(), frozenset([Role.ADMIN]))
app.dependency_overrides[get_current_principal] = lambda: mock_principal
app.dependency_overrides[get_current_identity_id] = lambda: mock_principal.identity_id

# Mock Identity Repository
mock_identity_repo = AsyncMock()
app.dependency_overrides[get_identity_repository] = lambda: mock_identity_repo

# Mock Authorization
mock_auth_use_case = AsyncMock(spec=AuthorizeActionUseCase)
mock_auth_use_case.execute.return_value = AuthorizationDecision(outcome=AuthorizationOutcome.ALLOWED, reason="Test bypass")

# Mock DisableAccountUseCase
mock_disable_use_case = AsyncMock(spec=DisableAccountUseCase)
app.dependency_overrides[get_disable_account] = lambda: mock_disable_use_case

@pytest.fixture
def client():
    with patch("camp_match.modules.security.adapters.api.dependencies.AuthorizeActionUseCase", return_value=mock_auth_use_case):
        yield TestClient(app)

def test_admin_routes_exist(client):
    # This should now bypass auth and reach the route
    valid_uuid = str(uuid.uuid4())
    
    # Mock the repository return value in the use case
    mock_disable_use_case.execute.return_value = IdentityResponse(
        id=valid_uuid, 
        email="test@example.com", 
        status="DISABLED",
        created_at=datetime.now()
    )
    
    response = client.post(f"/api/v1/auth/{valid_uuid}/disable")
    assert response.status_code != 401
    assert response.status_code != 403
    assert response.status_code == 200
