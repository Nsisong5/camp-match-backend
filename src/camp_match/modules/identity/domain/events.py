from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from camp_match.shared_kernel.domain.events import DomainEvent

if TYPE_CHECKING:
    from camp_match.modules.identity.domain.value_objects import EmailAddress
    from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """Fired when a new user successfully registers an account."""

    user_id: EntityId
    email: EmailAddress


@dataclass(frozen=True)
class AccountDisabled(DomainEvent):
    """Fired when an account is disabled."""

    user_id: EntityId


@dataclass(frozen=True)
class AccountReactivated(DomainEvent):
    """Fired when a disabled account is reactivated."""

    user_id: EntityId
