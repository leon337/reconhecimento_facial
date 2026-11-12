"""Novo Funcionário V2: rascunhos e dados complementares criptografados.

Revision ID: 20261112_09
Revises: 20260721_08
"""
from alembic import op
import sqlalchemy as sa

revision = '20261112_09'
down_revision = '20260721_08'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'onboarding_drafts',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('owner_user_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('company_id',sa.Integer(),sa.ForeignKey('companies.id')),
        sa.Column('worksite_id',sa.Integer(),sa.ForeignKey('worksites.id')),
        sa.Column('version',sa.Integer(),nullable=False),
        sa.Column('status',sa.String(20),nullable=False),
        sa.Column('encrypted_payload',sa.Text(),nullable=False),
        sa.Column('employee_id',sa.Integer(),sa.ForeignKey('employees.id'),unique=True),
        sa.Column('created_at',sa.DateTime(),nullable=False),
        sa.Column('updated_at',sa.DateTime(),nullable=False),
    )
    op.create_index('ix_onboarding_drafts_owner_user_id','onboarding_drafts',['owner_user_id'])
    op.create_index('ix_onboarding_drafts_company_id','onboarding_drafts',['company_id'])
    op.create_index('ix_onboarding_drafts_worksite_id','onboarding_drafts',['worksite_id'])
    op.create_table(
        'employee_onboarding',
        sa.Column('employee_id',sa.Integer(),sa.ForeignKey('employees.id',ondelete='CASCADE'),primary_key=True),
        sa.Column('company_id',sa.Integer(),sa.ForeignKey('companies.id')),
        sa.Column('worksite_id',sa.Integer(),sa.ForeignKey('worksites.id')),
        sa.Column('encrypted_payload',sa.Text(),nullable=False),
        sa.Column('version',sa.Integer(),nullable=False),
        sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('created_at',sa.DateTime(),nullable=False),
    )
    op.create_index('ix_employee_onboarding_company_id','employee_onboarding',['company_id'])
    op.create_index('ix_employee_onboarding_worksite_id','employee_onboarding',['worksite_id'])


def downgrade():
    op.drop_index('ix_employee_onboarding_worksite_id',table_name='employee_onboarding')
    op.drop_index('ix_employee_onboarding_company_id',table_name='employee_onboarding')
    op.drop_table('employee_onboarding')
    op.drop_index('ix_onboarding_drafts_worksite_id',table_name='onboarding_drafts')
    op.drop_index('ix_onboarding_drafts_company_id',table_name='onboarding_drafts')
    op.drop_index('ix_onboarding_drafts_owner_user_id',table_name='onboarding_drafts')
    op.drop_table('onboarding_drafts')
