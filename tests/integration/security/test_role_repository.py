import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.modules.security.domain.value_objects import Role
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.mark.asyncio
async def test_role_repository_persistence(db_session: AsyncSession):
    repo = SqlAlchemyRoleRepository(db_session)
    identity_id = EntityId.from_string(str(uuid.uuid4()))
    role = Role.ADMIN
    
    # Assign
    await repo.assign_role(identity_id, role)
    await db_session.commit()
    
    # Retrieve
    roles = await repo.get_assigned_roles(identity_id)
    assert role in roles
    
    # Assign again (idempotent)
    await repo.assign_role(identity_id, role)
    await db_session.commit()
    roles = await repo.get_assigned_roles(identity_id)
    assert len(roles) == 1
    
    # Revoke
    await repo.revoke_role(identity_id, role)
    await db_session.commit()
    roles = await repo.get_assigned_roles(identity_id)
    assert role not in roles
    
    # Revoke again (idempotent)
    await repo.revoke_role(identity_id, role)
    await db_session.commit()
    roles = await repo.get_assigned_roles(identity_id)
    assert role not in roles
