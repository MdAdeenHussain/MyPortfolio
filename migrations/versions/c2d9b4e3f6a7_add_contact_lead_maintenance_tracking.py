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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    lead_columns = {col["name"] for col in inspector.get_columns("contact_leads")}

    with op.batch_alter_table("contact_leads", schema=None) as batch_op:
        if "maintenance_subscribed" not in lead_columns:
            batch_op.add_column(sa.Column("maintenance_subscribed", sa.Boolean(), nullable=True))
        if "maintenance_until" not in lead_columns:
            batch_op.add_column(sa.Column("maintenance_until", sa.Date(), nullable=True))
        if "completed_at" not in lead_columns:
            batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    lead_columns = {col["name"] for col in inspector.get_columns("contact_leads")}

    with op.batch_alter_table("contact_leads", schema=None) as batch_op:
        if "completed_at" in lead_columns:
            batch_op.drop_column("completed_at")
        if "maintenance_until" in lead_columns:
            batch_op.drop_column("maintenance_until")
        if "maintenance_subscribed" in lead_columns:
            batch_op.drop_column("maintenance_subscribed")
