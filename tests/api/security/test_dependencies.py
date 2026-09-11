import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from camp_match.modules.security.adapters.api.dependencies import require_permission
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.platform.security.authentication import get_current_identity_id

# Create a temporary app to test dependencies
app = FastAPI()

async def raise_unauthorized():
    raise HTTPException(status_code=401)

app.dependency_overrides[get_current_identity_id] = raise_unauthorized

@app.get("/test-protected", dependencies=[require_permission(Permission.ADMIN_USERS_MANAGE)])
async def protected_route():
    return {"status": "ok"}

@pytest.fixture
def client():
    return TestClient(app)

def test_no_token_returns_401(client):
    response = client.get("/test-protected")
    assert response.status_code == 401
