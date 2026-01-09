"""Create device tables

Revision ID: 001
Revises: 
Create Date: 2026-01-09 11:15:00

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
    # Create enum types using DO block (PostgreSQL doesn't support IF NOT EXISTS for CREATE TYPE)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE devicetype AS ENUM ('arduino', 'esp32', 'raspberry_pi', 'virtual');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE devicestatus AS ENUM ('online', 'offline', 'error');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE commandstatus AS ENUM ('pending', 'sent', 'completed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('device_type', postgresql.ENUM('arduino', 'esp32', 'raspberry_pi', 'virtual', name='devicetype', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('online', 'offline', 'error', name='devicestatus', create_type=False), nullable=False, server_default='offline'),
        sa.Column('agent_token_hash', sa.String(), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('device_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_token_hash')
    )
    op.create_index('ix_devices_workspace_id', 'devices', ['workspace_id'])
    op.create_index('ix_devices_status', 'devices', ['status'])
    
    # Create device_commands table
    op.create_table(
        'device_commands',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('device_id', sa.String(), nullable=False),
        sa.Column('command_type', sa.String(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('status', postgresql.ENUM('pending', 'sent', 'completed', 'failed', name='commandstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE')
    )
    op.create_index('ix_device_commands_device_id', 'device_commands', ['device_id'])
    op.create_index('ix_device_commands_status', 'device_commands', ['status'])
    
    # Create device_states table
    op.create_table(
        'device_states',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('device_id', sa.String(), nullable=False),
        sa.Column('state_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE')
    )
    op.create_index('ix_device_states_device_id', 'device_states', ['device_id'])
    op.create_index('ix_device_states_timestamp', 'device_states', ['timestamp'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('device_states')
    op.drop_table('device_commands')
    op.drop_table('devices')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS commandstatus')
    op.execute('DROP TYPE IF EXISTS devicestatus')
    op.execute('DROP TYPE IF EXISTS devicetype')
