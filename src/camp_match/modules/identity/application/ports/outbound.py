"""Outbound ports for the Identity module, defining repository, hashing, and token interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from camp_match.modules.identity.domain.entities import UserAccount
    from camp_match.modules.identity.domain.value_objects import EmailAddress
    from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class IdentityRepository(Protocol):
    async def add(self, account: UserAccount) -> None:
        """Persists a new user account."""
        ...

    async def get_by_email(self, email: EmailAddress) -> UserAccount | None:
        """Retrieves a user account by email address."""
        ...

    async def get_by_id(self, identity_id: EntityId) -> UserAccount | None:
        """Retrieves a user account by its entity ID."""
        ...

    async def update(self, account: UserAccount) -> None:
        """Persists state updates to an existing account."""
        ...


class PasswordHasher(Protocol):
    def hash(self, raw_password: str) -> str:
        """Hashes a raw password into a secure string."""
        ...

    def verify(self, raw_password: str, encoded_hash: str) -> bool:
        """Verifies a raw password against an encoded hash."""
        ...


class AuthenticationSessionPort(Protocol):
    async def issue_tokens(self, identity_id: EntityId) -> TokenPair:
        """Issues a new token pair for the given identity."""
        ...

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Refreshes a token pair using a valid, unrevoked refresh token."""
        ...

    async def revoke(self, refresh_token: str) -> None:
        """
        Revokes a refresh token, rendering it invalid for future refreshes.
        Must be idempotent.
        """
        ...

    async def decode_access_token(self, access_token: str) -> EntityId:
        """
        Decodes an access token and returns the encapsulated EntityId.
        Raises InvalidCredentials if invalid or expired.
        """
        ...
