"""Use case for logging out and revoking session."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.ports.inbound import LogoutRequest
from camp_match.modules.identity.application.ports.outbound import AuthenticationSessionPort
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

logger = structlog.get_logger()


class LogoutUseCase:
    def __init__(self, session_port: AuthenticationSessionPort, uow: UnitOfWork) -> None:
        self._session_port = session_port
        self._uow = uow

    async def execute(self, request: LogoutRequest) -> None:
        async with self._uow:
            await self._session_port.revoke(request.refresh_token)
            await self._uow.commit()

        logger.info("logout_succeeded")
