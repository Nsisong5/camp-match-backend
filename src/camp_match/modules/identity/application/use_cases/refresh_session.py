"""Use case for refreshing an existing session."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.ports.inbound import (
    RefreshRequest,
    TokenResponse,
)
from camp_match.modules.identity.application.ports.outbound import AuthenticationSessionPort
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

logger = structlog.get_logger()


class RefreshSessionUseCase:
    def __init__(self, session_port: AuthenticationSessionPort, uow: UnitOfWork) -> None:
        self._session_port = session_port
        self._uow = uow

    async def execute(self, request: RefreshRequest) -> TokenResponse:
        async with self._uow:
            token_pair = await self._session_port.refresh(request.refresh_token)
            await self._uow.commit()

        logger.info("refresh_succeeded")

        return TokenResponse(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type=token_pair.token_type,
            expires_in=token_pair.expires_in,
        )
