"""Add client support

Revision ID: 002
Revises: 001
Create Date: 2026-01-10 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create clients table (using String instead of Enum to avoid complexity)
    op.create_table(
        'clients',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('client_type', sa.String()),
        sa.Column('os', sa.String()),
        sa.Column('version', sa.String()),
        sa.Column('status', sa.String(), nullable=False, server_default='offline'),
        sa.Column('last_seen', sa.DateTime()),
        sa.Column('ip_address', sa.String()),
        sa.Column('client_metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_clients_workspace', 'clients', ['workspace_id'])
    op.create_index('idx_clients_status', 'clients', ['status'])
    
    # Add columns to devices table
    op.add_column('devices', sa.Column('client_id', sa.String()))
    op.add_column('devices', sa.Column('connection_type', sa.String()))
    op.add_column('devices', sa.Column('connection_params', sa.JSON()))
    
    # Create foreign key
    op.create_foreign_key(
        'fk_devices_client_id',
        'devices', 'clients',
        ['client_id'], ['id']
    )
    
    # Create index
    op.create_index('idx_devices_client', 'devices', ['client_id'])


def downgrade():
    # Drop index
    op.drop_index('idx_devices_client')
    
    # Drop foreign key
    op.drop_constraint('fk_devices_client_id', 'devices', type_='foreignkey')
    
    # Drop columns from devices
    op.drop_column('devices', 'connection_params')
    op.drop_column('devices', 'connection_type')
    op.drop_column('devices', 'client_id')
    
    # Drop indexes
    op.drop_index('idx_clients_status')
    op.drop_index('idx_clients_workspace')
    
    # Drop clients table
    op.drop_table('clients')
