"""
Configuration management for IoT Worker
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # ThingsBoard
    THINGSBOARD_URL: str = os.getenv("THINGSBOARD_URL", "https://iot-gateway.lps.io.vn")
    THINGSBOARD_MQTT_HOST: str = os.getenv("THINGSBOARD_MQTT_HOST", "iot-gateway.lps.io.vn")
    THINGSBOARD_MQTT_PORT: int = int(os.getenv("THINGSBOARD_MQTT_PORT", "1883"))
    THINGSBOARD_MQTT_SSL: bool = os.getenv("THINGSBOARD_MQTT_SSL", "false").lower() == "true"
    THINGSBOARD_USERNAME: str = os.getenv("THINGSBOARD_USERNAME", "")
    THINGSBOARD_PASSWORD: str = os.getenv("THINGSBOARD_PASSWORD", "")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Processing
    WORKER_COUNT: int = int(os.getenv("WORKER_COUNT", "4"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and key.isupper()
        }


# Global config instance
config = Config()
