"""Test fakes for Identity module outbound ports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from camp_match.modules.identity.application.errors import IdentityAlreadyExists, InvalidCredentials
from camp_match.modules.identity.application.ports.outbound import TokenPair
from camp_match.shared_kernel.domain.identifiers import EntityId

if TYPE_CHECKING:
    from camp_match.modules.identity.domain.entities import UserAccount
    from camp_match.modules.identity.domain.value_objects import EmailAddress


class FakeIdentityRepository:
    def __init__(self) -> None:
        self.accounts: dict[EntityId, UserAccount] = {}

    async def add(self, account: UserAccount) -> None:
        for acc in self.accounts.values():
            if acc.email == account.email:
                raise IdentityAlreadyExists("Email is already registered.")
        self.accounts[account.id] = account

    async def get_by_email(self, email: EmailAddress) -> UserAccount | None:
        for acc in self.accounts.values():
            if acc.email == email:
                return acc
        return None

    async def get_by_id(self, identity_id: EntityId) -> UserAccount | None:
        return self.accounts.get(identity_id)

    async def update(self, account: UserAccount) -> None:
        self.accounts[account.id] = account


class FakePasswordHasher:
    def hash(self, raw_password: str) -> str:
        return f"hashed_{raw_password}"

    def verify(self, raw_password: str, encoded_hash: str) -> bool:
        return f"hashed_{raw_password}" == encoded_hash


class FakeAuthenticationSessionPort:
    def __init__(self) -> None:
        self.revoked_tokens: set[str] = set()

    async def issue_tokens(self, identity_id: EntityId) -> TokenPair:
        return TokenPair(
            access_token=f"access_{identity_id}",
            refresh_token=f"refresh_{identity_id}",
            token_type="bearer",
            expires_in=3600,
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        if refresh_token in self.revoked_tokens or not refresh_token.startswith("refresh_"):
            raise InvalidCredentials("Invalid or revoked refresh token.")
        identity_id_str = refresh_token.replace("refresh_", "")
        identity_id = EntityId.from_string(identity_id_str)
        return await self.issue_tokens(identity_id)

    async def revoke(self, refresh_token: str) -> None:
        self.revoked_tokens.add(refresh_token)

    async def decode_access_token(self, access_token: str) -> EntityId:
        if not access_token.startswith("access_"):
            raise InvalidCredentials("Invalid access token.")
        identity_id_str = access_token.replace("access_", "")
        return EntityId.from_string(identity_id_str)


class FakeEventBus:
    def __init__(self) -> None:
        self.events: list[object] = []

    async def publish(self, event: object) -> None:
        self.events.append(event)


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self) -> FakeUnitOfWork:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass
