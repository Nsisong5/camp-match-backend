"""Use case for logging out and revoking session."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.ports.inbound import LogoutRequest
from camp_match.modules.identity.application.ports.outbound import AuthenticationSessionPort

logger = structlog.get_logger()


class LogoutUseCase:
    def __init__(self, session_port: AuthenticationSessionPort) -> None:
        self._session_port = session_port

    async def execute(self, request: LogoutRequest) -> None:
        await self._session_port.revoke(request.refresh_token)

        logger.info("logout_succeeded")
