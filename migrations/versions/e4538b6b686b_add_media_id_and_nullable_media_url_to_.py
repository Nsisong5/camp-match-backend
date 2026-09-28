"""add media_id and nullable media_url to listing_media

Revision ID: e4538b6b686b
Revises: 78298898a964
Create Date: 2026-09-25 11:08:24.434983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4538b6b686b'
down_revision: Union[str, Sequence[str], None] = '78298898a964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('listing_media', sa.Column('media_id', sa.Uuid(), nullable=True))
    op.alter_column('listing_media', 'media_url',
               existing_type=sa.VARCHAR(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('listing_media', 'media_url',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('listing_media', 'media_id')
