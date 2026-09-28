from __future__ import annotations

import logging
from camp_match.modules.media.application.ports.inbound import DeleteMediaRequest
from camp_match.modules.media.application.ports.outbound import MediaRepository, StoragePort
from camp_match.modules.media.domain.value_objects import MediaStatus

logger = logging.getLogger(__name__)


class DeleteMediaUseCase:
    def __init__(self, repo: MediaRepository, storage: StoragePort) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(self, request: DeleteMediaRequest) -> None:
        media = await self._repo.get_by_id(request.media_id)
        if not media or media.status == MediaStatus.DELETED:
            return  # Idempotent: already gone or never existed

        if media.storage_reference:
            self._storage.delete(media.storage_reference)

        media.delete()
        await self._repo.update(media)
        logger.info("media_deleted media_id=%s", request.media_id.value)
