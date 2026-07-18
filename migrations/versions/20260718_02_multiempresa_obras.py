"""Adiciona empresas, obras e isolamento organizacional.

Revision ID: 20260718_02
Revises: 20260718_01
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa


revision = "20260718_02"
down_revision = "20260718_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_companies_slug"), "companies", ["slug"], unique=True)

    op.create_table(
        "worksites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "name", name="uq_worksites_company_name"),
    )
    op.create_index(op.f("ix_worksites_company_id"), "worksites", ["company_id"], unique=False)

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("company_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("worksite_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_users_company_id", "companies", ["company_id"], ["id"])
        batch_op.create_foreign_key("fk_users_worksite_id", "worksites", ["worksite_id"], ["id"])
        batch_op.create_index("ix_users_company_id", ["company_id"], unique=False)
        batch_op.create_index("ix_users_worksite_id", ["worksite_id"], unique=False)

    with op.batch_alter_table("pontos") as batch_op:
        batch_op.add_column(sa.Column("company_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("worksite_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_pontos_company_id", "companies", ["company_id"], ["id"])
        batch_op.create_foreign_key("fk_pontos_worksite_id", "worksites", ["worksite_id"], ["id"])
        batch_op.create_index("ix_pontos_company_id", ["company_id"], unique=False)
        batch_op.create_index("ix_pontos_worksite_id", ["worksite_id"], unique=False)


def downgrade():
    with op.batch_alter_table("pontos") as batch_op:
        batch_op.drop_index("ix_pontos_worksite_id")
        batch_op.drop_index("ix_pontos_company_id")
        batch_op.drop_constraint("fk_pontos_worksite_id", type_="foreignkey")
        batch_op.drop_constraint("fk_pontos_company_id", type_="foreignkey")
        batch_op.drop_column("worksite_id")
        batch_op.drop_column("company_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_worksite_id")
        batch_op.drop_index("ix_users_company_id")
        batch_op.drop_constraint("fk_users_worksite_id", type_="foreignkey")
        batch_op.drop_constraint("fk_users_company_id", type_="foreignkey")
        batch_op.drop_column("worksite_id")
        batch_op.drop_column("company_id")

    op.drop_index(op.f("ix_worksites_company_id"), table_name="worksites")
    op.drop_table("worksites")
    op.drop_index(op.f("ix_companies_slug"), table_name="companies")
    op.drop_table("companies")
