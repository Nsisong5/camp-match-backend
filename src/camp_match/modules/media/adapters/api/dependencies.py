from __future__ import annotations

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from camp_match.config.settings import Settings, get_settings
from camp_match.modules.media.adapters.persistence.repository import SqlAlchemyMediaRepository
from camp_match.modules.media.adapters.storage.local_storage_adapter import LocalFileSystemStorageAdapter
from camp_match.modules.media.application.use_cases.get_media_metadata import GetMediaMetadataUseCase
from camp_match.modules.media.application.use_cases.get_authorized_access import GetAuthorizedAccessUseCase
from camp_match.modules.media.application.use_cases.upload_media import UploadMediaUseCase
from camp_match.modules.media.application.use_cases.delete_media import DeleteMediaUseCase
from camp_match.platform.db.session import get_db_session


def get_media_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> SqlAlchemyMediaRepository:
    return SqlAlchemyMediaRepository(session)


def get_storage_adapter(settings: Annotated[Settings, Depends(get_settings)]) -> LocalFileSystemStorageAdapter:
    return LocalFileSystemStorageAdapter(
        storage_path=settings.media_storage_path,
        secret=settings.media_access_token_secret,
        ttl_seconds=settings.media_access_token_ttl_seconds,
    )


def get_get_media_metadata(
    repo: Annotated[SqlAlchemyMediaRepository, Depends(get_media_repository)],
) -> GetMediaMetadataUseCase:
    return GetMediaMetadataUseCase(repo)


def get_get_authorized_access(
    repo: Annotated[SqlAlchemyMediaRepository, Depends(get_media_repository)],
    storage: Annotated[LocalFileSystemStorageAdapter, Depends(get_storage_adapter)],
) -> GetAuthorizedAccessUseCase:
    return GetAuthorizedAccessUseCase(repo, storage)


def get_upload_media(
    repo: Annotated[SqlAlchemyMediaRepository, Depends(get_media_repository)],
    storage: Annotated[LocalFileSystemStorageAdapter, Depends(get_storage_adapter)],
) -> UploadMediaUseCase:
    return UploadMediaUseCase(repo, storage)


def get_delete_media(
    repo: Annotated[SqlAlchemyMediaRepository, Depends(get_media_repository)],
    storage: Annotated[LocalFileSystemStorageAdapter, Depends(get_storage_adapter)],
) -> DeleteMediaUseCase:
    return DeleteMediaUseCase(repo, storage)
