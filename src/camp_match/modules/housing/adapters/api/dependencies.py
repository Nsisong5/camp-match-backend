"""Module Housing: dependencies.py"""
"""API dependencies for housing module."""

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
)
from camp_match.modules.profile.adapters.api.dependencies import get_get_current_user_profile
from camp_match.modules.housing.adapters.university_location.university_location_provider import InProcessUniversityLocationProvider
from camp_match.modules.housing.adapters.profile.profile_provider import InProcessProfileProvider
from camp_match.modules.housing.adapters.security.authorization import InProcessAuthorizationService
from camp_match.modules.university_location.application.use_cases.get_campus import GetCampusUseCase
from camp_match.modules.university_location.adapters.persistence.repository import SqlAlchemyCampusRepository

def get_profile_provider(get_profile_uc=Depends(get_get_current_user_profile)) -> InProcessProfileProvider:
    return InProcessProfileProvider(get_profile_uc)

def get_uni_provider(session: Annotated[AsyncSession, Depends(get_db_session)]) -> InProcessUniversityLocationProvider:
    repo = SqlAlchemyCampusRepository(session)
    # GetCampusUseCase implements the GetCampus protocol
    return InProcessUniversityLocationProvider(GetCampusUseCase(repo))

def get_auth_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> InProcessAuthorizationService:
    from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
    from camp_match.modules.security.application.use_cases.authorize_action import AuthorizeActionUseCase
    from camp_match.modules.security.adapters.profile.profile_provider import InProcessProfileProvider as SecurityProfileProvider
    from camp_match.modules.profile.application.use_cases.get_current_user_profile import GetCurrentUserProfileUseCase
    from camp_match.modules.profile.adapters.persistence.repository import SqlAlchemyProfileRepository

    role_repo = SqlAlchemyRoleRepository(session)
    # The security module's profile provider needs its own use case
    profile_repo = SqlAlchemyProfileRepository(session)
    profile_uc = GetCurrentUserProfileUseCase(profile_repo)
    security_profile_provider = SecurityProfileProvider(profile_uc)
    
    auth_uc = AuthorizeActionUseCase(role_repo, security_profile_provider)
    return InProcessAuthorizationService(auth_uc)

def get_property_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> PropertyRepository:
    return SqlAlchemyPropertyRepository(session)
from camp_match.modules.housing.adapters.security.authorization import InProcessAuthorizationService

def get_unit_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UnitRepository:
    return SqlAlchemyUnitRepository(session)

def get_listing_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> ListingRepository:
    return SqlAlchemyListingRepository(session)

from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

# ...

def get_uow(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)

# ...

# Re-export ports for dependency injection in router
from camp_match.modules.housing.application.ports.outbound import (
    PropertyRepository as PropertyRepository,
    UnitRepository as UnitRepository,
    ListingRepository as ListingRepository,
    AuthorizationService as AuthorizationService,
)
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork as UnitOfWork
