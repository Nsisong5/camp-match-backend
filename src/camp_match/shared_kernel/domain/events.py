from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class DomainEvent:
    event_id: EntityId = field(default_factory=EntityId.new)
    occurred_at: datetime | None = None
