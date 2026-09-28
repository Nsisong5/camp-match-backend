from pydantic import BaseModel
from camp_match.modules.media.domain.value_objects import MediaStatus, AccessPolicy


class MediaMetadataResponseSchema(BaseModel):
    media_id: str
    content_type: str
    size_bytes: int
    status: MediaStatus
    access_policy: AccessPolicy
