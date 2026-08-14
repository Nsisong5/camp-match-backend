from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable

import structlog

from camp_match.shared_kernel.domain.events import DomainEvent

logger = structlog.get_logger()
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        logger.info(
            "domain_event_published",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
        )
        for handler in self._handlers[type(event)]:
            await handler(event)
