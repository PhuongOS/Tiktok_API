"""
Main entry point for IoT Worker Service
"""
import logging
import sys
import time
from app.config import config
from app.thingsboard_client import ThingsBoardClient
from app.mqtt_client import ThingsBoardMQTTClient
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
        self.mqtt_client = None
        self.gift_processor = GiftProcessor()
        self.running = False
    
    def start(self):
        """Start the service"""
        logger.info("Starting IoT Worker Service...")
        logger.info(f"ThingsBoard URL: {config.THINGSBOARD_URL}")
        logger.info(f"MQTT Host: {config.THINGSBOARD_MQTT_HOST}:{config.THINGSBOARD_MQTT_PORT}")
        
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
        
        # List existing devices
        devices = self.tb_client.list_devices()
        logger.info(f"Found {len(devices)} existing devices")
        for device in devices:
            logger.info(f"  - {device.get('name')} ({device.get('type')})")
        
        # TODO: Initialize MQTT connections for each device
        # TODO: Start Redis Stream consumer
        # TODO: Start processing loop
        
        self.running = True
        logger.info("IoT Worker Service started successfully")
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
    
    def stop(self):
        """Stop the service"""
        logger.info("Stopping IoT Worker Service...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        logger.info("IoT Worker Service stopped")


def main():
    """Main function"""
    service = IoTWorkerService()
    service.start()


if __name__ == "__main__":
    main()
