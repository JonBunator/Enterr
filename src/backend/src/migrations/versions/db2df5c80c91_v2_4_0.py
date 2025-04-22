"""v2.4.0

Revision ID: db2df5c80c91
Revises: In v2.4.0 notification support was added. This added a notification table.
Create Date: 2025-04-14 19:44:26.767656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db2df5c80c91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notification',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('apprise_token', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('trigger', sa.String(), nullable=False),
    sa.Column('user', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('notification')
