"""
Event Processing Pipeline
Orchestrates the flow from Redis to ThingsBoard
"""
import logging
import asyncio
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from app.redis_consumer import RedisStreamConsumer
from app.thingsboard_client import ThingsBoardClient
from app.mqtt_client import ThingsBoardMQTTClient
from app.processors.gift_processor import GiftProcessor

logger = logging.getLogger(__name__)


class EventProcessor:
    """Main event processing pipeline"""
    
    def __init__(
        self,
        tb_client: ThingsBoardClient,
        redis_consumer: RedisStreamConsumer,
        gift_processor: GiftProcessor
    ):
        self.tb_client = tb_client
        self.redis_consumer = redis_consumer
        self.gift_processor = gift_processor
        
        # Device ID to MQTT client mapping
        self.mqtt_clients: Dict[str, ThingsBoardMQTTClient] = {}
        
        # Device ID to ThingsBoard device token mapping
        self.device_tokens: Dict[str, str] = {}
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "commands_sent": 0,
            "errors": 0
        }
    
    async def initialize(self):
        """Initialize the processor"""
        logger.info("Initializing Event Processor...")
        
        # Register event handlers
        self.redis_consumer.register_handler('gift', self.handle_gift_event)
        self.redis_consumer.register_handler('comment', self.handle_comment_event)
        
        # Load existing devices and setup MQTT connections
        await self.load_devices()
        
        logger.info("Event Processor initialized")
    
    async def load_devices(self):
        """Load devices from ThingsBoard and setup MQTT connections"""
        try:
            devices = self.tb_client.list_devices()
            logger.info(f"Loading {len(devices)} devices from ThingsBoard")
            
            for device in devices:
                device_id = device.get('id', {}).get('id')
                device_name = device.get('name')
                
                if device_id:
                    # Get device credentials
                    token = self.tb_client.get_device_credentials(device_id)
                    if token:
                        self.device_tokens[device_name] = token
                        logger.info(f"Loaded device: {device_name}")
                        
                        # TODO: Create MQTT connection for each device
                        # For now, we'll create connections on-demand
        
        except Exception as e:
            logger.error(f"Error loading devices: {str(e)}")
    
    async def get_or_create_mqtt_client(
        self,
        device_id: str,
        mqtt_host: str,
        mqtt_port: int
    ) -> Optional[ThingsBoardMQTTClient]:
        """Get existing MQTT client or create new one"""
        if device_id in self.mqtt_clients:
            return self.mqtt_clients[device_id]
        
        # Get device token
        token = self.device_tokens.get(device_id)
        if not token:
            logger.error(f"No token found for device: {device_id}")
            return None
        
        # Create MQTT client
        mqtt_client = ThingsBoardMQTTClient(
            host=mqtt_host,
            port=mqtt_port
        )
        
        if mqtt_client.connect(token):
            self.mqtt_clients[device_id] = mqtt_client
            logger.info(f"Created MQTT client for device: {device_id}")
            return mqtt_client
        else:
            logger.error(f"Failed to connect MQTT client for device: {device_id}")
            return None
    
    async def handle_gift_event(self, event_data: Dict[str, Any]):
        """
        Handle gift event
        
        Args:
            event_data: Gift event data
            {
                "type": "gift",
                "user": {...},
                "gift": {"name": "Rose", "diamond_count": 1},
                "repeat_count": 10,
                "workspace_id": "workspace-123",
                "livestream_id": "livestream-uuid"
            }
        """
        try:
            logger.info(f"Handling gift event: {event_data.get('gift', {}).get('name')}")
            
            # Process gift to device command
            command = self.gift_processor.process(event_data)
            
            if command:
                # Send command to device
                await self.send_device_command(command)
                self.stats["commands_sent"] += 1
            else:
                logger.debug("No command generated from gift event")
            
            self.stats["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling gift event: {str(e)}")
            self.stats["errors"] += 1
    
    async def handle_comment_event(self, event_data: Dict[str, Any]):
        """Handle comment event"""
        try:
            comment = event_data.get('comment', '')
            logger.info(f"Handling comment event: {comment[:50]}")
            
            # TODO: Implement comment-based device control
            # For example: "red light on" -> turn on red LED
            
            self.stats["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling comment event: {str(e)}")
            self.stats["errors"] += 1
    
    async def send_device_command(self, command: Dict[str, Any]):
        """
        Send command to device via MQTT
        
        Args:
            command: Device command
            {
                "device_id": "motor_01",
                "method": "rotate",
                "params": {"rounds": 10, "speed": 100}
            }
        """
        try:
            device_id = command.get('device_id')
            method = command.get('method')
            params = command.get('params', {})
            
            logger.info(f"Sending command to {device_id}: {method}({params})")
            
            # Get or create MQTT client
            mqtt_client = await self.get_or_create_mqtt_client(
                device_id,
                mqtt_host="iot-gateway.lps.io.vn",
                mqtt_port=1883
            )
            
            if mqtt_client:
                # Generate request ID
                request_id = str(uuid.uuid4())
                
                # Send RPC request
                success = mqtt_client.send_rpc_request(request_id, method, params)
                
                if success:
                    logger.info(f"Command sent successfully to {device_id}")
                else:
                    logger.error(f"Failed to send command to {device_id}")
            else:
                logger.error(f"No MQTT client available for {device_id}")
        
        except Exception as e:
            logger.error(f"Error sending device command: {str(e)}")
    
    async def start(self, stream_keys: list):
        """Start processing events"""
        logger.info("Starting Event Processor...")
        
        # Initialize
        await self.initialize()
        
        # Start consuming from Redis Streams
        await self.redis_consumer.consume(stream_keys)
    
    def stop(self):
        """Stop processing"""
        logger.info("Stopping Event Processor...")
        
        # Stop consumer
        self.redis_consumer.stop()
        
        # Disconnect all MQTT clients
        for device_id, mqtt_client in self.mqtt_clients.items():
            mqtt_client.disconnect()
            logger.info(f"Disconnected MQTT client for {device_id}")
        
        # Log statistics
        logger.info(f"Statistics: {self.stats}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        return self.stats.copy()
