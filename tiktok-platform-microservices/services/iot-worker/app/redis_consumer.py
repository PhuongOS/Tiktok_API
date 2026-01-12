"""
Redis Streams Consumer
Consumes events from Redis Streams and processes them
"""
import redis
import logging
import json
import asyncio
from typing import Dict, Any, Callable, Optional, List
import time

logger = logging.getLogger(__name__)


class RedisStreamConsumer:
    """Consumer for Redis Streams"""
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        consumer_group: str = "iot-workers",
        consumer_name: str = "worker-1"
    ):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        
        self.redis_client: Optional[redis.Redis] = None
        self.running = False
        self.event_handlers: Dict[str, Callable] = {}
    
    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            return False
    
    def create_consumer_group(self, stream_key: str) -> bool:
        """Create consumer group if not exists"""
        try:
            # Try to create group
            self.redis_client.xgroup_create(
                name=stream_key,
                groupname=self.consumer_group,
                id='0',
                mkstream=True
            )
            logger.info(f"Created consumer group '{self.consumer_group}' for stream '{stream_key}'")
            return True
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group '{self.consumer_group}' already exists")
                return True
            else:
                logger.error(f"Failed to create consumer group: {str(e)}")
                return False
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
    
    async def consume(
        self,
        stream_keys: List[str],
        batch_size: int = 10,
        block_ms: int = 1000
    ):
        """
        Consume events from Redis Streams
        
        Args:
            stream_keys: List of stream keys to consume from
            batch_size: Number of messages to read per batch
            block_ms: Milliseconds to block waiting for messages
        """
        if not self.redis_client:
            logger.error("Not connected to Redis")
            return
        
        # Create consumer groups
        for stream_key in stream_keys:
            self.create_consumer_group(stream_key)
        
        logger.info(f"Starting consumer '{self.consumer_name}' for streams: {stream_keys}")
        self.running = True
        
        # Prepare stream dict for xreadgroup
        streams = {key: '>' for key in stream_keys}
        
        while self.running:
            try:
                # Read from streams
                messages = self.redis_client.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams=streams,
                    count=batch_size,
                    block=block_ms
                )
                
                if messages:
                    await self._process_messages(messages)
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.01)
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                break
            except Exception as e:
                logger.error(f"Error consuming messages: {str(e)}")
                await asyncio.sleep(1)
        
        logger.info("Consumer stopped")
    
    async def _process_messages(self, messages: List):
        """Process batch of messages"""
        for stream_key, stream_messages in messages:
            for message_id, message_data in stream_messages:
                try:
                    await self._process_message(stream_key, message_id, message_data)
                    
                    # Acknowledge message
                    self.redis_client.xack(stream_key, self.consumer_group, message_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message {message_id}: {str(e)}")
                    # TODO: Move to dead letter queue
    
    async def _process_message(self, stream_key: str, message_id: str, message_data: Dict):
        """Process single message"""
        try:
            # Parse message data
            event_type = message_data.get('type', 'unknown')
            event_data = json.loads(message_data.get('data', '{}'))
            
            logger.info(f"Processing {event_type} event from {stream_key} (ID: {message_id})")
            
            # Get handler
            handler = self.event_handlers.get(event_type)
            if handler:
                await handler(event_data)
            else:
                logger.warning(f"No handler registered for event type: {event_type}")
        
        except Exception as e:
            logger.error(f"Error in message processing: {str(e)}")
            raise
    
    def stop(self):
        """Stop consuming"""
        self.running = False
        logger.info("Stopping consumer...")
    
    def get_pending_count(self, stream_key: str) -> int:
        """Get count of pending messages"""
        try:
            pending = self.redis_client.xpending(stream_key, self.consumer_group)
            return pending['pending']
        except Exception as e:
            logger.error(f"Error getting pending count: {str(e)}")
            return 0
    
    def claim_pending_messages(
        self,
        stream_key: str,
        min_idle_time: int = 60000,
        count: int = 10
    ) -> List:
        """
        Claim pending messages that have been idle too long
        
        Args:
            stream_key: Stream key
            min_idle_time: Minimum idle time in milliseconds
            count: Number of messages to claim
        """
        try:
            # Get pending messages
            pending = self.redis_client.xpending_range(
                name=stream_key,
                groupname=self.consumer_group,
                min='-',
                max='+',
                count=count
            )
            
            claimed = []
            for msg in pending:
                if msg['time_since_delivered'] >= min_idle_time:
                    # Claim message
                    result = self.redis_client.xclaim(
                        name=stream_key,
                        groupname=self.consumer_group,
                        consumername=self.consumer_name,
                        min_idle_time=min_idle_time,
                        message_ids=[msg['message_id']]
                    )
                    claimed.extend(result)
            
            if claimed:
                logger.info(f"Claimed {len(claimed)} pending messages from {stream_key}")
            
            return claimed
        except Exception as e:
            logger.error(f"Error claiming pending messages: {str(e)}")
            return []
