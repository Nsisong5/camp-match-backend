"""Use case for retrieving identity details."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.errors import IdentityNotFound
from camp_match.modules.identity.application.ports.inbound import (
    IdentityQueryRequest,
    IdentityResponse,
)
from camp_match.modules.identity.application.ports.outbound import IdentityRepository
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()


class GetIdentityByIdUseCase:
    def __init__(self, repository: IdentityRepository) -> None:
        self._repository = repository

    async def execute(self, request: IdentityQueryRequest) -> IdentityResponse:
        try:
            entity_id = EntityId.from_string(request.identity_id)
        except ValueError as e:
            raise IdentityNotFound(f"Invalid identifier format: {e}") from e

        account = await self._repository.get_by_id(entity_id)
        if account is None:
            raise IdentityNotFound(f"No identity found with ID: {request.identity_id}")

        return IdentityResponse(
            id=str(account.id),
            email=str(account.email),
            status=account.status.name,
            created_at=account.created_at,
        )
