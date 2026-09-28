from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from camp_match.modules.media.domain.value_objects import (
    AccessPolicy,
    MediaPurpose,
    MediaStatus,
)
from camp_match.modules.media.application.ports.outbound import AccessGrant
from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True, slots=True)
class UploadMediaRequest:
    purpose: MediaPurpose
    data: bytes
    content_type: str
    original_filename: str
    uploaded_by: EntityId


@dataclass(frozen=True, slots=True)
class UploadMediaResponse:
    media_id: EntityId
    status: MediaStatus


class UploadMedia(Protocol):
    async def execute(self, request: UploadMediaRequest) -> UploadMediaResponse:
        ...


@dataclass(frozen=True, slots=True)
class GetMediaMetadataRequest:
    media_id: EntityId


@dataclass(frozen=True, slots=True)
class MediaMetadataResponse:
    media_id: EntityId
    content_type: str
    size_bytes: int
    status: MediaStatus
    access_policy: AccessPolicy


class GetMediaMetadata(Protocol):
    async def execute(self, request: GetMediaMetadataRequest) -> MediaMetadataResponse:
        ...


@dataclass(frozen=True, slots=True)
class GetAuthorizedAccessRequest:
    media_id: EntityId


class GetAuthorizedAccess(Protocol):
    async def execute(self, request: GetAuthorizedAccessRequest) -> AccessGrant:
        ...


@dataclass(frozen=True, slots=True)
class DeleteMediaRequest:
    media_id: EntityId


class DeleteMedia(Protocol):
    async def execute(self, request: DeleteMediaRequest) -> None:
        ...
