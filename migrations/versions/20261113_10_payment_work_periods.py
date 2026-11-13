"""Conferência de jornadas para preparação futura da folha, sem dados monetários.

Revision ID: 20261113_10
Revises: 20261112_09
"""
from alembic import op
import sqlalchemy as sa

revision = "20261113_10"
down_revision = "20261112_09"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "payment_periods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("worksite_id", sa.Integer(), sa.ForeignKey("worksites.id")),
        sa.Column("scope_key", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("scope_key", name="uq_payment_period_scope"),
        sa.CheckConstraint("start_date <= end_date", name="ck_payment_period_dates"),
    )
    op.create_index("ix_payment_periods_company_id", "payment_periods", ["company_id"])
    op.create_index("ix_payment_periods_worksite_id", "payment_periods", ["worksite_id"])
    op.create_table(
        "payment_work_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("payment_periods.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("worksite_id", sa.Integer(), sa.ForeignKey("worksites.id")),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("entry_time", sa.Time(), nullable=False),
        sa.Column("break_start", sa.Time(), nullable=False),
        sa.Column("break_end", sa.Time(), nullable=False),
        sa.Column("exit_time", sa.Time(), nullable=False),
        sa.Column("worked_minutes", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("period_id", "employee_id", "work_date", name="uq_payment_work_day"),
        sa.CheckConstraint(
            "worked_minutes > 0 AND worked_minutes <= 1440", name="ck_payment_work_minutes"
        ),
    )
    for column in ("period_id", "company_id", "worksite_id", "employee_id"):
        op.create_index(f"ix_payment_work_entries_{column}", "payment_work_entries", [column])


def downgrade():
    for column in ("employee_id", "worksite_id", "company_id", "period_id"):
        op.drop_index(f"ix_payment_work_entries_{column}", table_name="payment_work_entries")
    op.drop_table("payment_work_entries")
    op.drop_index("ix_payment_periods_worksite_id", table_name="payment_periods")
    op.drop_index("ix_payment_periods_company_id", table_name="payment_periods")
    op.drop_table("payment_periods")
