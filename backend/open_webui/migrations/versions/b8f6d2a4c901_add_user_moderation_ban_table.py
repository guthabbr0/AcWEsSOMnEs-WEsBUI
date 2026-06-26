"""Add user moderation ban table

Revision ID: b8f6d2a4c901
Revises: 7aa138f758ab
Create Date: 2026-06-25 05:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


revision: str = 'b8f6d2a4c901'
down_revision: Union[str, None] = '7aa138f758ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())

    if 'user_moderation_ban' not in table_names:
        op.create_table(
            'user_moderation_ban',
            sa.Column('id', sa.Text(), primary_key=True),
            sa.Column('user_id', sa.Text(), nullable=False),
            sa.Column('scope', sa.Text(), nullable=False),
            sa.Column('reason', sa.Text(), nullable=False),
            sa.Column('model_ids', open_webui.internal.db.JSONField(), nullable=True),
            sa.Column('channel_ids', open_webui.internal.db.JSONField(), nullable=True),
            sa.Column('starts_at', sa.BigInteger(), nullable=False),
            sa.Column('expires_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=False),
            sa.Column('created_by', sa.Text(), nullable=False),
            sa.Column('revoked_at', sa.BigInteger(), nullable=True),
            sa.Column('revoked_by', sa.Text(), nullable=True),
        )

    index_names = {idx['name'] for idx in inspector.get_indexes('user_moderation_ban')}
    for name, columns in {
        'ix_user_moderation_ban_user_id': ['user_id'],
        'ix_user_moderation_ban_scope': ['scope'],
        'ix_user_moderation_ban_starts_at': ['starts_at'],
        'ix_user_moderation_ban_expires_at': ['expires_at'],
        'ix_user_moderation_ban_revoked_at': ['revoked_at'],
    }.items():
        if name not in index_names:
            op.create_index(name, 'user_moderation_ban', columns, unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())
    if 'user_moderation_ban' not in table_names:
        return

    index_names = {idx['name'] for idx in inspector.get_indexes('user_moderation_ban')}
    for name in [
        'ix_user_moderation_ban_revoked_at',
        'ix_user_moderation_ban_expires_at',
        'ix_user_moderation_ban_starts_at',
        'ix_user_moderation_ban_scope',
        'ix_user_moderation_ban_user_id',
    ]:
        if name in index_names:
            op.drop_index(name, table_name='user_moderation_ban')

    op.drop_table('user_moderation_ban')
