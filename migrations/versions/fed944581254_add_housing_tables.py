"""add housing tables

Revision ID: fed944581254
Revises: 91857cb3d5d7
Create Date: 2026-09-14 11:34:22.379623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fed944581254'
down_revision: Union[str, Sequence[str], None] = '91857cb3d5d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # properties
    op.create_table(
        'properties',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('provider_id', sa.UUID(), nullable=False),
        sa.Column('property_type', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('latitude', sa.Numeric(9, 6), nullable=False),
        sa.Column('longitude', sa.Numeric(9, 6), nullable=False),
        sa.Column('campus_id', sa.UUID(), nullable=True),
        sa.Column('has_water', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_electricity', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_security', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_parking', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_generator', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_cctv', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_wifi', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('status', sa.String(), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('ACTIVE', 'ARCHIVED')", name="check_property_status")
    )
    op.create_index('ix_properties_provider_id', 'properties', ['provider_id'], unique=False)
    op.create_index('ix_properties_campus_id', 'properties', ['campus_id'], unique=False)

    # units
    op.create_table(
        'units',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('total_capacity', sa.Integer(), nullable=False),
        sa.Column('occupied_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_furnished', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_private_bathroom', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_kitchen', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.CheckConstraint("total_capacity > 0", name="check_total_capacity_positive"),
        sa.CheckConstraint("occupied_count >= 0 AND occupied_count <= total_capacity", name="check_occupancy_valid")
    )
    op.create_index('ix_units_property_id', 'units', ['property_id'], unique=False)

    # listings
    op.create_table(
        'listings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('unit_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price_amount_kobo', sa.BigInteger(), nullable=False),
        sa.Column('price_currency', sa.String(), server_default='NGN', nullable=False),
        sa.Column('price_period', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='DRAFT', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id']),
        sa.UniqueConstraint('unit_id'),
        sa.CheckConstraint("price_amount_kobo >= 0", name="check_price_non_negative"),
        sa.CheckConstraint("price_currency = 'NGN'", name="check_currency_ngn"),
        sa.CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'UNAVAILABLE', 'ARCHIVED')", name="check_listing_status")
    )
    op.create_index('ix_listings_property_id', 'listings', ['property_id'], unique=False)
    op.create_index('ix_listings_status', 'listings', ['status'], unique=False)

    # listing_media
    op.create_table(
        'listing_media',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('listing_id', sa.UUID(), nullable=False),
        sa.Column('media_url', sa.String(), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'])
    )
    op.create_index('ix_listing_media_listing_id', 'listing_media', ['listing_id'], unique=False)


def downgrade() -> None:
    op.drop_table('listing_media')
    op.drop_table('listings')
    op.drop_table('units')
    op.drop_table('properties')
