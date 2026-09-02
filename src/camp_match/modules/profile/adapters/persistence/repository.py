from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from camp_match.modules.profile.adapters.persistence.models import (
    ProfileModel,
    ScoutProfileModel,
    StudentProfileModel,
)
from camp_match.modules.profile.application.errors import ProfileAlreadyExists
from camp_match.modules.profile.domain.entities import Profile
from camp_match.modules.profile.domain.value_objects import (
    ProfileType,
    ScoutProfileDetails,
    StudentProfileDetails,
)
from camp_match.shared_kernel.domain.identifiers import EntityId

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

class SqlAlchemyProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, profile: Profile) -> None:
        model = ProfileModel(
            id=str(profile.id.value),
            identity_id=str(profile.identity_id.value),
            display_name=profile.display_name,
            bio=profile.bio,
            phone_number=profile.phone_number,
            avatar_url=profile.avatar_url,
            profile_type=profile.profile_type,
        )
        self._session.add(model)
        
        if profile.profile_type == ProfileType.STUDENT and profile.student_details:
            details = StudentProfileModel(
                profile_id=str(profile.id.value),
                university_name=profile.student_details.university_name,
                department=profile.student_details.department,
                budget_min_naira=profile.student_details.budget_min_naira,
                budget_max_naira=profile.student_details.budget_max_naira,
                preferred_accommodation_type=profile.student_details.preferred_accommodation_type,
                cleanliness_preference=profile.student_details.cleanliness_preference,
                sleep_schedule=profile.student_details.sleep_schedule,
            )
            self._session.add(details)
        elif profile.profile_type == ProfileType.SCOUT and profile.scout_details:
            details = ScoutProfileModel(
                profile_id=str(profile.id.value),
                business_name=profile.scout_details.business_name,
                business_description=profile.scout_details.business_description,
                years_active=profile.scout_details.years_active,
                availability_status=profile.scout_details.availability_status,
            )
            self._session.add(details)

        try:
            await self._session.flush()
        except IntegrityError as e:
            if "profiles_identity_id_key" in str(e):
                raise ProfileAlreadyExists(f"Profile for identity {profile.identity_id} already exists.") from e
            raise

    async def get_by_identity_id(self, identity_id: EntityId) -> Profile | None:
        stmt = select(ProfileModel).where(ProfileModel.identity_id == str(identity_id.value))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return await self._to_domain(model)

    async def get_by_id(self, profile_id: EntityId) -> Profile | None:
        stmt = select(ProfileModel).where(ProfileModel.id == str(profile_id.value))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return await self._to_domain(model)

    async def update_core(self, profile: Profile) -> None:
        stmt = select(ProfileModel).where(ProfileModel.id == str(profile.id.value))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.display_name = profile.display_name
            model.bio = profile.bio
            model.phone_number = profile.phone_number
            model.avatar_url = profile.avatar_url

    async def update_student_extension(self, profile: Profile) -> None:
        stmt = select(StudentProfileModel).where(StudentProfileModel.profile_id == str(profile.id.value))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model and profile.student_details:
            model.university_name = profile.student_details.university_name
            model.department = profile.student_details.department
            model.budget_min_naira = profile.student_details.budget_min_naira
            model.budget_max_naira = profile.student_details.budget_max_naira
            model.preferred_accommodation_type = profile.student_details.preferred_accommodation_type
            model.cleanliness_preference = profile.student_details.cleanliness_preference
            model.sleep_schedule = profile.student_details.sleep_schedule

    async def update_scout_extension(self, profile: Profile) -> None:
        stmt = select(ScoutProfileModel).where(ScoutProfileModel.profile_id == str(profile.id.value))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model and profile.scout_details:
            model.business_name = profile.scout_details.business_name
            model.business_description = profile.scout_details.business_description
            model.years_active = profile.scout_details.years_active
            model.availability_status = profile.scout_details.availability_status

    async def _to_domain(self, model: ProfileModel) -> Profile:
        student_details = None
        scout_details = None

        if model.profile_type == ProfileType.STUDENT:
            stmt = select(StudentProfileModel).where(StudentProfileModel.profile_id == model.id)
            result = await self._session.execute(stmt)
            details_model = result.scalar_one()
            student_details = StudentProfileDetails(
                university_name=details_model.university_name,
                department=details_model.department,
                budget_min_naira=details_model.budget_min_naira,
                budget_max_naira=details_model.budget_max_naira,
                preferred_accommodation_type=details_model.preferred_accommodation_type,
                cleanliness_preference=details_model.cleanliness_preference,
                sleep_schedule=details_model.sleep_schedule,
            )
        elif model.profile_type == ProfileType.SCOUT:
            stmt = select(ScoutProfileModel).where(ScoutProfileModel.profile_id == model.id)
            result = await self._session.execute(stmt)
            details_model = result.scalar_one()
            scout_details = ScoutProfileDetails(
                business_name=details_model.business_name,
                business_description=details_model.business_description,
                years_active=details_model.years_active,
                availability_status=details_model.availability_status,
            )
            
        return Profile(
            id=EntityId(model.id),
            identity_id=EntityId(model.identity_id),
            display_name=model.display_name,
            student_details=student_details,
            scout_details=scout_details,
            bio=model.bio,
            phone_number=model.phone_number,
            avatar_url=model.avatar_url,
        )
