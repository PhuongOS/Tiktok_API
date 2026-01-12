"""
MQTT Client for ThingsBoard
Handles MQTT connections and message publishing
"""
import paho.mqtt.client as mqtt
import logging
import json
import ssl
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


class ThingsBoardMQTTClient:
    """MQTT client for ThingsBoard communication"""
    
    def __init__(
        self,
        host: str,
        port: int = 1883,
        use_ssl: bool = False,
        keepalive: int = 60
    ):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.keepalive = keepalive
        self.client: Optional[mqtt.Client] = None
        self.device_token: Optional[str] = None
        self.connected = False
    
    def connect(self, device_token: str) -> bool:
        """Connect to ThingsBoard MQTT broker"""
        try:
            self.device_token = device_token
            
            # Create MQTT client
            self.client = mqtt.Client()
            
            # Set username (device token)
            self.client.username_pw_set(device_token)
            
            # Setup callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # SSL/TLS
            if self.use_ssl:
                self.client.tls_set(
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
            
            # Connect
            logger.info(f"Connecting to MQTT broker at {self.host}:{self.port}")
            self.client.connect(self.host, self.port, self.keepalive)
            
            # Start loop
            self.client.loop_start()
            
            return True
        except Exception as e:
            logger.error(f"MQTT connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to ThingsBoard MQTT broker")
            
            # Subscribe to RPC responses
            client.subscribe("v1/devices/me/rpc/response/+")
            logger.info("Subscribed to RPC responses")
        else:
            logger.error(f"Connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection (code {rc})")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on {topic}: {payload}")
            
            # Handle RPC responses
            if topic.startswith("v1/devices/me/rpc/response/"):
                request_id = topic.split("/")[-1]
                self._handle_rpc_response(request_id, payload)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def _handle_rpc_response(self, request_id: str, payload: Dict):
        """Handle RPC response from device"""
        logger.info(f"RPC response {request_id}: {payload}")
        # TODO: Store response in Redis or database
    
    def publish_telemetry(self, data: Dict[str, Any]) -> bool:
        """Publish telemetry data"""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return False
        
        try:
            topic = "v1/devices/me/telemetry"
            payload = json.dumps(data)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published telemetry: {data}")
                return True
            else:
                logger.error(f"Failed to publish telemetry: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing telemetry: {str(e)}")
            return False
    
    def send_rpc_request(self, request_id: str, method: str, params: Dict) -> bool:
        """Send RPC request to device"""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return False
        
        try:
            topic = f"v1/devices/me/rpc/request/{request_id}"
            payload = json.dumps({"method": method, "params": params})
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Sent RPC request {request_id}: {method}({params})")
                return True
            else:
                logger.error(f"Failed to send RPC: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error sending RPC: {str(e)}")
            return False
