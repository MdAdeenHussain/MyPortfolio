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
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    admin_columns = {col["name"] for col in inspector.get_columns("admin_users")}
    if "phone_number" not in admin_columns:
        with op.batch_alter_table("admin_users", schema=None) as batch_op:
            batch_op.add_column(sa.Column("phone_number", sa.String(length=30), nullable=True))

    inquiry_columns = {col["name"] for col in inspector.get_columns("plan_inquiries")}
    with op.batch_alter_table("plan_inquiries", schema=None) as batch_op:
        if "maintenance_subscribed" not in inquiry_columns:
            batch_op.add_column(sa.Column("maintenance_subscribed", sa.Boolean(), nullable=True))
        if "maintenance_until" not in inquiry_columns:
            batch_op.add_column(sa.Column("maintenance_until", sa.Date(), nullable=True))
        if "completed_at" not in inquiry_columns:
            batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    inquiry_columns = {col["name"] for col in inspector.get_columns("plan_inquiries")}
    with op.batch_alter_table("plan_inquiries", schema=None) as batch_op:
        if "completed_at" in inquiry_columns:
            batch_op.drop_column("completed_at")
        if "maintenance_until" in inquiry_columns:
            batch_op.drop_column("maintenance_until")
        if "maintenance_subscribed" in inquiry_columns:
            batch_op.drop_column("maintenance_subscribed")

    admin_columns = {col["name"] for col in inspector.get_columns("admin_users")}
    if "phone_number" in admin_columns:
        with op.batch_alter_table("admin_users", schema=None) as batch_op:
            batch_op.drop_column("phone_number")
