from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class EntityId:
    value: UUID

    @classmethod
    def new(cls) -> EntityId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, raw: str) -> EntityId:
        return cls(UUID(raw))

    def __str__(self) -> str:
        return str(self.value)
