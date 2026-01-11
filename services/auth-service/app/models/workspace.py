"""
Workspace models for multi-tenancy
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class PlanTier(str, enum.Enum):
    """Subscription plan tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class WorkspaceRole(str, enum.Enum):
    """User roles within a workspace"""
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Workspace(Base):
    """Workspace model for multi-tenancy"""
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_tier = Column(SQLEnum(PlanTier, values_callable=lambda x: [e.value for e in x]), default=PlanTier.FREE, nullable=False)

    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name})>"


class WorkspaceMember(Base):
    """Workspace membership with roles"""
    __tablename__ = "workspace_members"
    
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(SQLEnum(WorkspaceRole, values_callable=lambda x: [e.value for e in x]), nullable=False)

    
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    
    def __repr__(self):
        return f"<WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, role={self.role})>"
