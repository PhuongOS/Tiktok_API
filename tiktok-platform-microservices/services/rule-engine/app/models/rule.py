"""
Rule models for automation rules
"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Integer, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class RuleStatus(str, enum.Enum):
    """Rule status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class ComparisonOperator(str, enum.Enum):
    """Comparison operators"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


class ActionType(str, enum.Enum):
    """Action types"""
    DEVICE_CONTROL = "device_control"
    NOTIFICATION = "notification"
    WEBHOOK = "webhook"
    LOG = "log"


class ExecutionStatus(str, enum.Enum):
    """Execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class Rule(Base):
    """Automation rule"""
    __tablename__ = "rules"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenancy
    workspace_id = Column(String, nullable=False, index=True)
    created_by = Column(String, nullable=False)
    
    # Rule Info
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Status
    status = Column(
        SQLEnum(RuleStatus, values_callable=lambda x: [e.value for e in x]),
        default=RuleStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Trigger Config
    event_type = Column(String, nullable=False, index=True)  # comment, gift, like, etc.
    livestream_id = Column(String, nullable=True, index=True)  # null = all livestreams
    
    # Logic Operator
    logic_operator = Column(String, default="AND")  # AND or OR
    
    # Statistics
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conditions = relationship("RuleCondition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("RuleAction", back_populates="rule", cascade="all, delete-orphan")
    executions = relationship("RuleExecution", back_populates="rule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Rule(id={self.id}, name={self.name}, status={self.status})>"


class RuleCondition(Base):
    """Rule condition"""
    __tablename__ = "rule_conditions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String, ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    
    # Condition
    field = Column(String, nullable=False)  # e.g., "username", "gift_count", "comment"
    operator = Column(
        SQLEnum(ComparisonOperator, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    value = Column(String, nullable=False)  # Stored as string, converted at runtime
    
    # Order
    order = Column(Integer, default=0)
    
    # Relationship
    rule = relationship("Rule", back_populates="conditions")
    
    def __repr__(self):
        return f"<RuleCondition({self.field} {self.operator} {self.value})>"


class RuleAction(Base):
    """Rule action"""
    __tablename__ = "rule_actions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String, ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    
    # Action Type
    action_type = Column(
        SQLEnum(ActionType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    
    # Action Config (JSON)
    config = Column(JSON, nullable=False)
    
    # Order
    order = Column(Integer, default=0)
    
    # Relationship
    rule = relationship("Rule", back_populates="actions")
    
    def __repr__(self):
        return f"<RuleAction({self.action_type})>"


class RuleExecution(Base):
    """Rule execution audit log"""
    __tablename__ = "rule_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String, ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    
    # Event Info
    event_id = Column(String, nullable=False)  # Redis stream message ID
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, nullable=False)
    
    # Execution Result
    status = Column(
        SQLEnum(ExecutionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    actions_executed = Column(Integer, default=0)
    actions_failed = Column(Integer, default=0)
    error_message = Column(String)
    
    # Timing
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_ms = Column(Integer)  # Execution time in milliseconds
    
    # Relationship
    rule = relationship("Rule", back_populates="executions")
    
    def __repr__(self):
        return f"<RuleExecution(rule_id={self.rule_id}, status={self.status})>"
