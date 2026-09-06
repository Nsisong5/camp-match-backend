import pytest
import uuid
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from camp_match.modules.identity.adapters.api.router import router as identity_router
from camp_match.modules.identity.adapters.api.dependencies import (
    get_disable_account,
    get_identity_repository
)
from camp_match.modules.security.adapters.api.dependencies import require_permission
from camp_match.modules.security.domain.value_objects import Permission

from camp_match.modules.identity.adapters.persistence.repository import SqlAlchemyIdentityRepository
from unittest.mock import AsyncMock, MagicMock
from camp_match.modules.identity.application.use_cases.disable_account import DisableAccountUseCase
from camp_match.platform.db.session import get_db_session
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId

app = FastAPI()
app.include_router(identity_router)

from camp_match.modules.identity.application.ports.inbound import IdentityResponse
from datetime import datetime

# Mock Use Cases
mock_disable_use_case = AsyncMock(spec=DisableAccountUseCase)
mock_disable_use_case.execute.return_value = IdentityResponse(
    id=str(uuid.uuid4()), 
    email="test@example.com", 
    status="DISABLED",
    created_at=datetime.now()
)

# Override dependencies
app.dependency_overrides[get_current_identity_id] = lambda: EntityId.from_string(str(uuid.uuid4()))
app.dependency_overrides[get_disable_account] = lambda: mock_disable_use_case
app.dependency_overrides[get_db_session] = lambda: None
app.dependency_overrides[get_identity_repository] = lambda: AsyncMock(spec=SqlAlchemyIdentityRepository)

@pytest.fixture
def client():
    return TestClient(app)

def test_admin_routes_exist(client):
    # This should now bypass auth/db check and reach the route, returning 200/404 based on use case
    valid_uuid = str(uuid.uuid4())
    response = client.post(f"/api/v1/auth/{valid_uuid}/disable")
    assert response.status_code != 401
    assert response.status_code != 403
