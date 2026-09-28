from __future__ import annotations

import logging
from camp_match.modules.media.application.errors import (
    MediaTooLarge,
    MediaUploadFailed,
    UnsupportedMediaType,
)
from camp_match.modules.media.application.ports.inbound import (
    UploadMediaRequest,
    UploadMediaResponse,
)
from camp_match.modules.media.application.ports.outbound import (
    MediaRepository,
    StoragePort,
)
from camp_match.modules.media.domain.entities import MediaFile
from camp_match.modules.media.domain.policy import rules_for
from camp_match.modules.media.domain.value_objects import MediaStatus
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = logging.getLogger(__name__)


def sniff_content_type(data: bytes) -> str | None:
    if data.startswith(b"\xFF\xD8\xFF"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"%PDF"):
        return "application/pdf"
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    return None


class UploadMediaUseCase:
    def __init__(self, repo: MediaRepository, storage: StoragePort) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(self, request: UploadMediaRequest) -> UploadMediaResponse:
        rules = rules_for(request.purpose)

        # 1. Sniff actual content type from bytes
        sniffed_type = sniff_content_type(request.data)
        if not sniffed_type or sniffed_type not in rules.allowed_content_types:
            raise UnsupportedMediaType(
                f"File signature does not match allowed content types for purpose {request.purpose.value}"
            )

        # 2. Validate size
        if len(request.data) > rules.max_size_bytes:
            raise MediaTooLarge(
                f"File size {len(request.data)} bytes exceeds maximum allowed {rules.max_size_bytes} bytes"
            )

        # 3. Construct and persist media file in UPLOADING state first
        media_id = EntityId.new()
        media = MediaFile(
            id=media_id,
            purpose=request.purpose,
            content_type=sniffed_type,
            size_bytes=len(request.data),
            original_filename=request.original_filename,
            uploaded_by=request.uploaded_by,
            status=MediaStatus.UPLOADING,
        )
        await self._repo.add(media)

        storage_key = f"media/{media_id.value}"

        try:
            self._storage.store(storage_key, request.data, sniffed_type)
            media.mark_available(storage_key)
            await self._repo.update(media)
            logger.info(
                "media_uploaded media_id=%s purpose=%s size=%s",
                media_id.value,
                request.purpose.value,
                len(request.data),
            )
            return UploadMediaResponse(media_id=media_id, status=media.status)
        except Exception as e:
            media.mark_failed()
            await self._repo.update(media)
            logger.warning(
                "media_upload_failed media_id=%s purpose=%s error=%s",
                media_id.value,
                request.purpose.value,
                str(e),
            )
            raise MediaUploadFailed(f"Failed to store media file: {e}") from e
