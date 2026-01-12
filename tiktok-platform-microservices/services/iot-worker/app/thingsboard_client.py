"""
ThingsBoard API Client
Handles authentication and device management
"""
import requests
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ThingsBoardClient:
    """Client for ThingsBoard REST API"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.tenant_id: Optional[str] = None
    
    def login(self) -> bool:
        """Login and get JWT token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                logger.info(f"Logged in to ThingsBoard as {self.username}")
                
                # Get user info to retrieve tenant ID
                self._get_user_info()
                return True
            else:
                logger.error(f"Login failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def _get_user_info(self):
        """Get current user info"""
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/user",
                headers=self._headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                self.tenant_id = user.get('tenantId', {}).get('id')
                logger.info(f"Tenant ID: {self.tenant_id}")
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {"X-Authorization": f"Bearer {self.token}"}
    
    def create_device(self, name: str, device_type: str = "default", label: str = "") -> Optional[Dict]:
        """Create a new device"""
        try:
            response = requests.post(
                f"{self.base_url}/api/device",
                headers=self._headers(),
                json={
                    "name": name,
                    "type": device_type,
                    "label": label or name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                device = response.json()
                device_id = device.get('id', {}).get('id')
                logger.info(f"Created device: {name} (ID: {device_id})")
                return device
            else:
                logger.error(f"Failed to create device: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error creating device: {str(e)}")
            return None
    
    def get_device_credentials(self, device_id: str) -> Optional[str]:
        """Get device access token"""
        try:
            response = requests.get(
                f"{self.base_url}/api/device/{device_id}/credentials",
                headers=self._headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                creds = response.json()
                token = creds.get('credentialsId')
                logger.info(f"Retrieved credentials for device {device_id}")
                return token
            else:
                logger.error(f"Failed to get credentials: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting credentials: {str(e)}")
            return None
    
    def list_devices(self, page_size: int = 100) -> List[Dict]:
        """List all devices"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tenant/devices",
                headers=self._headers(),
                params={"pageSize": page_size, "page": 0},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                devices = data.get('data', [])
                logger.info(f"Retrieved {len(devices)} devices")
                return devices
            else:
                logger.error(f"Failed to list devices: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing devices: {str(e)}")
            return []
    
    def send_rpc_command(self, device_id: str, method: str, params: Dict) -> bool:
        """Send RPC command to device"""
        try:
            response = requests.post(
                f"{self.base_url}/api/rpc/oneway/{device_id}",
                headers=self._headers(),
                json={"method": method, "params": params},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Sent RPC command to {device_id}: {method}")
                return True
            else:
                logger.error(f"Failed to send RPC: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error sending RPC: {str(e)}")
            return False
