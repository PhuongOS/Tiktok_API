"""
Rule API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.rule import Rule, RuleCondition, RuleAction, RuleStatus, RuleExecution
from app.schemas.rule import RuleCreate, RuleResponse, RuleExecutionResponse

router = APIRouter(prefix="/api/rules", tags=["Rules"])


# TODO: Get from Auth Service JWT
from fastapi import Request
async def get_current_workspace(request: Request) -> str:
    return request.headers.get("X-Workspace-ID", "workspace-123")

async def get_current_user() -> str:
    return "user-123"


@router.post("", response_model=RuleResponse, status_code=201)
async def create_rule(
    data: RuleCreate,
    workspace_id: str = Depends(get_current_workspace),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new rule"""
    rule = Rule(
        workspace_id=workspace_id,
        created_by=user_id,
        name=data.name,
        description=data.description,
        event_type=data.event_type,
        livestream_id=data.livestream_id,
        logic_operator=data.logic_operator,
        status=RuleStatus.DRAFT
    )
    
    # Add conditions
    for cond_data in data.conditions:
        condition = RuleCondition(
            rule=rule,
            field=cond_data.field,
            operator=cond_data.operator,
            value=cond_data.value,
            order=cond_data.order
        )
        rule.conditions.append(condition)
    
    # Add actions
    for action_data in data.actions:
        action = RuleAction(
            rule=rule,
            action_type=action_data.action_type,
            config=action_data.config,
            order=action_data.order
        )
        rule.actions.append(action)
    
    db.add(rule)
    await db.commit()
    
    # Re-fetch rule with eager loading to avoid MissingGreenlet error
    result = await db.execute(
        select(Rule)
        .options(selectinload(Rule.conditions), selectinload(Rule.actions))
        .where(Rule.id == rule.id)
    )
    rule = result.scalar_one()
    
    return rule


@router.get("", response_model=List[RuleResponse])
async def list_rules(
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List all rules"""
    result = await db.execute(
        select(Rule)
        .options(selectinload(Rule.conditions), selectinload(Rule.actions))
        .where(Rule.workspace_id == workspace_id)
        .order_by(Rule.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Get rule details"""
    result = await db.execute(
        select(Rule)
        .options(selectinload(Rule.conditions), selectinload(Rule.actions))
        .where(
            Rule.id == rule_id,
            Rule.workspace_id == workspace_id
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule


@router.patch("/{rule_id}/activate")
async def activate_rule(
    rule_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Activate rule"""
    result = await db.execute(
        select(Rule).where(
            Rule.id == rule_id,
            Rule.workspace_id == workspace_id
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.status = RuleStatus.ACTIVE
    await db.commit()
    
    return {"message": "Rule activated"}


@router.patch("/{rule_id}/deactivate")
async def deactivate_rule(
    rule_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate rule"""
    result = await db.execute(
        select(Rule).where(
            Rule.id == rule_id,
            Rule.workspace_id == workspace_id
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.status = RuleStatus.INACTIVE
    await db.commit()
    
    return {"message": "Rule deactivated"}


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Delete rule"""
    result = await db.execute(
        select(Rule).where(
            Rule.id == rule_id,
            Rule.workspace_id == workspace_id
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db.delete(rule)
    await db.commit()
    
    return {"message": "Rule deleted"}


@router.get("/{rule_id}/executions", response_model=List[RuleExecutionResponse])
async def list_rule_executions(
    rule_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List rule executions"""
    # First check if rule exists
    result = await db.execute(
        select(Rule).where(
            Rule.id == rule_id,
            Rule.workspace_id == workspace_id
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Get executions
    result = await db.execute(
        select(RuleExecution)
        .where(RuleExecution.rule_id == rule_id)
        .order_by(RuleExecution.executed_at.desc())
        .limit(50)
    )
    return result.scalars().all()
