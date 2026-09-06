import pytest
from camp_match.modules.security.domain.value_objects import Permission, Role
from camp_match.modules.security.domain.policy import permissions_for, is_ownership_scoped

def test_permissions_for_role():
    assert Permission.ADMIN_USERS_MANAGE in permissions_for(Role.ADMIN)
    assert len(permissions_for(Role.OPERATIONS)) == 0
    assert len(permissions_for(Role.STUDENT)) == 0
    assert len(permissions_for(Role.SCOUT)) == 0

def test_is_ownership_scoped():
    assert not is_ownership_scoped(Permission.ADMIN_USERS_MANAGE)
    assert is_ownership_scoped(Permission.EXAMPLE_TEST_PERMISSION)
