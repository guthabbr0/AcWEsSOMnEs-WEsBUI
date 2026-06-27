"""Add moderation appeals and audit log

Revision ID: c9a2f4e7d610
Revises: b8f6d2a4c901
Create Date: 2026-06-26 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


revision: str = 'c9a2f4e7d610'
down_revision: Union[str, None] = 'b8f6d2a4c901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())

    if 'user_moderation_appeal' not in table_names:
        op.create_table(
            'user_moderation_appeal',
            sa.Column('id', sa.Text(), primary_key=True),
            sa.Column('ban_id', sa.Text(), nullable=False),
            sa.Column('user_id', sa.Text(), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('status', sa.Text(), nullable=False),
            sa.Column('created_at', sa.BigInteger(), nullable=False),
            sa.Column('resolved_at', sa.BigInteger(), nullable=True),
            sa.Column('resolved_by', sa.Text(), nullable=True),
            sa.Column('resolution_note', sa.Text(), nullable=True),
        )

    appeal_indexes = {idx['name'] for idx in inspector.get_indexes('user_moderation_appeal')}
    for name, columns in {
        'ix_user_moderation_appeal_ban_id': ['ban_id'],
        'ix_user_moderation_appeal_user_id': ['user_id'],
        'ix_user_moderation_appeal_status': ['status'],
        'ix_user_moderation_appeal_created_at': ['created_at'],
        'ix_user_moderation_appeal_resolved_at': ['resolved_at'],
    }.items():
        if name not in appeal_indexes:
            op.create_index(name, 'user_moderation_appeal', columns, unique=False)

    if 'user_moderation_audit_log' not in table_names:
        op.create_table(
            'user_moderation_audit_log',
            sa.Column('id', sa.Text(), primary_key=True),
            sa.Column('actor_user_id', sa.Text(), nullable=True),
            sa.Column('target_user_id', sa.Text(), nullable=True),
            sa.Column('action', sa.Text(), nullable=False),
            sa.Column('ban_id', sa.Text(), nullable=True),
            sa.Column('appeal_id', sa.Text(), nullable=True),
            sa.Column('data', open_webui.internal.db.JSONField(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=False),
        )

    audit_indexes = {idx['name'] for idx in inspector.get_indexes('user_moderation_audit_log')}
    for name, columns in {
        'ix_user_moderation_audit_log_actor_user_id': ['actor_user_id'],
        'ix_user_moderation_audit_log_target_user_id': ['target_user_id'],
        'ix_user_moderation_audit_log_action': ['action'],
        'ix_user_moderation_audit_log_ban_id': ['ban_id'],
        'ix_user_moderation_audit_log_appeal_id': ['appeal_id'],
        'ix_user_moderation_audit_log_created_at': ['created_at'],
    }.items():
        if name not in audit_indexes:
            op.create_index(name, 'user_moderation_audit_log', columns, unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())

    if 'user_moderation_audit_log' in table_names:
        audit_indexes = {idx['name'] for idx in inspector.get_indexes('user_moderation_audit_log')}
        for name in [
            'ix_user_moderation_audit_log_created_at',
            'ix_user_moderation_audit_log_appeal_id',
            'ix_user_moderation_audit_log_ban_id',
            'ix_user_moderation_audit_log_action',
            'ix_user_moderation_audit_log_target_user_id',
            'ix_user_moderation_audit_log_actor_user_id',
        ]:
            if name in audit_indexes:
                op.drop_index(name, table_name='user_moderation_audit_log')
        op.drop_table('user_moderation_audit_log')

    if 'user_moderation_appeal' in table_names:
        appeal_indexes = {idx['name'] for idx in inspector.get_indexes('user_moderation_appeal')}
        for name in [
            'ix_user_moderation_appeal_resolved_at',
            'ix_user_moderation_appeal_created_at',
            'ix_user_moderation_appeal_status',
            'ix_user_moderation_appeal_user_id',
            'ix_user_moderation_appeal_ban_id',
        ]:
            if name in appeal_indexes:
                op.drop_index(name, table_name='user_moderation_appeal')
        op.drop_table('user_moderation_appeal')
