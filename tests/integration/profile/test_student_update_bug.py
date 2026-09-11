import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.identity.adapters.persistence.repository import SqlAlchemyIdentityRepository
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import EmailAddress
from camp_match.modules.profile.adapters.persistence.repository import SqlAlchemyProfileRepository
from camp_match.modules.profile.domain.entities import Profile
from camp_match.modules.profile.domain.value_objects import (
    StudentProfileDetails,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


async def _create_test_identity(db_session: AsyncSession, email: str) -> EntityId:
    identity_repo = SqlAlchemyIdentityRepository(db_session)
    identity_id = EntityId.new()
    account = UserAccount.register(
        id=identity_id,
        email=EmailAddress(email),
        password_hash="hashed_password",
        created_at=datetime.now(UTC),
    )
    await identity_repo.add(account)
    await db_session.commit()
    return identity_id

@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_update_student_extension_persistence(db_session: AsyncSession):
    # Setup
    unique_email = f"test_{uuid.uuid4()}@example.com"
    identity_id = await _create_test_identity(db_session, unique_email)
    profile_repo = SqlAlchemyProfileRepository(db_session)
    profile_id = EntityId.new()
    
    initial_details = StudentProfileDetails(
        university_name="Original Uni",
        budget_min_naira=10000,
    )
    profile = Profile(
        id=profile_id,
        identity_id=identity_id,
        display_name="Student",
        student_details=initial_details,
    )
    
    await profile_repo.add(profile)
    await db_session.commit()
    
    # Update
    updated_details = StudentProfileDetails(
        university_name="New Uni",
        budget_min_naira=20000,
    )
    profile.update_student_details(updated_details)
    await profile_repo.update_student_extension(profile)
    await db_session.commit()
    
    # Verify
    # We must expire the session to force a reload from the DB
    db_session.expire_all()
    
    retrieved = await profile_repo.get_by_id(profile_id)
    assert retrieved is not None
    assert retrieved.student_details is not None
    assert retrieved.student_details.university_name == "New Uni"
    assert retrieved.student_details.budget_min_naira == 20000
