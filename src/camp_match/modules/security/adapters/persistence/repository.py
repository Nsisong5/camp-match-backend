from __future__ import annotations

import uuid
from typing import FrozenSet

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.security.adapters.persistence.models import SecurityUserRoleModel
from camp_match.modules.security.application.ports.outbound import RoleRepository
from camp_match.modules.security.domain.value_objects import Role
from camp_match.shared_kernel.domain.identifiers import EntityId


class SqlAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_assigned_roles(self, identity_id: EntityId) -> FrozenSet[Role]:
        stmt = select(SecurityUserRoleModel.role).where(
            SecurityUserRoleModel.identity_id == identity_id.value
        )
        result = await self._session.execute(stmt)
        roles = result.scalars().all()
        return frozenset(Role[role] for role in roles)

    async def assign_role(self, identity_id: EntityId, role: Role) -> None:
        model = SecurityUserRoleModel(
            id=uuid.uuid4(), identity_id=identity_id.value, role=role.name
        )
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError:
            # Idempotent: ignore if role already exists
            await self._session.rollback()

    async def revoke_role(self, identity_id: EntityId, role: Role) -> None:
        stmt = delete(SecurityUserRoleModel).where(
            SecurityUserRoleModel.identity_id == identity_id.value,
            SecurityUserRoleModel.role == role.name,
        )
        await self._session.execute(stmt)
        # Idempotent: no error if role didn't exist
