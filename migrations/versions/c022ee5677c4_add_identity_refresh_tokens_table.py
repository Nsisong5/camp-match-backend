"""add identity_refresh_tokens table

Revision ID: c022ee5677c4
Revises: 1b30121db23f
Create Date: 2026-08-31 20:19:05.733697

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c022ee5677c4'
down_revision: str | Sequence[str] | None = '1b30121db23f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'identity_refresh_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replaced_by_id', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_identity_refresh_tokens_account_id'), 'identity_refresh_tokens', ['account_id'], unique=False)
    op.create_index(op.f('ix_identity_refresh_tokens_token_hash'), 'identity_refresh_tokens', ['token_hash'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_identity_refresh_tokens_token_hash'), table_name='identity_refresh_tokens')
    op.drop_index(op.f('ix_identity_refresh_tokens_account_id'), table_name='identity_refresh_tokens')
    op.drop_table('identity_refresh_tokens')
