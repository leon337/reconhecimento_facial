"""Segrega e protege os dados biométricos.

Revision ID: 20260719_04
Revises: 20260718_03
Create Date: 2026-07-19
"""

from alembic import op
import sqlalchemy as sa

revision = "20260719_04"
down_revision = "20260718_03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "biometric_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("encrypted_template", sa.Text(), nullable=False),
        sa.Column("image_object_key", sa.String(length=255), nullable=True),
        sa.Column("algorithm_version", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        op.f("ix_biometric_profiles_user_id"),
        "biometric_profiles",
        ["user_id"],
        unique=True,
    )


def downgrade():
    op.drop_index(op.f("ix_biometric_profiles_user_id"), table_name="biometric_profiles")
    op.drop_table("biometric_profiles")
