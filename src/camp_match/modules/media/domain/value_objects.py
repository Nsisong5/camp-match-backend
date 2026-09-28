from __future__ import annotations

from enum import Enum


class MediaPurpose(Enum):
    PROFILE_AVATAR = "PROFILE_AVATAR"
    LISTING_PHOTO = "LISTING_PHOTO"
    VERIFICATION_EVIDENCE = "VERIFICATION_EVIDENCE"


class MediaCategory(Enum):
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"


class MediaStatus(Enum):
    UPLOADING = "UPLOADING"
    AVAILABLE = "AVAILABLE"
    FAILED = "FAILED"
    DELETED = "DELETED"


class AccessPolicy(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
