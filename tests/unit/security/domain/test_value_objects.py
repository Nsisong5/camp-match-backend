import pytest
from camp_match.modules.security.domain.value_objects import Role, Permission, AuthorizationOutcome
from camp_match.modules.security.domain.policy import _ROLE_PERMISSIONS

def test_role_permissions_mapping():
    assert Permission.ADMIN_USERS_MANAGE in _ROLE_PERMISSIONS[Role.ADMIN]
    assert len(_ROLE_PERMISSIONS[Role.OPERATIONS]) == 0
    assert len(_ROLE_PERMISSIONS[Role.STUDENT]) == 0
    assert len(_ROLE_PERMISSIONS[Role.SCOUT]) == 0

def test_authorization_outcomes():
    assert AuthorizationOutcome.ALLOWED.name == "ALLOWED"
    assert AuthorizationOutcome.DENIED.name == "DENIED"
    assert AuthorizationOutcome.UNAUTHENTICATED.name == "UNAUTHENTICATED"
    assert AuthorizationOutcome.INVALID_CONTEXT.name == "INVALID_CONTEXT"
