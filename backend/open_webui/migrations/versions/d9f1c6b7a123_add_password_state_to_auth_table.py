"""add password state to auth table

Revision ID: d9f1c6b7a123
Revises: b2c3d4e5f6a7
Create Date: 2026-03-26 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd9f1c6b7a123'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    auth_cols = {c['name'] for c in inspector.get_columns('auth')}

    if 'password_change_required' not in auth_cols:
        op.add_column(
            'auth',
            sa.Column(
                'password_change_required',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )

    if 'password_login_enabled' not in auth_cols:
        op.add_column(
            'auth',
            sa.Column(
                'password_login_enabled',
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    auth_cols = {c['name'] for c in inspector.get_columns('auth')}

    if 'password_login_enabled' in auth_cols:
        op.drop_column('auth', 'password_login_enabled')

    if 'password_change_required' in auth_cols:
        op.drop_column('auth', 'password_change_required')
