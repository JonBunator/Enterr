"""v2_5_0

Revision ID: ec08ca6514ef
Revises: db2df5c80c91
Create Date: 2025-12-03 10:24:54.359654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec08ca6514ef'
down_revision: Union[str, None] = 'db2df5c80c91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "action_history",
        sa.Column("custom_failed_details_message", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("action_history", "custom_failed_details_message")
