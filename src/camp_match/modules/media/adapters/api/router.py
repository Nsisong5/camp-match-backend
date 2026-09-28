from __future__ import annotations

from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from camp_match.config.settings import Settings, get_settings
from camp_match.modules.media.adapters.api import dependencies, schemas
from camp_match.modules.media.adapters.persistence.repository import SqlAlchemyMediaRepository
from camp_match.modules.media.adapters.storage.access_token import verify_token
from camp_match.modules.media.application.errors import MediaNotFound
from camp_match.modules.media.application.ports.inbound import GetMediaMetadataRequest
from camp_match.modules.media.application.use_cases.get_media_metadata import GetMediaMetadataUseCase
from camp_match.modules.media.domain.value_objects import AccessPolicy, MediaStatus
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId

router = APIRouter(prefix="/api/v1/media", tags=["media"])


@router.get("/{media_id}", response_model=schemas.MediaMetadataResponseSchema)
async def get_media_metadata(
    media_id: str,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    use_case: Annotated[GetMediaMetadataUseCase, Depends(dependencies.get_get_media_metadata)],
) -> schemas.MediaMetadataResponseSchema:
    try:
        media_uuid = EntityId.from_string(media_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Media not found")

    try:
        result = await use_case.execute(GetMediaMetadataRequest(media_id=media_uuid))
    except MediaNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Enforce ADR-080: Media/File's own public endpoint serves PUBLIC media only
    if result.access_policy == AccessPolicy.PRIVATE:
        raise HTTPException(status_code=403, detail="Private media access denied via generic endpoint")

    return schemas.MediaMetadataResponseSchema(
        media_id=str(result.media_id.value),
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        status=result.status,
        access_policy=result.access_policy,
    )


@router.get("/{media_id}/stream")
async def stream_media(
    media_id: str,
    token: str,
    repo: Annotated[SqlAlchemyMediaRepository, Depends(dependencies.get_media_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    expected_key = f"media/{media_id}"
    verified_key = verify_token(token, settings.media_access_token_secret)
    if not verified_key or verified_key != expected_key:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        media_uuid = EntityId.from_string(media_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Media not found")

    media = await repo.get_by_id(media_uuid)
    if not media or media.status != MediaStatus.AVAILABLE or not media.storage_reference:
        raise HTTPException(status_code=404, detail="Media not found")

    file_path = Path(settings.media_storage_path) / media.storage_reference
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    data = file_path.read_bytes()
    return Response(content=data, media_type=media.content_type)
