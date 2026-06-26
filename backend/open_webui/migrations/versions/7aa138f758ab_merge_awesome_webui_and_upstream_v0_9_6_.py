"""merge awesome-webui and upstream v0.9.6 heads

Revision ID: 7aa138f758ab
Revises: e8f9a1b2c3d4, 461111b60977
Create Date: 2026-06-25 02:51:42.928921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '7aa138f758ab'
down_revision: Union[str, None] = ('e8f9a1b2c3d4', '461111b60977')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
