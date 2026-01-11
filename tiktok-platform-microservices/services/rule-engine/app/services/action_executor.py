"""
Execute rule actions
"""
from typing import Dict, Any, List
from app.models.rule import RuleAction, ActionType, Rule, RuleExecution, ExecutionStatus
from app.database import async_session_factory
import httpx
import logging
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Execute rule actions"""

    async def execute_rule(self, rule: Rule, event: Dict[str, Any], event_id: str):
        """
        Execute rule actions and log execution
        """
        start_time = datetime.utcnow()
        
        # Create execution record
        execution = RuleExecution(
            rule_id=rule.id,
            event_id=event_id,
            event_type=rule.event_type,
            event_data=event,
            status=ExecutionStatus.PARTIAL
        )
        
        results = {"success": 0, "failed": 0}
        error_msg = None
        
        try:
            # Execute actions
            results = await self.execute_actions(rule.actions, event)
            
            # Determine status
            if results["failed"] == 0:
                execution.status = ExecutionStatus.SUCCESS
            elif results["success"] == 0 and len(rule.actions) > 0:
                execution.status = ExecutionStatus.FAILED
                error_msg = "All actions failed"
            else:
                execution.status = ExecutionStatus.PARTIAL
                
        except Exception as e:
            logger.error(f"Rule execution failed: {e}")
            execution.status = ExecutionStatus.FAILED
            error_msg = str(e)
            
        # duration
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Update execution record
        execution.actions_executed = results["success"]
        execution.actions_failed = results["failed"]
        execution.error_message = error_msg
        execution.duration_ms = int(duration)
        
        # Save to DB
        async with async_session_factory() as db:
            db.add(execution)
            
            # Update Rule stats
            # Need to re-fetch rule attached to this session or update via query
            # Update query is safer/faster
            from sqlalchemy import update
            await db.execute(
                update(Rule)
                .where(Rule.id == rule.id)
                .values(
                    execution_count=Rule.execution_count + 1,
                    last_executed_at=start_time
                )
            )
            
            await db.commit()
            logger.info(f"💾 Saved execution log for Rule {rule.id}")
    async def execute_actions(self, actions: List[RuleAction], event: Dict[str, Any]) -> Dict[str, int]:
        """
        Execute all actions for a rule
        
        Returns: {"success": count, "failed": count}
        """
        results = {"success": 0, "failed": 0}
        
        for action in sorted(actions, key=lambda a: a.order):
            try:
                await ActionExecutor._execute_action(action, event)
                results["success"] += 1
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                results["failed"] += 1
        
        return results
    
    @staticmethod
    async def _execute_action(action: RuleAction, event: Dict[str, Any]):
        """Execute single action"""
        action_type = action.action_type
        config = action.config
        
        # Replace template variables in config
        config = ActionExecutor._render_template(config, event)
        
        if action_type == ActionType.DEVICE_CONTROL:
            await ActionExecutor._device_control(config)
        
        elif action_type == ActionType.NOTIFICATION:
            await ActionExecutor._send_notification(config)
        
        elif action_type == ActionType.WEBHOOK:
            await ActionExecutor._call_webhook(config)
        
        elif action_type == ActionType.LOG:
            ActionExecutor._log_action(config)
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    @staticmethod
    async def _device_control(config: Dict):
        """Control device via Device Service webhook"""
        workspace_id = config.get("workspace_id")
        device_id = config.get("device_id")
        command_type = config.get("command", "custom")
        parameters = config.get("params", {})
        
        if not workspace_id or not device_id:
            raise ValueError("workspace_id and device_id are required for device control")
        
        # Call Device Service webhook endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8004/api/webhook/control",
                json={
                    "workspace_id": workspace_id,
                    "device_id": device_id,
                    "command_type": command_type,
                    "parameters": parameters
                },
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        logger.info(f"✅ Device control: {device_id} - {command_type} - {result.get('status')}")

    
    @staticmethod
    async def _send_notification(config: Dict):
        """Send notification"""
        title = config.get("title")
        message = config.get("message")
        
        # TODO: Implement notification service
        logger.info(f"📬 Notification: {title} - {message}")
    
    @staticmethod
    async def _call_webhook(config: Dict):
        """Call webhook"""
        url = config.get("url")
        method = config.get("method", "POST")
        body = config.get("body", {})
        headers = config.get("headers", {})
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                json=body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
        
        logger.info(f"🔗 Webhook called: {url}")
    
    @staticmethod
    def _log_action(config: Dict):
        """Log action"""
        message = config.get("message", "Rule triggered")
        logger.info(f"📝 {message}")
    
    @staticmethod
    def _render_template(config: Dict, event: Dict[str, Any]) -> Dict:
        """Replace {{variable}} with event values"""
        config_str = json.dumps(config)
        
        # Find all {{variable}} patterns
        pattern = r'\{\{(\w+)\}\}'
        
        def replace(match):
            var_name = match.group(1)
            return str(event.get(var_name, match.group(0)))
        
        config_str = re.sub(pattern, replace, config_str)
        
        return json.loads(config_str)
