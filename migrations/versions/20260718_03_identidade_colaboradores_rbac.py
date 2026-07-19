"""Separa cadastro funcional da conta e adiciona RBAC.

Revision ID: 20260718_03
Revises: 20260718_02
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_03"
down_revision = "20260718_02"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("worksite_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("registration", sa.String(length=50), nullable=True),
        sa.Column("job_title", sa.String(length=80), nullable=True),
        sa.Column("schedule", sa.String(length=120), nullable=True),
        sa.Column("address", sa.String(length=200), nullable=True),
        sa.Column("pass_type", sa.String(length=50), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["worksite_id"], ["worksites.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id", "registration", name="uq_employees_company_registration"
        ),
    )
    op.create_index("ix_employees_company_id", "employees", ["company_id"])
    op.create_index("ix_employees_worksite_id", "employees", ["worksite_id"])

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("access_role", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("employee_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_users_access_role", ["access_role"])
        batch_op.create_index("ix_users_employee_id", ["employee_id"], unique=True)
        batch_op.create_foreign_key(
            "fk_users_employee_id_employees", "employees", ["employee_id"], ["id"]
        )

    # Compatibilidade: administradores legados passam a ter papel explícito.
    op.execute("UPDATE users SET access_role = 'admin' WHERE role = 'admin'")


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("fk_users_employee_id_employees", type_="foreignkey")
        batch_op.drop_index("ix_users_employee_id")
        batch_op.drop_index("ix_users_access_role")
        batch_op.drop_column("employee_id")
        batch_op.drop_column("access_role")

    op.drop_index("ix_employees_worksite_id", table_name="employees")
    op.drop_index("ix_employees_company_id", table_name="employees")
    op.drop_table("employees")
