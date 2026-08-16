from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from camp_match.modules.identity.domain.value_objects import AccountStatus
from camp_match.shared_kernel.domain.identifiers import EntityId

if TYPE_CHECKING:
    from camp_match.modules.identity.domain.value_objects import EmailAddress

IdentityId = EntityId


@dataclass
class UserAccount:
    """Represents a user's security identity and account lifecycle."""

    id: IdentityId
    email: EmailAddress
    password_hash: str
    status: AccountStatus
    created_at: datetime

    @classmethod
    def register(
        cls, id: IdentityId, email: EmailAddress, password_hash: str, created_at: datetime
    ) -> UserAccount:
        """Constructs a brand-new account in the ACTIVE state."""
        return cls(
            id=id,
            email=email,
            password_hash=password_hash,
            status=AccountStatus.ACTIVE,
            created_at=created_at,
        )

    def suspend(self) -> None:
        """Transitions the account to SUSPENDED state."""
        self.status = AccountStatus.SUSPENDED

    def disable(self) -> None:
        """Transitions the account to DISABLED state."""
        self.status = AccountStatus.DISABLED

    def reactivate(self) -> None:
        """Transitions the account back to ACTIVE state."""
        self.status = AccountStatus.ACTIVE

    @property
    def can_authenticate(self) -> bool:
        """Returns True if the account is allowed to authenticate right now."""
        return self.status == AccountStatus.ACTIVE
