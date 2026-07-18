"""Schema inicial de usuários e registros de ponto.

Revision ID: 20260718_01
Revises:
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("registration", sa.String(length=50), nullable=True),
        sa.Column("role", sa.String(length=80), nullable=True),
        sa.Column("schedule", sa.String(length=120), nullable=True),
        sa.Column("address", sa.String(length=200), nullable=True),
        sa.Column("pass_type", sa.String(length=50), nullable=True),
        sa.Column("face_encoding", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "pontos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("pontos")
    op.drop_table("users")
