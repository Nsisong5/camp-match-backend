from typing import Annotated

from fastapi import Depends, Header, HTTPException
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
from camp_match.platform.clock import SystemClock
from camp_match.platform.db.session import get_db_session
from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork
from camp_match.platform.in_memory_event_bus import InMemoryEventBus
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.identifiers import EntityId

# Singletons for platform components
_clock = SystemClock()
_event_bus = InMemoryEventBus()

def get_clock() -> SystemClock:
    return _clock

def get_event_bus() -> InMemoryEventBus:
    return _event_bus

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

def get_refresh_session(auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)]) -> RefreshSessionUseCase:
    return RefreshSessionUseCase(session_port=auth)

def get_logout(auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)]) -> LogoutUseCase:
    return LogoutUseCase(session_port=auth)

def get_get_identity(repo: Annotated[SqlAlchemyIdentityRepository, Depends(get_identity_repository)]) -> GetIdentityByIdUseCase:
    return GetIdentityByIdUseCase(repository=repo)

async def get_current_identity_id(
    authorization: Annotated[str | None, Header()] = None,
    auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)] = ...,  # type: ignore
) -> EntityId:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    return await auth.decode_access_token(token)
