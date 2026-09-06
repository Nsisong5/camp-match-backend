from __future__ import annotations

import structlog
from typing import Optional

from camp_match.modules.security.application.ports.inbound import AuthorizationRequest
from camp_match.modules.security.application.ports.outbound import RoleRepository, ProfileProvider
from camp_match.modules.security.domain.policy import permissions_for, is_ownership_scoped
from camp_match.modules.security.domain.value_objects import (
    AuthorizationDecision,
    AuthorizationOutcome,
    Principal,
    Role,
)

logger = structlog.get_logger()


class AuthorizeActionUseCase:
    def __init__(
        self,
        role_repository: RoleRepository,
        profile_provider: ProfileProvider,
    ) -> None:
        self._role_repository = role_repository
        self._profile_provider = profile_provider

    async def execute(self, request: AuthorizationRequest) -> AuthorizationDecision:
        # 1. Resolve roles
        assigned_roles = await self._role_repository.get_assigned_roles(request.identity_id)
        profile_type_str = await self._profile_provider.get_profile_type(request.identity_id)
        
        resolved_roles = set(assigned_roles)
        if profile_type_str:
            try:
                resolved_roles.add(Role[profile_type_str])
            except KeyError:
                pass
        
        principal = Principal.create(request.identity_id, frozenset(resolved_roles))
        
        # 2. Map permissions
        granted_permissions = set()
        for role in principal.roles:
            granted_permissions.update(permissions_for(role))
            
        # 3. Check authorization
        if request.permission not in granted_permissions:
            logger.warning(
                "authorization_denied",
                identity_id=str(request.identity_id),
                permission=request.permission.value,
                roles=[r.name for r in principal.roles],
                reason="Permission not granted by roles"
            )
            return AuthorizationDecision(AuthorizationOutcome.DENIED, "Permission not granted")
        
        # 4. Ownership scoped check
        if is_ownership_scoped(request.permission):
            if request.resource_owner_id is None:
                logger.warning(
                    "authorization_invalid_context",
                    identity_id=str(request.identity_id),
                    permission=request.permission.value
                )
                return AuthorizationDecision(AuthorizationOutcome.INVALID_CONTEXT, "Missing resource owner")
            
            if request.identity_id == request.resource_owner_id or Role.ADMIN in principal.roles:
                logger.info("authorization_allowed", identity_id=str(request.identity_id), permission=request.permission.value)
                return AuthorizationDecision(AuthorizationOutcome.ALLOWED, "Ownership match or Admin")
            
            logger.warning(
                "authorization_denied",
                identity_id=str(request.identity_id),
                resource_owner_id=str(request.resource_owner_id),
                permission=request.permission.value,
                reason="Ownership mismatch"
            )
            return AuthorizationDecision(AuthorizationOutcome.DENIED, "Ownership mismatch")
        
        # 5. Success
        logger.info("authorization_allowed", identity_id=str(request.identity_id), permission=request.permission.value)
        return AuthorizationDecision(AuthorizationOutcome.ALLOWED, "Granted")
