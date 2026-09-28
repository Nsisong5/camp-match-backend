from __future__ import annotations

from dataclasses import dataclass
from camp_match.modules.media.domain.value_objects import MediaCategory, MediaPurpose, AccessPolicy


@dataclass(frozen=True, slots=True)
class MediaPurposeRules:
    category: MediaCategory
    access_policy: AccessPolicy
    allowed_content_types: frozenset[str]
    max_size_bytes: int


def rules_for(purpose: MediaPurpose) -> MediaPurposeRules:
    if purpose == MediaPurpose.PROFILE_AVATAR:
        return MediaPurposeRules(
            category=MediaCategory.IMAGE,
            access_policy=AccessPolicy.PUBLIC,
            allowed_content_types=frozenset({"image/jpeg", "image/png", "image/webp"}),
            max_size_bytes=5 * 1024 * 1024,
        )
    elif purpose == MediaPurpose.LISTING_PHOTO:
        return MediaPurposeRules(
            category=MediaCategory.IMAGE,
            access_policy=AccessPolicy.PUBLIC,
            allowed_content_types=frozenset({"image/jpeg", "image/png", "image/webp"}),
            max_size_bytes=5 * 1024 * 1024,
        )
    elif purpose == MediaPurpose.VERIFICATION_EVIDENCE:
        return MediaPurposeRules(
            category=MediaCategory.DOCUMENT,
            access_policy=AccessPolicy.PRIVATE,
            allowed_content_types=frozenset({"image/jpeg", "image/png", "image/webp", "application/pdf"}),
            max_size_bytes=10 * 1024 * 1024,
        )
    raise ValueError(f"Unknown media purpose: {purpose}")
