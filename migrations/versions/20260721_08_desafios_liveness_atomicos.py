"""desafios de prova de vida persistidos e atomicos

Revision ID: 20260721_08
Revises: 20260720_07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260721_08"
down_revision = "20260720_07"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "liveness_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("session_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=24), nullable=False),
        sa.Column("subject_user_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["subject_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_liveness_challenges_token_hash", "liveness_challenges", ["token_hash"], unique=True)
    op.create_index("ix_liveness_challenges_session_hash", "liveness_challenges", ["session_hash"], unique=False)
    op.create_index("ix_liveness_challenges_purpose", "liveness_challenges", ["purpose"], unique=False)
    op.create_index("ix_liveness_challenges_subject_user_id", "liveness_challenges", ["subject_user_id"], unique=False)
    op.create_index("ix_liveness_challenges_expires_at", "liveness_challenges", ["expires_at"], unique=False)
    op.create_index("ix_liveness_challenges_consumed_at", "liveness_challenges", ["consumed_at"], unique=False)


def downgrade():
    op.drop_index("ix_liveness_challenges_consumed_at", table_name="liveness_challenges")
    op.drop_index("ix_liveness_challenges_expires_at", table_name="liveness_challenges")
    op.drop_index("ix_liveness_challenges_subject_user_id", table_name="liveness_challenges")
    op.drop_index("ix_liveness_challenges_purpose", table_name="liveness_challenges")
    op.drop_index("ix_liveness_challenges_session_hash", table_name="liveness_challenges")
    op.drop_index("ix_liveness_challenges_token_hash", table_name="liveness_challenges")
    op.drop_table("liveness_challenges")
