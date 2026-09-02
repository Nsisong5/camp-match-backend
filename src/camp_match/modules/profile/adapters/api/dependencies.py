from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.identity.adapters.api.dependencies import get_get_identity
from camp_match.modules.profile.adapters.identity.identity_provider import InProcessIdentityProvider
from camp_match.modules.profile.adapters.persistence.repository import SqlAlchemyProfileRepository
from camp_match.modules.profile.application.use_cases.create_profile import CreateProfileUseCase
from camp_match.modules.profile.application.use_cases.get_current_user_profile import (
    GetCurrentUserProfileUseCase,
)
from camp_match.modules.profile.application.use_cases.get_public_profile import (
    GetPublicProfileUseCase,
)
from camp_match.modules.profile.application.use_cases.update_profile import UpdateProfileUseCase
from camp_match.modules.profile.application.use_cases.update_scout_profile import (
    UpdateScoutProfileUseCase,
)
from camp_match.modules.profile.application.use_cases.update_student_profile import (
    UpdateStudentProfileUseCase,
)
from camp_match.platform.clock import get_clock
from camp_match.platform.db.session import get_db_session
from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork
from camp_match.platform.event_bus import get_event_bus
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork


def get_profile_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> SqlAlchemyProfileRepository:
    return SqlAlchemyProfileRepository(session)

def get_uow(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)

def get_identity_provider(get_identity_uc=Depends(get_get_identity)) -> InProcessIdentityProvider:
    return InProcessIdentityProvider(get_identity_uc)

def get_create_profile(
    repo: Annotated[SqlAlchemyProfileRepository, Depends(get_profile_repository)],
    idp: Annotated[InProcessIdentityProvider, Depends(get_identity_provider)],
    event_bus=Depends(get_event_bus),
    clock=Depends(get_clock),
    uow=Depends(get_uow),
) -> CreateProfileUseCase:
    return CreateProfileUseCase(repo, idp, event_bus, clock, uow)

def get_get_current_user_profile(
    repo: Annotated[SqlAlchemyProfileRepository, Depends(get_profile_repository)],
) -> GetCurrentUserProfileUseCase:
    return GetCurrentUserProfileUseCase(repo)

def get_get_public_profile(
    repo: Annotated[SqlAlchemyProfileRepository, Depends(get_profile_repository)],
) -> GetPublicProfileUseCase:
    return GetPublicProfileUseCase(repo)

def get_update_profile(
    repo: Annotated[SqlAlchemyProfileRepository, Depends(get_profile_repository)],
    uow=Depends(get_uow),
) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(repo, uow)

def get_update_student_profile(
    repo: Annotated[SqlAlchemyProfileRepository, Depends(get_profile_repository)],
    uow=Depends(get_uow),
) -> UpdateStudentProfileUseCase:
    return UpdateStudentProfileUseCase(repo, uow)

def get_update_scout_profile(
    repo: Annotated[SqlAlchemyProfileRepository, Depends(get_profile_repository)],
    uow=Depends(get_uow),
) -> UpdateScoutProfileUseCase:
    return UpdateScoutProfileUseCase(repo, uow)
