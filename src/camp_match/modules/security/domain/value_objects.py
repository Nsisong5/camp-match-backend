from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from camp_match.shared_kernel.domain.identifiers import EntityId


class Role(Enum):
    STUDENT = auto()
    SCOUT = auto()
    ADMIN = auto()
    OPERATIONS = auto()


class Permission(Enum):
    ADMIN_USERS_MANAGE = "admin.users.manage"
    UNIVERSITY_MANAGE = "university.manage"
    HOUSING_MANAGE = "housing.manage"
    EXAMPLE_TEST_PERMISSION = "test.ownership.scoped"  # Test-only


class AuthorizationOutcome(Enum):
    ALLOWED = auto()
    DENIED = auto()
    UNAUTHENTICATED = auto()
    INVALID_CONTEXT = auto()


@dataclass(frozen=True)
class AuthorizationDecision:
    outcome: AuthorizationOutcome
    reason: str


@dataclass(frozen=True)
class Principal:
    identity_id: EntityId
    roles: frozenset[Role]

    @classmethod
    def create(cls, identity_id: EntityId, roles: frozenset[Role]) -> Principal:
        return cls(identity_id=identity_id, roles=roles)
