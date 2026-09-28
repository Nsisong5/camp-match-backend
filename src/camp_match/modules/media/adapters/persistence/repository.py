from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from sqlalchemy import select
from camp_match.modules.media.adapters.persistence.models import MediaFileModel
from camp_match.modules.media.domain.entities import MediaFile
from camp_match.modules.media.domain.value_objects import MediaPurpose, MediaStatus
from camp_match.shared_kernel.domain.identifiers import EntityId

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyMediaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, media: MediaFile) -> None:
        model = MediaFileModel(
            id=media.id.value,
            purpose=media.purpose.value,
            storage_reference=media.storage_reference,
            content_type=media.content_type,
            size_bytes=media.size_bytes,
            original_filename=media.original_filename,
            status=media.status.value,
            uploaded_by=media.uploaded_by.value,
            created_at=media.created_at,
            updated_at=media.updated_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, media_id: EntityId) -> MediaFile | None:
        model = await self._session.get(MediaFileModel, media_id.value)
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, media: MediaFile) -> None:
        model = await self._session.get(MediaFileModel, media.id.value)
        if model:
            model.status = media.status.value
            model.storage_reference = media.storage_reference
            model.updated_at = media.updated_at
            await self._session.flush()

    async def find_stuck_uploads(self, older_than: timedelta) -> list[MediaFile]:
        threshold = datetime.now(UTC) - older_than
        stmt = select(MediaFileModel).where(
            MediaFileModel.status == MediaStatus.UPLOADING.value,
            MediaFileModel.created_at <= threshold,
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: MediaFileModel) -> MediaFile:
        return MediaFile(
            id=EntityId(model.id),
            purpose=MediaPurpose(model.purpose),
            content_type=model.content_type,
            size_bytes=model.size_bytes,
            original_filename=model.original_filename,
            uploaded_by=EntityId(model.uploaded_by),
            status=MediaStatus(model.status),
            storage_reference=model.storage_reference,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
