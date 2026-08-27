"""Initial DB Schema with pgvector extension and core tables.

Revision ID: 0001
Revises: 
Create Date: 2026-08-27

"""
from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension exists
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        'citizens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True, unique=True),
        sa.Column('phone_hash', sa.String(64), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_citizens_email', 'citizens', ['email'])

    op.create_table(
        'auth_credentials',
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'uan_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id'), nullable=False),
        sa.Column('uan', sa.String(20), nullable=False, unique=True),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('kyc_status', sa.String(50), server_default='UNVERIFIED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_uan_citizen', 'uan_records', ['citizen_id'])

    op.create_table(
        'employment_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id'), nullable=False),
        sa.Column('uan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('uan_records.id'), nullable=False),
        sa.Column('employer_name', sa.String(255), nullable=False),
        sa.Column('employer_establishment_id', sa.String(100), nullable=True),
        sa.Column('date_of_joining', sa.Date(), nullable=False),
        sa.Column('date_of_exit', sa.Date(), nullable=True),
        sa.Column('exit_reason', sa.String(100), nullable=True),
        sa.Column('basic_wage_history', sa.JSON(), server_default='[]', nullable=False),
        sa.Column('is_data_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('data_source', sa.String(50), server_default='DEMO_SEED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'pf_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employment_history.id'), nullable=False),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id'), nullable=False),
        sa.Column('member_id', sa.String(100), nullable=False),
        sa.Column('account_type', sa.String(20), server_default='EPF', nullable=False),
        sa.Column('status', sa.String(50), server_default='ACTIVE', nullable=False),
        sa.Column('inoperative_since', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'pf_balance_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('pf_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pf_accounts.id'), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('employee_share', sa.Numeric(14, 2), nullable=False),
        sa.Column('employer_share', sa.Numeric(14, 2), nullable=False),
        sa.Column('interest_accrued', sa.Numeric(14, 2), server_default='0', nullable=False),
        sa.Column('total_balance', sa.Numeric(14, 2), nullable=False),
        sa.Column('data_source', sa.String(50), server_default='DEMO_SEED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'rule_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rule_id', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('yaml_definition', sa.JSON(), nullable=False),
        sa.Column('source_reference', sa.Text(), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_by', sa.String(100), server_default='SYSTEM', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'health_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id'), nullable=False),
        sa.Column('pf_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pf_accounts.id'), nullable=True),
        sa.Column('employment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employment_history.id'), nullable=True),
        sa.Column('rule_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rule_versions.id'), nullable=False),
        sa.Column('rule_id', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), server_default='OPEN', nullable=False),
        sa.Column('what_is_wrong', sa.Text(), nullable=False),
        sa.Column('why_it_happened', sa.Text(), nullable=True),
        sa.Column('potential_impact', sa.Text(), nullable=False),
        sa.Column('correction_path', sa.JSON(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id'), nullable=False),
        sa.Column('claim_type', sa.String(50), nullable=False),
        sa.Column('intent_source', sa.String(50), nullable=False),
        sa.Column('raw_intent_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='DRAFT', nullable=False),
        sa.Column('eligibility_result', sa.JSON(), nullable=False),
        sa.Column('calculation_result', sa.JSON(), nullable=True),
        sa.Column('presubmit_result', sa.JSON(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citizens.id'), nullable=False),
        sa.Column('case_type', sa.String(50), nullable=False),
        sa.Column('case_subtype', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), server_default='OPEN', nullable=False),
        sa.Column('claim_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('claims.id'), nullable=True),
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('health_findings.id'), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'case_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(50), nullable=False),
        sa.Column('what_happened', sa.Text(), nullable=False),
        sa.Column('why_it_happened', sa.Text(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('metadata_payload', sa.JSON(), nullable=True),
        sa.Column('previous_status', sa.String(50), nullable=True),
        sa.Column('new_status', sa.String(50), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'audit_log',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address_hash', sa.String(64), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('request_id', sa.String(100), nullable=True),
        sa.Column('outcome', sa.String(50), nullable=False),
        sa.Column('detail', sa.JSON(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('case_events')
    op.drop_table('cases')
    op.drop_table('claims')
    op.drop_table('health_findings')
    op.drop_table('rule_versions')
    op.drop_table('pf_balance_snapshots')
    op.drop_table('pf_accounts')
    op.drop_table('employment_history')
    op.drop_table('uan_records')
    op.drop_table('auth_credentials')
    op.drop_table('citizens')
