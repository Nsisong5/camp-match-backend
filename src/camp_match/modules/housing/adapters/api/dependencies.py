from __future__ import annotations

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from camp_match.platform.db.session import get_db_session
from camp_match.modules.housing.adapters.persistence.repository import (
    SqlAlchemyPropertyRepository,
    SqlAlchemyUnitRepository,
    SqlAlchemyListingRepository,
)
from camp_match.modules.housing.application.ports.outbound import (
    PropertyRepository,
    UnitRepository,
    ListingRepository,
    AuthorizationService,
)
from camp_match.modules.university_location.adapters.persistence.repository import SqlAlchemyUniversityRepository
from camp_match.modules.housing.adapters.university_location.university_location_provider import InProcessUniversityLocationProvider
from camp_match.modules.profile.adapters.persistence.repository import SqlAlchemyProfileRepository
from camp_match.modules.profile.application.use_cases.get_current_user_profile import GetCurrentUserProfileUseCase
from camp_match.modules.housing.adapters.profile.profile_provider import InProcessProfileProvider
from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.modules.security.application.use_cases.authorize_action import AuthorizeActionUseCase
from camp_match.modules.housing.adapters.security.authorization import InProcessAuthorizationService
from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork


def get_university_location_provider(session: Annotated[AsyncSession, Depends(get_db_session)]) -> InProcessUniversityLocationProvider:
    repo = SqlAlchemyUniversityRepository(session)
    return InProcessUniversityLocationProvider(repo)


def get_profile_provider(session: Annotated[AsyncSession, Depends(get_db_session)]) -> InProcessProfileProvider:
    profile_repo = SqlAlchemyProfileRepository(session)
    profile_uc = GetCurrentUserProfileUseCase(profile_repo)
    return InProcessProfileProvider(profile_uc)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    profile_provider: Annotated[InProcessProfileProvider, Depends(get_profile_provider)],
) -> InProcessAuthorizationService:
    role_repo = SqlAlchemyRoleRepository(session)
    auth_uc = AuthorizeActionUseCase(role_repo, profile_provider)
    return InProcessAuthorizationService(auth_uc)


def get_property_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> PropertyRepository:
    return SqlAlchemyPropertyRepository(session)


def get_unit_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UnitRepository:
    return SqlAlchemyUnitRepository(session)


def get_listing_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> ListingRepository:
    return SqlAlchemyListingRepository(session)


def get_uow(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)
