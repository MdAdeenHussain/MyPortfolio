"""add admin credentials and inquiry tracking fields

Revision ID: a0f8b7c2d4e1
Revises: 98fe61bdc8c5
Create Date: 2026-03-03 23:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0f8b7c2d4e1"
down_revision = "98fe61bdc8c5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("admin_users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("phone_number", sa.String(length=30), nullable=True))

    with op.batch_alter_table("plan_inquiries", schema=None) as batch_op:
        batch_op.add_column(sa.Column("maintenance_subscribed", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("maintenance_until", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("plan_inquiries", schema=None) as batch_op:
        batch_op.drop_column("completed_at")
        batch_op.drop_column("maintenance_until")
        batch_op.drop_column("maintenance_subscribed")

    with op.batch_alter_table("admin_users", schema=None) as batch_op:
        batch_op.drop_column("phone_number")
