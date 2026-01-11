"""
Redis Event Consumer for Rule Engine
"""
import asyncio
import json
import logging
import os
from typing import Dict, List, Any
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session_factory
from app.models.rule import Rule, RuleStatus
from app.services.rule_evaluator import RuleEvaluator
from app.services.action_executor import ActionExecutor

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes TikTok events from Redis and triggers rules"""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis: redis.Redis = None
        self.cursors: Dict[str, str] = {}  # stream_key -> last_id
        self.running = False
        self.evaluator = RuleEvaluator()
        self.executor = ActionExecutor()

    async def start(self):
        """Start the consumer loop"""
        logger.info("🚀 Starting Redis Event Consumer...")
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        self.running = True
        
        while self.running:
            try:
                # 1. Discover streams (active workspaces)
                # In production, we might use a separate 'active_workspaces' set in Redis
                # For now, we'll query the DB for active rules to know which workspaces to listen to
                active_streams = await self._get_active_streams()
                
                if not active_streams:
                    # No active rules? Sleep and retry
                    await asyncio.sleep(5)
                    continue

                # 2. Prepare streams dict for XREAD (key -> last_id)
                # Use '$' for new streams to only get new messages
                # Use self.cursors[key] for existing streams to continue where we left off
                xread_streams = {}
                for stream in active_streams:
                    if stream in self.cursors:
                        xread_streams[stream] = self.cursors[stream]
                    else:
                        # New stream, start from beginning to catch any pending events
                        # This fixes race conditions where event is published before we start listening
                        xread_streams[stream] = "0"
                        # Initialize cursor
                        # We need to get the last ID if we use '$' in XREAD so we can update cursor?
                        # XREAD with '$' blocks until NEW message.
                        # If we have mixed streams (some new, some old), we can't use '$' easily mixed with IDs?
                        # Actually XREAD keys ID keys ID... 
                        # If we pass '$', it ignores history.
                        # Let's start with '$' for new ones.

                # 3. Read from streams
                # Block for 2 seconds (2000ms). If running=False, we exit loop.
                try:
                    events = await self.redis.xread(xread_streams, count=10, block=2000)
                except redis.exceptions.ResponseError as e:
                    logger.error(f"Redis XREAD Error: {e}")
                    # Might happen if stream doesn't exist yet?
                    # If stream doesn't exist, XREAD might fail or just ignore.
                    # With redis-py, if we ask for '$' on non-existent stream, it acts as if empty usually.
                    await asyncio.sleep(1)
                    continue

                if events:
                    for stream, messages in events:
                        for message_id, data in messages:
                            await self._process_event(stream, message_id, data)
                            # Update cursor
                            self.cursors[stream] = message_id
                
            except Exception as e:
                logger.error(f"❌ Consumer Error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Backoff

    async def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.redis:
            await self.redis.close()
        logger.info("🛑 Redis Event Consumer stopped")

    async def _get_active_streams(self) -> List[str]:
        """
        Get list of Redis streams to listen to based on active rules.
        Stream format: tiktok:events:{workspace_id}
        """
        async with async_session_factory() as db:
            # distinct workspace_id from rules where status = 'active'
            result = await db.execute(
                select(Rule.workspace_id)
                .where(Rule.status == RuleStatus.ACTIVE)
                .distinct()
            )
            workspace_ids = result.scalars().all()
            
            return [f"tiktok:events:{ws_id}" for ws_id in workspace_ids]

    async def _process_event(self, stream: str, message_id: str, data: Dict[str, Any]):
        """Process a single event"""
        try:
            workspace_id = stream.split(":")[-1]
            event_type = data.get("event_type")
            
            logger.debug(f"📥 Processing {event_type} from {workspace_id} (ID: {message_id})")
            
            # Fetch active rules for this workspace and event type
            rules = await self._get_matching_rules(workspace_id, event_type)
            
            for rule in rules:
                try:
                    # Evaluate Rule
                    if self.evaluator.evaluate_rule(rule, data):
                        logger.info(f"✅ Rule Matched: {rule.name} (ID: {rule.id})")
                        
                        # Execute Actions
                        await self.executor.execute_rule(rule, data, message_id)
                except Exception as e:
                    logger.error(f"Error processing rule {rule.id}: {e}")

        except Exception as e:
            logger.error(f"Error processing event {message_id}: {e}")

    async def _get_matching_rules(self, workspace_id: str, event_type: str) -> List[Rule]:
        """Fetch active rules for workspace and event type"""
        async with async_session_factory() as db:
            result = await db.execute(
                select(Rule)
                .options(selectinload(Rule.conditions), selectinload(Rule.actions))
                .where(
                    Rule.workspace_id == workspace_id,
                    Rule.status == RuleStatus.ACTIVE,
                    Rule.event_type == event_type
                )
            )
            return result.scalars().all()

# Global instance
event_consumer = EventConsumer()
