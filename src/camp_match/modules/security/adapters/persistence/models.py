from __future__ import annotations

from sqlalchemy import Column, String, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from camp_match.platform.db.base import Base

class SecurityUserRoleModel(Base):
    __tablename__ = "security_user_roles"
    __table_args__ = (
        UniqueConstraint("identity_id", "role", name="_identity_role_uc"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True)
    identity_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
