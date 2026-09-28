from __future__ import annotations

from camp_match.modules.media.application.errors import MediaNotFound
from camp_match.modules.media.application.ports.inbound import (
    GetMediaMetadataRequest,
    MediaMetadataResponse,
)
from camp_match.modules.media.application.ports.outbound import MediaRepository
from camp_match.modules.media.domain.value_objects import MediaStatus


class GetMediaMetadataUseCase:
    def __init__(self, repo: MediaRepository) -> None:
        self._repo = repo

    async def execute(self, request: GetMediaMetadataRequest) -> MediaMetadataResponse:
        media = await self._repo.get_by_id(request.media_id)
        if not media or media.status == MediaStatus.DELETED:
            raise MediaNotFound(f"Media file {request.media_id} not found")

        return MediaMetadataResponse(
            media_id=media.id,
            content_type=media.content_type,
            size_bytes=media.size_bytes,
            status=media.status,
            access_policy=media.access_policy,
        )
