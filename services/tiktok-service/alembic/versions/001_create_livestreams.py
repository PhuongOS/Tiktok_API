"""create livestreams table

Revision ID: 001
Revises: 
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type
    op.execute("CREATE TYPE livestreamstatus AS ENUM ('connecting', 'live', 'disconnected', 'error')")
    
    # Create table
    op.create_table(
        'livestreams',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('tiktok_username', sa.String(), nullable=False),
        sa.Column('room_id', sa.String()),
        sa.Column('status', sa.Enum('connecting', 'live', 'disconnected', 'error', name='livestreamstatus'), nullable=False),
        sa.Column('total_comments', sa.Integer(), server_default='0'),
        sa.Column('total_gifts', sa.Integer(), server_default='0'),
        sa.Column('total_likes', sa.Integer(), server_default='0'),
        sa.Column('total_joins', sa.Integer(), server_default='0'),
        sa.Column('total_follows', sa.Integer(), server_default='0'),
        sa.Column('total_shares', sa.Integer(), server_default='0'),
        sa.Column('total_events', sa.Integer(), server_default='0'),
        sa.Column('connected_at', sa.DateTime(timezone=True)),
        sa.Column('disconnected_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_livestreams_workspace_id', 'livestreams', ['workspace_id'])
    op.create_index('ix_livestreams_tiktok_username', 'livestreams', ['tiktok_username'])
    op.create_index('ix_livestreams_status', 'livestreams', ['status'])


def downgrade() -> None:
    op.drop_table('livestreams')
    op.execute('DROP TYPE livestreamstatus')
