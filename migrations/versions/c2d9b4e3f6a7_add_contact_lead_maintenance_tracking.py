"""add contact lead maintenance tracking

Revision ID: c2d9b4e3f6a7
Revises: a0f8b7c2d4e1
Create Date: 2026-03-03 23:58:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c2d9b4e3f6a7"
down_revision = "a0f8b7c2d4e1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("contact_leads", schema=None) as batch_op:
        batch_op.add_column(sa.Column("maintenance_subscribed", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("maintenance_until", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("contact_leads", schema=None) as batch_op:
        batch_op.drop_column("completed_at")
        batch_op.drop_column("maintenance_until")
        batch_op.drop_column("maintenance_subscribed")
