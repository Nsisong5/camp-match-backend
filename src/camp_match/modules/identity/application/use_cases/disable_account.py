"""Use case for disabling a user account."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.errors import IdentityNotFound
from camp_match.modules.identity.application.ports.inbound import (
    IdentityResponse,
    UpdateStatusRequest,
)
from camp_match.modules.identity.application.ports.outbound import IdentityRepository
from camp_match.modules.identity.domain.events import AccountDisabled
from camp_match.shared_kernel.application.event_bus import EventBus
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.clock import Clock
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()


class DisableAccountUseCase:
    def __init__(
        self,
        repository: IdentityRepository,
        clock: Clock,
        event_bus: EventBus,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._event_bus = event_bus
        self._unit_of_work = unit_of_work

    async def execute(self, request: UpdateStatusRequest) -> IdentityResponse:
        try:
            entity_id = EntityId.from_string(request.identity_id)
        except ValueError as e:
            raise IdentityNotFound(f"Invalid identifier format: {e}") from e

        account = await self._repository.get_by_id(entity_id)
        if account is None:
            raise IdentityNotFound(f"No identity found with ID: {request.identity_id}")

        old_status = account.status

        # Transition status
        account.disable()

        # Only persist and publish if state actually changed
        if account.status != old_status:
            async with self._unit_of_work:
                await self._repository.update(account)
                await self._unit_of_work.commit()

            # Publish event
            event = AccountDisabled(user_id=account.id, occurred_at=self._clock.now())
            await self._event_bus.publish(event)

            logger.info("account_disabled", identity_id=str(account.id))
        else:
            logger.info("account_disable_noop", identity_id=str(account.id))

        return IdentityResponse(
            id=str(account.id),
            email=str(account.email),
            status=account.status.name,
            created_at=account.created_at,
        )
