"""
Gift Event Processor
Converts TikTok gift events to device commands
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GiftProcessor:
    """Process gift events and generate device commands"""
    
    def __init__(self):
        # Gift to device mapping configuration
        # This can be loaded from database in the future
        self.gift_mappings = {
            "Rose": {"action": "rotate", "multiplier": 1},
            "TikTok": {"action": "flash_led", "multiplier": 5},
            "Lion": {"action": "rotate", "multiplier": 10},
            "Universe": {"action": "special_effect", "multiplier": 100}
        }
    
    def process(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process gift event and return device command
        
        Args:
            event_data: Gift event data from TikTok
            {
                "type": "gift",
                "user": {"unique_id": "user123", "nickname": "John"},
                "gift": {"name": "Rose", "diamond_count": 1},
                "repeat_count": 10
            }
        
        Returns:
            Device command or None
            {
                "device_id": "motor_01",
                "method": "rotate",
                "params": {"rounds": 10, "speed": 100}
            }
        """
        try:
            gift = event_data.get('gift', {})
            gift_name = gift.get('name')
            diamond_count = gift.get('diamond_count', 0)
            repeat_count = event_data.get('repeat_count', 1)
            
            # Get gift mapping
            mapping = self.gift_mappings.get(gift_name)
            if not mapping:
                logger.debug(f"No mapping for gift: {gift_name}")
                return None
            
            # Calculate parameters
            total_diamonds = diamond_count * repeat_count
            multiplier = mapping.get('multiplier', 1)
            action = mapping.get('action')
            
            # Generate command based on action
            if action == "rotate":
                rounds = total_diamonds * multiplier
                speed = min(100, total_diamonds * 10)  # Max 100 RPM
                
                return {
                    "device_id": "motor_01",  # TODO: Get from rule/config
                    "method": "rotate",
                    "params": {
                        "rounds": rounds,
                        "speed": speed
                    }
                }
            
            elif action == "flash_led":
                duration = total_diamonds * multiplier
                
                return {
                    "device_id": "led_strip_01",
                    "method": "flash",
                    "params": {
                        "duration": duration,
                        "color": "#FF0000"
                    }
                }
            
            elif action == "special_effect":
                return {
                    "device_id": "motor_01",
                    "method": "special_effect",
                    "params": {
                        "effect_id": 1,
                        "duration": 30
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing gift event: {str(e)}")
            return None
    
    def add_mapping(self, gift_name: str, action: str, multiplier: int = 1):
        """Add or update gift mapping"""
        self.gift_mappings[gift_name] = {
            "action": action,
            "multiplier": multiplier
        }
        logger.info(f"Added gift mapping: {gift_name} → {action} (x{multiplier})")
    
    def remove_mapping(self, gift_name: str):
        """Remove gift mapping"""
        if gift_name in self.gift_mappings:
            del self.gift_mappings[gift_name]
            logger.info(f"Removed gift mapping: {gift_name}")
