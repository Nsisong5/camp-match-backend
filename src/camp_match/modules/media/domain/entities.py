from __future__ import annotations

from datetime import UTC, datetime
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.modules.media.domain.value_objects import (
    MediaPurpose,
    MediaCategory,
    MediaStatus,
    AccessPolicy,
)
from camp_match.modules.media.domain.policy import rules_for


class MediaFile:
    def __init__(
        self,
        id: EntityId,
        purpose: MediaPurpose,
        content_type: str,
        size_bytes: int,
        original_filename: str,
        uploaded_by: EntityId,
        status: MediaStatus = MediaStatus.UPLOADING,
        storage_reference: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if size_bytes <= 0:
            raise ValueError("size_bytes must be positive")
        if not original_filename.strip():
            raise ValueError("original_filename cannot be empty")

        if status == MediaStatus.AVAILABLE and not storage_reference:
            raise ValueError("storage_reference is required when status is AVAILABLE")
        if status != MediaStatus.AVAILABLE and storage_reference is not None:
            raise ValueError("storage_reference can only be set when status is AVAILABLE")

        self._id = id
        self._purpose = purpose
        self._content_type = content_type
        self._size_bytes = size_bytes
        self._original_filename = original_filename.strip()
        self._uploaded_by = uploaded_by
        self._status = status
        self._storage_reference = storage_reference
        
        now = datetime.now(UTC)
        self._created_at = created_at or now
        self._updated_at = updated_at or now

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def purpose(self) -> MediaPurpose:
        return self._purpose

    @property
    def category(self) -> MediaCategory:
        return rules_for(self._purpose).category

    @property
    def access_policy(self) -> AccessPolicy:
        return rules_for(self._purpose).access_policy

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

    @property
    def original_filename(self) -> str:
        return self._original_filename

    @property
    def uploaded_by(self) -> EntityId:
        return self._uploaded_by

    @property
    def status(self) -> MediaStatus:
        return self._status

    @property
    def storage_reference(self) -> str | None:
        return self._storage_reference

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def mark_available(self, storage_reference: str) -> None:
        if not storage_reference.strip():
            raise ValueError("storage_reference cannot be empty")
        if self._status == MediaStatus.DELETED:
            raise ValueError("Cannot make deleted media available")
        self._status = MediaStatus.AVAILABLE
        self._storage_reference = storage_reference.strip()
        self._updated_at = datetime.now(UTC)

    def mark_failed(self) -> None:
        if self._status == MediaStatus.DELETED:
            raise ValueError("Cannot fail deleted media")
        self._status = MediaStatus.FAILED
        self._storage_reference = None
        self._updated_at = datetime.now(UTC)

    def delete(self) -> None:
        self._status = MediaStatus.DELETED
        self._storage_reference = None
        self._updated_at = datetime.now(UTC)
