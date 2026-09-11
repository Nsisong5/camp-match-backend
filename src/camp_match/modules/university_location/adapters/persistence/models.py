from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import NUMERIC, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from camp_match.modules.university_location.domain.value_objects import (
    InstitutionStatus,
    InstitutionType,
)
from camp_match.platform.db.base import Base


class UniversityModel(Base):
    __tablename__ = "universities"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    official_name: Mapped[str] = mapped_column(String, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    short_name: Mapped[str | None] = mapped_column(String, nullable=True)
    institution_type: Mapped[str] = mapped_column(
        String,
        CheckConstraint(f"institution_type IN ({', '.join([f"'{t.value}'" for t in InstitutionType])})"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String,
        CheckConstraint(f"status IN ({', '.join([f"'{s.value}'" for s in InstitutionStatus])})"),
        nullable=False,
        default=InstitutionStatus.ACTIVE.value,
    )
    country: Mapped[str] = mapped_column(String, nullable=False, default="Nigeria")
    state_region: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
    
    campuses: Mapped[list["CampusModel"]] = relationship(back_populates="university")


class CampusModel(Base):
    __tablename__ = "campuses"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    university_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("universities.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(NUMERIC(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(NUMERIC(9, 6), nullable=False)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    state_region: Mapped[str | None] = mapped_column(String, nullable=True)
    is_main_campus: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String,
        CheckConstraint(f"status IN ({', '.join([f"'{s.value}'" for s in InstitutionStatus])})"),
        nullable=False,
        default=InstitutionStatus.ACTIVE.value,
    )
    source: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    university: Mapped["UniversityModel"] = relationship(back_populates="campuses")

    __table_args__ = (
        UniqueConstraint("university_id", "normalized_name", name="idx_campus_university_normalized_name"),
        Index(
            "idx_campus_main_per_university",
            "university_id",
            postgresql_where=(is_main_campus == True),
            unique=True,
        ),
    )
