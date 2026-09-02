from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.identity.adapters.persistence.repository import SqlAlchemyIdentityRepository
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import EmailAddress
from camp_match.modules.profile.adapters.persistence.repository import SqlAlchemyProfileRepository
from camp_match.modules.profile.application.errors import ProfileAlreadyExists
from camp_match.modules.profile.domain.entities import Profile
from camp_match.modules.profile.domain.value_objects import (
    AccommodationTypePreference,
    CleanlinessPreference,
    ProfileType,
    ScoutAvailabilityStatus,
    ScoutProfileDetails,
    SleepSchedule,
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
async def test_repository_add_and_get_student(db_session: AsyncSession):
    identity_id = await _create_test_identity(db_session, "student@example.com")
    profile_repo = SqlAlchemyProfileRepository(db_session)

    profile_id = EntityId.new()
    student_details = StudentProfileDetails(
        university_name="University of Ibadan",
        department="Computer Science",
        budget_min_naira=50000,
        budget_max_naira=150000,
        preferred_accommodation_type=AccommodationTypePreference.SELF_CONTAINED,
        cleanliness_preference=CleanlinessPreference.VERY_TIDY,
        sleep_schedule=SleepSchedule.EARLY_BIRD,
    )
    profile = Profile(
        id=profile_id,
        identity_id=identity_id,
        display_name="Student Name",
        student_details=student_details,
        bio="Hello, I am a student.",
        phone_number="+2348011112222",
        avatar_url="http://example.com/avatar.png",
    )

    await profile_repo.add(profile)
    await db_session.commit()

    # Get by ID
    retrieved_by_id = await profile_repo.get_by_id(profile_id)
    assert retrieved_by_id is not None
    assert retrieved_by_id.id == profile_id
    assert retrieved_by_id.identity_id == identity_id
    assert retrieved_by_id.display_name == "Student Name"
    assert retrieved_by_id.profile_type == ProfileType.STUDENT
    assert retrieved_by_id.bio == "Hello, I am a student."
    assert retrieved_by_id.phone_number == "+2348011112222"
    assert retrieved_by_id.avatar_url == "http://example.com/avatar.png"
    
    assert retrieved_by_id.student_details is not None
    assert retrieved_by_id.student_details.university_name == "University of Ibadan"
    assert retrieved_by_id.student_details.department == "Computer Science"
    assert retrieved_by_id.student_details.budget_min_naira == 50000
    assert retrieved_by_id.student_details.budget_max_naira == 150000
    assert retrieved_by_id.student_details.preferred_accommodation_type == AccommodationTypePreference.SELF_CONTAINED
    assert retrieved_by_id.student_details.cleanliness_preference == CleanlinessPreference.VERY_TIDY
    assert retrieved_by_id.student_details.sleep_schedule == SleepSchedule.EARLY_BIRD
    assert retrieved_by_id.scout_details is None

    # Get by identity ID
    retrieved_by_identity = await profile_repo.get_by_identity_id(identity_id)
    assert retrieved_by_identity is not None
    assert retrieved_by_identity.id == profile_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_add_and_get_scout(db_session: AsyncSession):
    identity_id = await _create_test_identity(db_session, "scout@example.com")
    profile_repo = SqlAlchemyProfileRepository(db_session)

    profile_id = EntityId.new()
    scout_details = ScoutProfileDetails(
        business_name="Camp Match Agents",
        business_description="We find the best housing for you.",
        years_active=5,
        availability_status=ScoutAvailabilityStatus.ACTIVE,
    )
    profile = Profile(
        id=profile_id,
        identity_id=identity_id,
        display_name="Scout Name",
        scout_details=scout_details,
        bio="Hello, I am a scout.",
        phone_number="+2348022223333",
        avatar_url="http://example.com/scout.png",
    )

    await profile_repo.add(profile)
    await db_session.commit()

    retrieved = await profile_repo.get_by_id(profile_id)
    assert retrieved is not None
    assert retrieved.id == profile_id
    assert retrieved.profile_type == ProfileType.SCOUT
    assert retrieved.scout_details is not None
    assert retrieved.scout_details.business_name == "Camp Match Agents"
    assert retrieved.scout_details.business_description == "We find the best housing for you."
    assert retrieved.scout_details.years_active == 5
    assert retrieved.scout_details.availability_status == ScoutAvailabilityStatus.ACTIVE
    assert retrieved.student_details is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_get_nonexistent(db_session: AsyncSession):
    profile_repo = SqlAlchemyProfileRepository(db_session)
    assert await profile_repo.get_by_id(EntityId.new()) is None
    assert await profile_repo.get_by_identity_id(EntityId.new()) is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_add_duplicate_identity_raises(db_session: AsyncSession):
    identity_id = await _create_test_identity(db_session, "duplicate@example.com")
    profile_repo = SqlAlchemyProfileRepository(db_session)

    # First profile
    p1 = Profile(
        id=EntityId.new(),
        identity_id=identity_id,
        display_name="First Profile",
        student_details=StudentProfileDetails(university_name="Uni 1"),
    )
    await profile_repo.add(p1)
    await db_session.commit()

    # Second profile with same identity_id
    p2 = Profile(
        id=EntityId.new(),
        identity_id=identity_id,
        display_name="Second Profile",
        student_details=StudentProfileDetails(university_name="Uni 2"),
    )
    with pytest.raises(ProfileAlreadyExists):
        await profile_repo.add(p2)
        await db_session.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_update_core(db_session: AsyncSession):
    identity_id = await _create_test_identity(db_session, "update_core@example.com")
    profile_repo = SqlAlchemyProfileRepository(db_session)

    profile_id = EntityId.new()
    profile = Profile(
        id=profile_id,
        identity_id=identity_id,
        display_name="Original Name",
        student_details=StudentProfileDetails(university_name="Original Uni"),
        bio="Original Bio",
        phone_number="123",
        avatar_url="original.png",
    )
    await profile_repo.add(profile)
    await db_session.commit()

    # Update core
    profile.update_core(
        display_name="Updated Name",
        bio="Updated Bio",
        phone_number="456",
        avatar_url="updated.png",
    )
    await profile_repo.update_core(profile)
    await db_session.commit()

    retrieved = await profile_repo.get_by_id(profile_id)
    assert retrieved is not None
    assert retrieved.display_name == "Updated Name"
    assert retrieved.bio == "Updated Bio"
    assert retrieved.phone_number == "456"
    assert retrieved.avatar_url == "updated.png"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_update_student_extension(db_session: AsyncSession):
    identity_id = await _create_test_identity(db_session, "update_student@example.com")
    profile_repo = SqlAlchemyProfileRepository(db_session)

    profile_id = EntityId.new()
    profile = Profile(
        id=profile_id,
        identity_id=identity_id,
        display_name="Student",
        student_details=StudentProfileDetails(university_name="Original Uni", department="Original Dept"),
    )
    await profile_repo.add(profile)
    await db_session.commit()

    # Update student details
    new_details = StudentProfileDetails(
        university_name="New Uni",
        department="New Dept",
        budget_min_naira=60000,
        budget_max_naira=120000,
        preferred_accommodation_type=AccommodationTypePreference.HOSTEL,
        cleanliness_preference=CleanlinessPreference.MODERATE,
        sleep_schedule=SleepSchedule.NIGHT_OWL,
    )
    profile.update_student_details(new_details)
    await profile_repo.update_student_extension(profile)
    await db_session.commit()

    retrieved = await profile_repo.get_by_id(profile_id)
    assert retrieved is not None
    assert retrieved.student_details is not None
    assert retrieved.student_details.university_name == "New Uni"
    assert retrieved.student_details.department == "New Dept"
    assert retrieved.student_details.budget_min_naira == 60000
    assert retrieved.student_details.budget_max_naira == 120000
    assert retrieved.student_details.preferred_accommodation_type == AccommodationTypePreference.HOSTEL
    assert retrieved.student_details.cleanliness_preference == CleanlinessPreference.MODERATE
    assert retrieved.student_details.sleep_schedule == SleepSchedule.NIGHT_OWL


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_update_scout_extension(db_session: AsyncSession):
    identity_id = await _create_test_identity(db_session, "update_scout@example.com")
    profile_repo = SqlAlchemyProfileRepository(db_session)

    profile_id = EntityId.new()
    profile = Profile(
        id=profile_id,
        identity_id=identity_id,
        display_name="Scout",
        scout_details=ScoutProfileDetails(business_name="Original Business", years_active=1),
    )
    await profile_repo.add(profile)
    await db_session.commit()

    # Update scout details
    new_details = ScoutProfileDetails(
        business_name="New Business",
        business_description="New Description",
        years_active=3,
        availability_status=ScoutAvailabilityStatus.PAUSED,
    )
    profile.update_scout_details(new_details)
    await profile_repo.update_scout_extension(profile)
    await db_session.commit()

    retrieved = await profile_repo.get_by_id(profile_id)
    assert retrieved is not None
    assert retrieved.scout_details is not None
    assert retrieved.scout_details.business_name == "New Business"
    assert retrieved.scout_details.business_description == "New Description"
    assert retrieved.scout_details.years_active == 3
    assert retrieved.scout_details.availability_status == ScoutAvailabilityStatus.PAUSED
