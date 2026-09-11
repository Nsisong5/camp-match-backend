from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from camp_match.modules.identity.adapters.api import schemas
from camp_match.modules.identity.adapters.api.dependencies import (
    get_authenticate_user,
    get_disable_account,
    get_get_identity,
    get_logout,
    get_reactivate_account,
    get_refresh_session,
    get_register_account,
)
from camp_match.modules.identity.application.ports.inbound import (
    AuthenticationRequest,
    IdentityQueryRequest,
    LogoutRequest,
    RefreshRequest,
    RegistrationRequest,
    UpdateStatusRequest,
)
from camp_match.modules.identity.application.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
)
from camp_match.modules.identity.application.use_cases.disable_account import DisableAccountUseCase
from camp_match.modules.identity.application.use_cases.get_identity import GetIdentityByIdUseCase
from camp_match.modules.identity.application.use_cases.logout import LogoutUseCase
from camp_match.modules.identity.application.use_cases.reactivate_account import (
    ReactivateAccountUseCase,
)
from camp_match.modules.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from camp_match.modules.identity.application.use_cases.register_account import (
    RegisterAccountUseCase,
)
from camp_match.modules.security.adapters.api.dependencies import require_permission
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegisterResponse,
)
async def register(
    reg_request: schemas.RegisterRequest,
    use_case: Annotated[RegisterAccountUseCase, Depends(get_register_account)],
) -> schemas.RegisterResponse:
    registration_request = RegistrationRequest(
        email=reg_request.email, raw_password=reg_request.password
    )
    identity = await use_case.execute(registration_request)
    return schemas.RegisterResponse(id=identity.id, email=identity.email)

@router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=schemas.LoginResponse
)
async def login(
    login_request: schemas.LoginRequest,
    use_case: Annotated[AuthenticateUserUseCase, Depends(get_authenticate_user)],
) -> schemas.LoginResponse:
    auth_request = AuthenticationRequest(
        email=login_request.email, raw_password=login_request.password
    )
    tokens = await use_case.execute(auth_request)
    return schemas.LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )

@router.get("/me", status_code=status.HTTP_200_OK, response_model=schemas.MeResponse)
async def me(
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    use_case: Annotated[GetIdentityByIdUseCase, Depends(get_get_identity)],
) -> schemas.MeResponse:
    query_request = IdentityQueryRequest(identity_id=str(identity_id))
    identity = await use_case.execute(query_request)
    return schemas.MeResponse(id=identity.id, email=identity.email, status=identity.status)

@router.post(
    "/refresh", status_code=status.HTTP_200_OK, response_model=schemas.RefreshResponse
)
async def refresh(
    refresh_data: Annotated[schemas.RefreshRequest, Body(...)],
    use_case: Annotated[RefreshSessionUseCase, Depends(get_refresh_session)],
) -> schemas.RefreshResponse:
    refresh_request = RefreshRequest(refresh_token=refresh_data.refresh_token)
    tokens = await use_case.execute(refresh_request)
    return schemas.RefreshResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    logout_data: Annotated[schemas.RefreshRequest, Body(...)],
    use_case: Annotated[LogoutUseCase, Depends(get_logout)],
) -> None:
    logout_request = LogoutRequest(refresh_token=logout_data.refresh_token)
    await use_case.execute(logout_request)

@router.post("/{identity_id}/disable", response_model=schemas.MeResponse)
async def disable_account(
    identity_id: str,
    use_case: Annotated[DisableAccountUseCase, Depends(get_disable_account)],
    _ = require_permission(Permission.ADMIN_USERS_MANAGE)
) -> schemas.MeResponse:
    request = UpdateStatusRequest(identity_id=identity_id)
    identity = await use_case.execute(request)
    return schemas.MeResponse(id=identity.id, email=identity.email, status=identity.status)

@router.post("/{identity_id}/reactivate", response_model=schemas.MeResponse)
async def reactivate_account(
    identity_id: str,
    use_case: Annotated[ReactivateAccountUseCase, Depends(get_reactivate_account)],
    _ = require_permission(Permission.ADMIN_USERS_MANAGE)
) -> schemas.MeResponse:
    request = UpdateStatusRequest(identity_id=identity_id)
    identity = await use_case.execute(request)
    return schemas.MeResponse(id=identity.id, email=identity.email, status=identity.status)
