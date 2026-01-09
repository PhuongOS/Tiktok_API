"""
Unit tests for User and Workspace models
"""
import pytest
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, PlanTier, WorkspaceRole


class TestUserModel:
    """Test User model"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
    
    @pytest.mark.asyncio
    async def test_user_default_values(self, db_session):
        """Test user default values"""
        user = User(
            email="defaults@example.com",
            password_hash="hash"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Check defaults
        assert user.is_active is True
        assert user.is_verified is False
    
    @pytest.mark.asyncio
    async def test_user_unique_email(self, db_session):
        """Test email uniqueness constraint"""
        user1 = User(email="unique@example.com", password_hash="hash1")
        db_session.add(user1)
        await db_session.commit()
        
        # Try to create another user with same email
        user2 = User(email="unique@example.com", password_hash="hash2")
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            await db_session.commit()


class TestWorkspaceModel:
    """Test Workspace model"""
    
    @pytest.mark.asyncio
    async def test_create_workspace(self, db_session):
        """Test creating a workspace"""
        # Create user first
        user = User(email="owner@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create workspace
        workspace = Workspace(
            name="Test Workspace",
            owner_id=user.id,
            plan_tier=PlanTier.FREE
        )
        
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)
        
        assert workspace.id is not None
        assert workspace.name == "Test Workspace"
        assert workspace.owner_id == user.id
        assert workspace.plan_tier == PlanTier.FREE
        assert workspace.created_at is not None
    
    @pytest.mark.asyncio
    async def test_workspace_plan_tiers(self, db_session):
        """Test different plan tiers"""
        user = User(email="plans@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        for tier in [PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE]:
            workspace = Workspace(
                name=f"{tier.value} Workspace",
                owner_id=user.id,
                plan_tier=tier
            )
            db_session.add(workspace)
        
        await db_session.commit()
        
        # Verify all created
        from sqlalchemy import select
        result = await db_session.execute(select(Workspace))
        workspaces = result.scalars().all()
        assert len(workspaces) == 3


class TestWorkspaceMemberModel:
    """Test WorkspaceMember model"""
    
    @pytest.mark.asyncio
    async def test_create_workspace_member(self, db_session):
        """Test creating a workspace member"""
        # Create user and workspace
        user = User(email="member@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        workspace = Workspace(
            name="Member Test",
            owner_id=user.id
        )
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)
        
        # Add member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER
        )
        
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(member)
        
        assert member.workspace_id == workspace.id
        assert member.user_id == user.id
        assert member.role == WorkspaceRole.OWNER
        assert member.joined_at is not None
    
    @pytest.mark.asyncio
    async def test_workspace_member_roles(self, db_session):
        """Test different workspace roles"""
        # Create users and workspace
        owner = User(email="owner@test.com", password_hash="hash")
        admin = User(email="admin@test.com", password_hash="hash")
        operator = User(email="operator@test.com", password_hash="hash")
        viewer = User(email="viewer@test.com", password_hash="hash")
        
        db_session.add_all([owner, admin, operator, viewer])
        await db_session.commit()
        
        for user in [owner, admin, operator, viewer]:
            await db_session.refresh(user)
        
        workspace = Workspace(name="Roles Test", owner_id=owner.id)
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)
        
        # Add members with different roles
        members = [
            WorkspaceMember(workspace_id=workspace.id, user_id=owner.id, role=WorkspaceRole.OWNER),
            WorkspaceMember(workspace_id=workspace.id, user_id=admin.id, role=WorkspaceRole.ADMIN),
            WorkspaceMember(workspace_id=workspace.id, user_id=operator.id, role=WorkspaceRole.OPERATOR),
            WorkspaceMember(workspace_id=workspace.id, user_id=viewer.id, role=WorkspaceRole.VIEWER),
        ]
        
        db_session.add_all(members)
        await db_session.commit()
        
        # Verify all roles
        from sqlalchemy import select
        result = await db_session.execute(
            select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace.id)
        )
        all_members = result.scalars().all()
        assert len(all_members) == 4
        
        roles = [m.role for m in all_members]
        assert WorkspaceRole.OWNER in roles
        assert WorkspaceRole.ADMIN in roles
        assert WorkspaceRole.OPERATOR in roles
        assert WorkspaceRole.VIEWER in roles
    
    @pytest.mark.asyncio
    async def test_workspace_member_cascade_delete(self, db_session):
        """Test cascade delete when workspace is deleted"""
        # Create user and workspace
        user = User(email="cascade@test.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        workspace = Workspace(name="Cascade Test", owner_id=user.id)
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)
        
        # Add member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER
        )
        db_session.add(member)
        await db_session.commit()
        
        # Delete workspace
        await db_session.delete(workspace)
        await db_session.commit()
        
        # Verify member is also deleted
        from sqlalchemy import select
        result = await db_session.execute(
            select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace.id)
        )
        members = result.scalars().all()
        assert len(members) == 0


# Run with: pytest tests/test_models.py -v
