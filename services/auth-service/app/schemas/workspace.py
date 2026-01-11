"""
Pydantic schemas for workspaces
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.models.workspace import PlanTier, WorkspaceRole


# Request Schemas
class WorkspaceCreate(BaseModel):
    """Workspace creation request"""
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    plan_tier: Optional[PlanTier] = PlanTier.FREE


class WorkspaceMemberAdd(BaseModel):
    """Add member to workspace request"""
    user_id: str
    role: WorkspaceRole


# Response Schemas
class WorkspaceResponse(BaseModel):
    """Workspace response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    owner_id: str
    plan_tier: PlanTier
    created_at: datetime
    updated_at: Optional[datetime] = None


class WorkspaceMemberResponse(BaseModel):
    """Workspace member response"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    role: WorkspaceRole
    joined_at: datetime
