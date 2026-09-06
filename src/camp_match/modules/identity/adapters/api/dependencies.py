from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.config.settings import Settings, get_settings
from camp_match.modules.identity.adapters.persistence.repository import SqlAlchemyIdentityRepository
from camp_match.modules.identity.adapters.security.jwt_session import (
    JwtAuthenticationSessionAdapter,
)
from camp_match.modules.identity.adapters.security.password_hasher import ScryptPasswordHasher
from camp_match.modules.identity.application.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
)
from camp_match.modules.identity.application.use_cases.get_identity import GetIdentityByIdUseCase
from camp_match.modules.identity.application.use_cases.logout import LogoutUseCase
from camp_match.modules.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from camp_match.modules.identity.application.use_cases.register_account import (
    RegisterAccountUseCase,
)
from camp_match.modules.identity.application.use_cases.disable_account import DisableAccountUseCase
from camp_match.modules.identity.application.use_cases.reactivate_account import ReactivateAccountUseCase
from camp_match.platform.clock import SystemClock, get_clock
from camp_match.platform.db.session import get_db_session
from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork
from camp_match.platform.event_bus import InMemoryEventBus, get_event_bus
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

# Singletons for platform components

def get_uow(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)

def get_identity_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> SqlAlchemyIdentityRepository:
    return SqlAlchemyIdentityRepository(session)

def get_password_hasher() -> ScryptPasswordHasher:
    return ScryptPasswordHasher()

def get_auth_session(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> JwtAuthenticationSessionAdapter:
    return JwtAuthenticationSessionAdapter(session, settings)

def get_register_account(
    repo: Annotated[SqlAlchemyIdentityRepository, Depends(get_identity_repository)],
    hasher: Annotated[ScryptPasswordHasher, Depends(get_password_hasher)],
    clock: Annotated[SystemClock, Depends(get_clock)],
    event_bus: Annotated[InMemoryEventBus, Depends(get_event_bus)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> RegisterAccountUseCase:
    return RegisterAccountUseCase(
        repository=repo,
        password_hasher=hasher,
        clock=clock,
        event_bus=event_bus,
        unit_of_work=uow
    )

def get_authenticate_user(
    repo: Annotated[SqlAlchemyIdentityRepository, Depends(get_identity_repository)],
    hasher: Annotated[ScryptPasswordHasher, Depends(get_password_hasher)],
    auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)],
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        repository=repo,
        password_hasher=hasher,
        session_port=auth
    )

def get_refresh_session(
    auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> RefreshSessionUseCase:
    return RefreshSessionUseCase(session_port=auth, uow=uow)

def get_logout(
    auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> LogoutUseCase:
    return LogoutUseCase(session_port=auth, uow=uow)

def get_get_identity(repo: Annotated[SqlAlchemyIdentityRepository, Depends(get_identity_repository)]) -> GetIdentityByIdUseCase:
    return GetIdentityByIdUseCase(repository=repo)

def get_disable_account(
    repo: Annotated[SqlAlchemyIdentityRepository, Depends(get_identity_repository)],
    clock: Annotated[SystemClock, Depends(get_clock)],
    event_bus: Annotated[InMemoryEventBus, Depends(get_event_bus)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> DisableAccountUseCase:
    return DisableAccountUseCase(
        repository=repo,
        clock=clock,
        event_bus=event_bus,
        unit_of_work=uow
    )

def get_reactivate_account(
    repo: Annotated[SqlAlchemyIdentityRepository, Depends(get_identity_repository)],
    clock: Annotated[SystemClock, Depends(get_clock)],
    event_bus: Annotated[InMemoryEventBus, Depends(get_event_bus)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> ReactivateAccountUseCase:
    return ReactivateAccountUseCase(
        repository=repo,
        clock=clock,
        event_bus=event_bus,
        unit_of_work=uow
    )
