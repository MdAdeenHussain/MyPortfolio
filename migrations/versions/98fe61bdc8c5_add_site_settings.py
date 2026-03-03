"""add site settings

Revision ID: 98fe61bdc8c5
Revises: 33f47b0d9d6d
Create Date: 2026-03-03 20:34:17.869824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98fe61bdc8c5'
down_revision = '33f47b0d9d6d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("instagram_url", sa.String(length=255), nullable=True),
        sa.Column("x_url", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=255), nullable=True),
        sa.Column("facebook_url", sa.String(length=255), nullable=True),
        sa.Column("whatsapp_number", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("site_settings")
