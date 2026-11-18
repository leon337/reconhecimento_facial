"""Histórico append-only de conferência e propostas de ponto.

Revision ID: 20261118_10
Revises: 20261112_09
"""
from alembic import op
import sqlalchemy as sa

revision = "20261118_10"
down_revision = "20261112_09"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("punch_review_events",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("request_key",sa.String(36),nullable=False,unique=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("company_id",sa.Integer(),sa.ForeignKey("companies.id")),
        sa.Column("worksite_id",sa.Integer(),sa.ForeignKey("worksites.id")),
        sa.Column("day",sa.Date(),nullable=False),
        sa.Column("action",sa.String(32),nullable=False),
        sa.Column("note",sa.Text(),nullable=False),
        sa.Column("point_id",sa.Integer(),sa.ForeignKey("pontos.id")),
        sa.Column("proposed_type",sa.String(10)),
        sa.Column("proposed_time",sa.String(5)),
        sa.Column("actor_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("created_at",sa.DateTime(),nullable=False))
    for col in ("user_id","company_id","worksite_id","day"):
        op.create_index("ix_punch_review_events_"+col,"punch_review_events",[col])


def downgrade():
    for col in ("day","worksite_id","company_id","user_id"):
        op.drop_index("ix_punch_review_events_"+col,table_name="punch_review_events")
    op.drop_table("punch_review_events")
