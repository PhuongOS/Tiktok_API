"""
Main entry point for IoT Worker Service
"""
import logging
import sys
import asyncio
from app.config import config
from app.thingsboard_client import ThingsBoardClient
from app.redis_consumer import RedisStreamConsumer
from app.event_processor import EventProcessor
from app.processors.gift_processor import GiftProcessor

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IoTWorkerService:
    """Main IoT Worker Service"""
    
    def __init__(self):
        self.tb_client = None
        self.redis_consumer = None
        self.event_processor = None
        self.running = False
    
    async def start(self):
        """Start the service"""
        logger.info("=" * 60)
        logger.info("Starting IoT Worker Service...")
        logger.info("=" * 60)
        logger.info(f"ThingsBoard URL: {config.THINGSBOARD_URL}")
        logger.info(f"MQTT Host: {config.THINGSBOARD_MQTT_HOST}:{config.THINGSBOARD_MQTT_PORT}")
        logger.info(f"Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
        
        # Initialize ThingsBoard client
        self.tb_client = ThingsBoardClient(
            base_url=config.THINGSBOARD_URL,
            username=config.THINGSBOARD_USERNAME,
            password=config.THINGSBOARD_PASSWORD
        )
        
        # Login
        if not self.tb_client.login():
            logger.error("Failed to login to ThingsBoard")
            sys.exit(1)
        
        # Initialize Redis consumer
        self.redis_consumer = RedisStreamConsumer(
            redis_host=config.REDIS_HOST,
            redis_port=config.REDIS_PORT,
            redis_db=config.REDIS_DB,
            consumer_group="iot-workers",
            consumer_name="worker-1"
        )
        
        if not self.redis_consumer.connect():
            logger.error("Failed to connect to Redis")
            sys.exit(1)
        
        # Initialize processors
        gift_processor = GiftProcessor()
        
        # Initialize event processor
        self.event_processor = EventProcessor(
            tb_client=self.tb_client,
            redis_consumer=self.redis_consumer,
            gift_processor=gift_processor
        )
        
        self.running = True
        logger.info("=" * 60)
        logger.info("IoT Worker Service started successfully!")
        logger.info("=" * 60)
        
        # Start processing events
        # Stream keys to consume from
        stream_keys = [
            "iot:commands:workspace-123",  # TODO: Make this dynamic based on workspaces
        ]
        
        try:
            await self.event_processor.start(stream_keys)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await self.stop()
    
    async def stop(self):
        """Stop the service"""
        logger.info("Stopping IoT Worker Service...")
        self.running = False
        
        if self.event_processor:
            self.event_processor.stop()
        
        logger.info("IoT Worker Service stopped")


async def main():
    """Main function"""
    service = IoTWorkerService()
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
