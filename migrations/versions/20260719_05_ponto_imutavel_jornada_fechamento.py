"""ponto imutavel jornada fechamento

Revision ID: 20260719_05
Revises: 20260719_04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260719_05"
down_revision = "20260719_04"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "work_schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("worksite_id", sa.Integer(), sa.ForeignKey("worksites.id"), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("daily_minutes", sa.Integer(), nullable=False),
        sa.Column("break_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "attendance_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("worksite_id", sa.Integer(), sa.ForeignKey("worksites.id"), nullable=True),
        sa.Column("schedule_id", sa.Integer(), sa.ForeignKey("work_schedules.id"), nullable=True),
        sa.Column("event_type", sa.String(length=30), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="biometric"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("employee_id", "occurred_at", "event_type", name="uq_attendance_event_identity"),
    )
    op.create_table(
        "attendance_adjustments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attendance_event_id", sa.Integer(), sa.ForeignKey("attendance_events.id"), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("replacement_event_type", sa.String(length=30), nullable=True),
        sa.Column("replacement_occurred_at", sa.DateTime(), nullable=True),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "attendance_closures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("worked_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overtime_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("closed_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("employee_id", "period_start", "period_end", name="uq_attendance_closure_period"),
    )


def downgrade():
    op.drop_table("attendance_closures")
    op.drop_table("attendance_adjustments")
    op.drop_table("attendance_events")
    op.drop_table("work_schedules")
