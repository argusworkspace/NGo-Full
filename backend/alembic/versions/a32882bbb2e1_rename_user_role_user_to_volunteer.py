"""rename user role USER to VOLUNTEER

Revision ID: a32882bbb2e1
Revises: bbed155fc1de
Create Date: 2026-08-29 11:33:47.899193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a32882bbb2e1'
down_revision: Union[str, None] = 'bbed155fc1de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE user_role RENAME VALUE 'USER' TO 'VOLUNTEER'")


def downgrade() -> None:
    op.execute("ALTER TYPE user_role RENAME VALUE 'VOLUNTEER' TO 'USER'")
