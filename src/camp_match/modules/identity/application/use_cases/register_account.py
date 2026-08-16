"""Use case for registering a new user account."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.errors import (
    IdentityAlreadyExists,
    InvalidAuthenticationRequest,
)
from camp_match.modules.identity.application.ports.inbound import (
    RegistrationRequest,
    RegistrationResponse,
)
from camp_match.modules.identity.application.ports.outbound import (
    IdentityRepository,
    PasswordHasher,
)
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.events import UserRegistered
from camp_match.modules.identity.domain.value_objects import EmailAddress
from camp_match.shared_kernel.application.event_bus import EventBus
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.clock import Clock
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()


class RegisterAccountUseCase:
    def __init__(
        self,
        repository: IdentityRepository,
        password_hasher: PasswordHasher,
        clock: Clock,
        event_bus: EventBus,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._clock = clock
        self._event_bus = event_bus
        self._unit_of_work = unit_of_work

    async def execute(self, request: RegistrationRequest) -> RegistrationResponse:
        try:
            email_vo = EmailAddress(request.email)
        except ValueError as e:
            raise InvalidAuthenticationRequest(str(e)) from e

        # Check existing account
        existing = await self._repository.get_by_email(email_vo)
        if existing is not None:
            logger.info("registration_rejected_duplicate", email=str(email_vo))
            raise IdentityAlreadyExists("Email is already registered.")

        # Hash password and create account
        hashed_password = self._password_hasher.hash(request.raw_password)
        account_id = EntityId.new()
        now = self._clock.now()

        account = UserAccount.register(
            id=account_id,
            email=email_vo,
            password_hash=hashed_password,
            created_at=now,
        )

        # Persist within a unit of work
        async with self._unit_of_work:
            try:
                await self._repository.add(account)
                await self._unit_of_work.commit()
            except IdentityAlreadyExists as e:
                # Handle unique constraint race condition
                logger.info("registration_rejected_duplicate", email=str(email_vo))
                raise e

        # Publish UserRegistered event
        event = UserRegistered(user_id=account_id, email=email_vo, occurred_at=now)
        await self._event_bus.publish(event)

        logger.info("registration_succeeded", identity_id=str(account_id), email=str(email_vo))

        return RegistrationResponse(
            id=str(account_id),
            email=str(email_vo),
            status=account.status.name,
            created_at=account.created_at,
        )
