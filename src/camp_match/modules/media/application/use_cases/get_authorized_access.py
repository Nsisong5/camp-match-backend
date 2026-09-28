from __future__ import annotations

from camp_match.modules.media.application.errors import MediaNotAvailable, MediaNotFound
from camp_match.modules.media.application.ports.inbound import GetAuthorizedAccessRequest
from camp_match.modules.media.application.ports.outbound import AccessGrant, MediaRepository, StoragePort
from camp_match.modules.media.domain.value_objects import MediaStatus


class GetAuthorizedAccessUseCase:
    """
    Use case to obtain a signed time-limited access grant for an available media file.
    
    NOTE: This use case does not check access_policy itself (ADR-080). That boundary
    is enforced by who calls this port: Media/File's own public HTTP layer only calls
    this for PUBLIC media, whereas private media is accessed exclusively via in-process
    calls from owning modules after performing business-level authorization.
    """
    def __init__(self, repo: MediaRepository, storage: StoragePort) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(self, request: GetAuthorizedAccessRequest) -> AccessGrant:
        media = await self._repo.get_by_id(request.media_id)
        if not media or media.status == MediaStatus.DELETED:
            raise MediaNotFound(f"Media file {request.media_id} not found")

        if media.status != MediaStatus.AVAILABLE or not media.storage_reference:
            raise MediaNotAvailable(f"Media file {request.media_id} is not available (status: {media.status.value})")

        return self._storage.issue_access_token(media.storage_reference)
