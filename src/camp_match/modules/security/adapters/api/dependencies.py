from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.profile.adapters.persistence.repository import SqlAlchemyProfileRepository
from camp_match.modules.profile.application.use_cases.get_current_user_profile import (
    GetCurrentUserProfileUseCase,
)
from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.modules.security.adapters.profile.profile_provider import InProcessProfileProvider
from camp_match.modules.security.application.use_cases.authorize_action import (
    AuthorizeActionUseCase,
)
from camp_match.modules.security.domain.value_objects import (
    AuthorizationOutcome,
    Permission,
    Principal,
    Role,
)
from camp_match.platform.db.session import get_db_session as get_session
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId


async def get_current_principal(
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    session: AsyncSession = Depends(get_session),
) -> Principal:
    # Build dependencies
    role_repo = SqlAlchemyRoleRepository(session)
    profile_repo = SqlAlchemyProfileRepository(session)
    profile_use_case = GetCurrentUserProfileUseCase(profile_repo)
    profile_provider = InProcessProfileProvider(profile_use_case)
    
    # Resolve roles
    assigned_roles = await role_repo.get_assigned_roles(identity_id)
    profile_type_str = await profile_provider.get_profile_type(identity_id)
    
    resolved_roles = set(assigned_roles)
    if profile_type_str:
        try:
            resolved_roles.add(Role[profile_type_str])
        except KeyError:
            pass
            
    return Principal.create(identity_id, frozenset(resolved_roles))

def require_permission(permission: Permission) -> Callable:
    async def _check_permission(
        identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
        session: AsyncSession = Depends(get_session),
    ) -> None:
        role_repo = SqlAlchemyRoleRepository(session)

        profile_repo = SqlAlchemyProfileRepository(session)
        profile_use_case = GetCurrentUserProfileUseCase(profile_repo)
        profile_provider = InProcessProfileProvider(profile_use_case)
        
        use_case = AuthorizeActionUseCase(role_repo, profile_provider)
        
        from camp_match.modules.security.application.ports.inbound import AuthorizationRequest
        
        decision = await use_case.execute(
            AuthorizationRequest(identity_id=identity_id, permission=permission)
        )
        
        if decision.outcome != AuthorizationOutcome.ALLOWED:
            raise HTTPException(status_code=403, detail="Forbidden")
            
    return Depends(_check_permission)
