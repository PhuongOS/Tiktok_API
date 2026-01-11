"""
Redis Streams event publisher
"""
import redis.asyncio as redis
from typing import Dict, Any
import os
import logging

logger = logging.getLogger(__name__)


class RedisEventPublisher:
    """Publish TikTok events to Redis Streams"""
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    async def publish_event(
        self,
        workspace_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> str:
        """
        Publish to Redis Stream
        
        Stream: tiktok:events:{workspace_id}
        """
        stream_key = f"tiktok:events:{workspace_id}"
        
        message = {
            "event_type": event_type,
            **event_data
        }
        
        message_id = await self.redis.xadd(
            stream_key,
            message,
            maxlen=10000  # Keep last 10k events
        )
        
        logger.debug(f"📤 {event_type} → {stream_key}")
        return message_id
    
    async def close(self):
        await self.redis.close()


# Global instance
redis_publisher = RedisEventPublisher()
