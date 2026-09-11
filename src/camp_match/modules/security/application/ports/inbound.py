from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from camp_match.modules.security.domain.value_objects import (
    AuthorizationDecision,
    Permission,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class AuthorizationRequest:
    identity_id: EntityId
    permission: Permission
    resource_owner_id: EntityId | None = None


class AuthorizationService(Protocol):
    async def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        ...
