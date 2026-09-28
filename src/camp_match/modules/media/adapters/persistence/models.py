from __future__ import annotations

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from camp_match.platform.db.base import Base


class MediaFileModel(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True)
    purpose = Column(String, nullable=False)
    storage_reference = Column(String, nullable=True)
    content_type = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    original_filename = Column(String, nullable=False)
    status = Column(String, nullable=False, default="UPLOADING", index=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "purpose IN ('PROFILE_AVATAR', 'LISTING_PHOTO', 'VERIFICATION_EVIDENCE')",
            name="check_media_purpose",
        ),
        CheckConstraint("size_bytes > 0", name="check_media_size_positive"),
        CheckConstraint(
            "status IN ('UPLOADING', 'AVAILABLE', 'FAILED', 'DELETED')",
            name="check_media_status",
        ),
    )
