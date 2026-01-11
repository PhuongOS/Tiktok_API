"""
Rule API schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.rule import RuleStatus, ComparisonOperator, ActionType, ExecutionStatus
import enum


class RuleConditionCreate(BaseModel):
    """Create rule condition"""
    field: str
    operator: ComparisonOperator
    value: str
    order: int = 0


class RuleActionCreate(BaseModel):
    """Create rule action"""
    action_type: ActionType
    config: Dict[str, Any]
    order: int = 0


class RuleCreate(BaseModel):
    """Create rule"""
    name: str
    description: Optional[str] = None
    event_type: str
    livestream_id: Optional[str] = None
    logic_operator: str = "AND"
    conditions: List[RuleConditionCreate] = []
    actions: List[RuleActionCreate] = []


class RuleConditionResponse(BaseModel):
    """Rule condition response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    field: str
    operator: ComparisonOperator
    value: str
    order: int


class RuleActionResponse(BaseModel):
    """Rule action response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    action_type: ActionType
    config: Dict[str, Any]
    order: int


class ExecutionStatus(str, enum.Enum):
    """Execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class RuleExecutionResponse(BaseModel):
    """Rule execution response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    event_id: str
    event_type: str
    status: ExecutionStatus
    executed_at: datetime
    duration_ms: Optional[int]
    error_message: Optional[str]
    actions_executed: int


class RuleResponse(BaseModel):
    """Rule response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    status: RuleStatus
    event_type: str
    livestream_id: Optional[str]
    logic_operator: str
    execution_count: int
    last_executed_at: Optional[datetime]
    created_at: datetime
    conditions: List[RuleConditionResponse] = []
    actions: List[RuleActionResponse] = []
