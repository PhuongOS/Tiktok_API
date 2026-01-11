"""create workspaces tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE plantier AS ENUM ('free', 'pro', 'enterprise')")
    op.execute("CREATE TYPE workspacerole AS ENUM ('owner', 'admin', 'operator', 'viewer')")
    
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('plan_tier', sa.Enum('free', 'pro', 'enterprise', name='plantier'), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'])
    )
    
    # Create workspace_members table
    op.create_table(
        'workspace_members',
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('owner', 'admin', 'operator', 'viewer', name='workspacerole'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('workspace_id', 'user_id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    op.drop_table('workspace_members')
    op.drop_table('workspaces')
    op.execute('DROP TYPE workspacerole')
    op.execute('DROP TYPE plantier')

