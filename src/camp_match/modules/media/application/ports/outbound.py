from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from camp_match.modules.media.domain.entities import MediaFile
from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True, slots=True)
class AccessGrant:
    token: str
    expires_at: datetime


class StoragePort(Protocol):
    def store(self, key: str, data: bytes, content_type: str) -> None:
        ...

    def delete(self, key: str) -> None:
        ...

    def exists(self, key: str) -> bool:
        ...

    def issue_access_token(self, key: str) -> AccessGrant:
        ...


class MediaRepository(Protocol):
    async def add(self, media: MediaFile) -> None:
        ...

    async def get_by_id(self, media_id: EntityId) -> MediaFile | None:
        ...

    async def update(self, media: MediaFile) -> None:
        ...

    async def find_stuck_uploads(self, older_than: timedelta) -> list[MediaFile]:
        ...
