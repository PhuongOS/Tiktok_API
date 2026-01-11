"""add_enum_types

Revision ID: b0eb7e89b7ac
Revises: 002
Create Date: 2026-01-08 09:09:39.652682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0eb7e89b7ac'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE plantier AS ENUM ('free', 'pro', 'enterprise')")
    op.execute("CREATE TYPE workspacerole AS ENUM ('owner', 'admin', 'operator', 'viewer')")
    
    # Drop default constraint, alter type, recreate default
    op.execute("ALTER TABLE workspaces ALTER COLUMN plan_tier DROP DEFAULT")
    op.execute("ALTER TABLE workspaces ALTER COLUMN plan_tier TYPE plantier USING plan_tier::plantier")
    op.execute("ALTER TABLE workspaces ALTER COLUMN plan_tier SET DEFAULT 'free'::plantier")
    
    # Alter workspace_members role column
    op.execute("ALTER TABLE workspace_members ALTER COLUMN role TYPE workspacerole USING role::workspacerole")


def downgrade() -> None:
    # Revert columns to string
    op.execute("ALTER TABLE workspaces ALTER COLUMN plan_tier DROP DEFAULT")
    op.execute("ALTER TABLE workspaces ALTER COLUMN plan_tier TYPE VARCHAR")
    op.execute("ALTER TABLE workspaces ALTER COLUMN plan_tier SET DEFAULT 'free'")
    
    op.execute("ALTER TABLE workspace_members ALTER COLUMN role TYPE VARCHAR")
    
    # Drop enum types
    op.execute('DROP TYPE workspacerole')
    op.execute('DROP TYPE plantier')

