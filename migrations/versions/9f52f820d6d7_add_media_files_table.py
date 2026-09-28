"""add media_files table

Revision ID: 9f52f820d6d7
Revises: fed944581254
Create Date: 2026-09-24 20:25:34.603857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f52f820d6d7'
down_revision: Union[str, Sequence[str], None] = 'fed944581254'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('media_files',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('purpose', sa.String(), nullable=False),
    sa.Column('storage_reference', sa.String(), nullable=True),
    sa.Column('content_type', sa.String(), nullable=False),
    sa.Column('size_bytes', sa.BigInteger(), nullable=False),
    sa.Column('original_filename', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('uploaded_by', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("purpose IN ('PROFILE_AVATAR', 'LISTING_PHOTO', 'VERIFICATION_EVIDENCE')", name='check_media_purpose'),
    sa.CheckConstraint("status IN ('UPLOADING', 'AVAILABLE', 'FAILED', 'DELETED')", name='check_media_status'),
    sa.CheckConstraint('size_bytes > 0', name='check_media_size_positive'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_media_files_status'), 'media_files', ['status'], unique=False)
    op.create_index(op.f('ix_media_files_uploaded_by'), 'media_files', ['uploaded_by'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_media_files_uploaded_by'), table_name='media_files')
    op.drop_index(op.f('ix_media_files_status'), table_name='media_files')
    op.drop_table('media_files')
