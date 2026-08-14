from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol

from camp_match.shared_kernel.domain.events import DomainEvent

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None: ...
