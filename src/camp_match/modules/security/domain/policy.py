from __future__ import annotations

from camp_match.modules.security.domain.value_objects import Permission, Role

_ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset([Permission.ADMIN_USERS_MANAGE, Permission.UNIVERSITY_MANAGE, Permission.HOUSING_MANAGE, Permission.EXAMPLE_TEST_PERMISSION]),
    Role.OPERATIONS: frozenset(),
    Role.STUDENT: frozenset(),
    Role.SCOUT: frozenset([Permission.HOUSING_MANAGE]),
}

_OWNERSHIP_SCOPED_PERMISSIONS: frozenset[Permission] = frozenset(
    [Permission.EXAMPLE_TEST_PERMISSION, Permission.HOUSING_MANAGE]
)


def permissions_for(role: Role) -> frozenset[Permission]:
    return _ROLE_PERMISSIONS.get(role, frozenset())


def is_ownership_scoped(permission: Permission) -> bool:
    return permission in _OWNERSHIP_SCOPED_PERMISSIONS
