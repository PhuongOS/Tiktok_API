"""create rules tables

Revision ID: 001
Revises: 
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE rulestatus AS ENUM ('active', 'inactive', 'draft')")
    op.execute("CREATE TYPE comparisonoperator AS ENUM ('==', '!=', '>', '>=', '<', '<=', 'contains', 'not_contains', 'in', 'not_in')")
    op.execute("CREATE TYPE actiontype AS ENUM ('device_control', 'notification', 'webhook', 'log')")
    op.execute("CREATE TYPE executionstatus AS ENUM ('success', 'failed', 'partial')")
    
    # Create rules table
    op.create_table(
        'rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'draft', name='rulestatus'), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('livestream_id', sa.String()),
        sa.Column('logic_operator', sa.String(), server_default='AND'),
        sa.Column('execution_count', sa.Integer(), server_default='0'),
        sa.Column('last_executed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for rules
    op.create_index('ix_rules_workspace_id', 'rules', ['workspace_id'])
    op.create_index('ix_rules_status', 'rules', ['status'])
    op.create_index('ix_rules_event_type', 'rules', ['event_type'])
    op.create_index('ix_rules_livestream_id', 'rules', ['livestream_id'])
    
    # Create rule_conditions table
    op.create_table(
        'rule_conditions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('rule_id', sa.String(), nullable=False),
        sa.Column('field', sa.String(), nullable=False),
        sa.Column('operator', postgresql.ENUM('==', '!=', '>', '>=', '<', '<=', 'contains', 'not_contains', 'in', 'not_in', name='comparisonoperator'), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('order', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create rule_actions table
    op.create_table(
        'rule_actions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('rule_id', sa.String(), nullable=False),
        sa.Column('action_type', postgresql.ENUM('device_control', 'notification', 'webhook', 'log', name='actiontype'), nullable=False),
        sa.Column('config', postgresql.JSON(), nullable=False),
        sa.Column('order', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create rule_executions table
    op.create_table(
        'rule_executions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('rule_id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('event_data', postgresql.JSON(), nullable=False),
        sa.Column('status', postgresql.ENUM('success', 'failed', 'partial', name='executionstatus'), nullable=False),
        sa.Column('actions_executed', sa.Integer(), server_default='0'),
        sa.Column('actions_failed', sa.Integer(), server_default='0'),
        sa.Column('error_message', sa.String()),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('duration_ms', sa.Integer()),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('rule_executions')
    op.drop_table('rule_actions')
    op.drop_table('rule_conditions')
    op.drop_table('rules')
    
    op.execute('DROP TYPE executionstatus')
    op.execute('DROP TYPE actiontype')
    op.execute('DROP TYPE comparisonoperator')
    op.execute('DROP TYPE rulestatus')
