from __future__ import annotations

from typing import FrozenSet

from camp_match.modules.security.domain.value_objects import Permission, Role

_ROLE_PERMISSIONS: dict[Role, FrozenSet[Permission]] = {
    Role.ADMIN: frozenset([Permission.ADMIN_USERS_MANAGE, Permission.EXAMPLE_TEST_PERMISSION]),
    Role.OPERATIONS: frozenset(),
    Role.STUDENT: frozenset([Permission.EXAMPLE_TEST_PERMISSION]),
    Role.SCOUT: frozenset(),
}

_OWNERSHIP_SCOPED_PERMISSIONS: FrozenSet[Permission] = frozenset(
    [Permission.EXAMPLE_TEST_PERMISSION]
)


def permissions_for(role: Role) -> FrozenSet[Permission]:
    return _ROLE_PERMISSIONS.get(role, frozenset())


def is_ownership_scoped(permission: Permission) -> bool:
    return permission in _OWNERSHIP_SCOPED_PERMISSIONS
