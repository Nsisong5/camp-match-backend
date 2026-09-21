"""Module Housing: models.py"""
"""Database models for housing module."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    Integer,
    Boolean,
    BigInteger,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from camp_match.platform.db.base import Base


class PropertyModel(Base):
    __tablename__ = "properties"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    provider_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    property_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    campus_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    has_water: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_electricity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_security: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_parking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_generator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_cctv: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'ARCHIVED')", name="check_property_status"),
    )


class UnitModel(Base):
    __tablename__ = "units"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    property_id: Mapped[UUID] = mapped_column(ForeignKey("properties.id"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    occupied_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_furnished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_private_bathroom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_kitchen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("total_capacity > 0", name="check_total_capacity_positive"),
        CheckConstraint("occupied_count >= 0 AND occupied_count <= total_capacity", name="check_occupancy_valid"),
    )


class ListingModel(Base):
    __tablename__ = "listings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    property_id: Mapped[UUID] = mapped_column(ForeignKey("properties.id"), nullable=False, index=True)
    unit_id: Mapped[UUID] = mapped_column(ForeignKey("units.id"), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    price_amount_kobo: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_currency: Mapped[str] = mapped_column(String, nullable=False, default="NGN")
    price_period: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="DRAFT", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("price_amount_kobo >= 0", name="check_price_non_negative"),
        CheckConstraint("price_currency = 'NGN'", name="check_currency_ngn"),
        CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'UNAVAILABLE', 'ARCHIVED')", name="check_listing_status"),
    )


class ListingMediaModel(Base):
    __tablename__ = "listing_media"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    listing_id: Mapped[UUID] = mapped_column(ForeignKey("listings.id"), nullable=False, index=True)
    media_url: Mapped[str] = mapped_column(String, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
