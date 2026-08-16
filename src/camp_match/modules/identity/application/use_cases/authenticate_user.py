"""Use case for authenticating a user and issuing tokens."""

from __future__ import annotations

import structlog

from camp_match.modules.identity.application.errors import (
    AccountDisabled,
    AccountSuspended,
    InvalidCredentials,
)
from camp_match.modules.identity.application.ports.inbound import (
    AuthenticationRequest,
    TokenResponse,
)
from camp_match.modules.identity.application.ports.outbound import (
    AuthenticationSessionPort,
    IdentityRepository,
    PasswordHasher,
)
from camp_match.modules.identity.domain.value_objects import AccountStatus, EmailAddress

logger = structlog.get_logger()


class AuthenticateUserUseCase:
    def __init__(
        self,
        repository: IdentityRepository,
        password_hasher: PasswordHasher,
        session_port: AuthenticationSessionPort,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._session_port = session_port

    async def execute(self, request: AuthenticationRequest) -> TokenResponse:
        # Step 1: Normalize email
        try:
            email_vo = EmailAddress(request.email)
        except ValueError:
            logger.warning("login_failed", reason="invalid_email_format")
            raise InvalidCredentials("Invalid credentials.") from None

        # Step 2: Look up account by email
        account = await self._repository.get_by_email(email_vo)

        # Step 3: Handle account not found
        if account is None:
            logger.warning("login_failed", reason="account_not_found", email=str(email_vo))
            raise InvalidCredentials("Invalid credentials.")

        # Step 4: Verify password
        is_valid = self._password_hasher.verify(request.raw_password, account.password_hash)
        if not is_valid:
            logger.warning("login_failed", reason="invalid_password", identity_id=str(account.id))
            raise InvalidCredentials("Invalid credentials.")

        # Step 5: Check account status
        if not account.can_authenticate:
            logger.warning("login_blocked", status=account.status.name, identity_id=str(account.id))
            if account.status == AccountStatus.SUSPENDED:
                raise AccountSuspended("Account is suspended.")
            elif account.status == AccountStatus.DISABLED:
                raise AccountDisabled("Account is disabled.")
            else:
                raise InvalidCredentials("Account cannot authenticate.")

        # Step 6: Issue tokens
        token_pair = await self._session_port.issue_tokens(account.id)

        logger.info("login_succeeded", identity_id=str(account.id))

        return TokenResponse(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type=token_pair.token_type,
            expires_in=token_pair.expires_in,
        )
