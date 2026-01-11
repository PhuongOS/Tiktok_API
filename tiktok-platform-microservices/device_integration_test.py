"""
Device Service Integration Test

This script tests the complete end-to-end flow:
1. Auth Service - Register user and get token
2. TikTok Service - Create workspace
3. Device Service - Register device
4. Device Service - Connect device via WebSocket
5. Rule Engine - Create rule with DEVICE_CONTROL action
6. TikTok Service - Publish event
7. Verify - Device receives command via WebSocket

Usage:
    python device_integration_test.py
"""
import asyncio
import httpx
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Service URLs
AUTH_URL = "http://localhost:8001"
TIKTOK_URL = "http://localhost:8002"
RULE_ENGINE_URL = "http://localhost:8003"
DEVICE_URL = "http://localhost:8004"


async def test_device_integration():
    """Run complete integration test"""
    
    logger.info("=" * 60)
    logger.info("DEVICE SERVICE INTEGRATION TEST")
    logger.info("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Register user and login
        logger.info("\n[1/7] Registering user...")
        email = f"device_test_{datetime.now().timestamp()}@example.com"
        password = "testpass123"
        
        register_response = await client.post(
            f"{AUTH_URL}/api/auth/register",
            json={"email": email, "password": password}
        )
        assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
        logger.info(f"✅ User registered: {email}")
        
        # Login
        login_response = await client.post(
            f"{AUTH_URL}/api/auth/login",
            data={"username": email, "password": password}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        logger.info("✅ User logged in")
        
        # Step 2: Connect to TikTok livestream
        logger.info("\n[2/7] Connecting to TikTok livestream...")
        livestream_response = await client.post(
            f"{TIKTOK_URL}/api/livestreams/connect",
            json={"tiktok_input": "@device_test_user"},
            headers=headers
        )
        assert livestream_response.status_code == 201, f"Livestream connection failed: {livestream_response.text}"
        livestream_data = livestream_response.json()
        livestream_id = livestream_data["id"]
        workspace_id = livestream_id  # Use livestream_id as workspace_id
        headers["X-Workspace-ID"] = workspace_id
        logger.info(f"✅ Livestream connected: {livestream_id}")
        
        # Step 3: Register device
        logger.info("\n[3/7] Registering device...")
        device_response = await client.post(
            f"{DEVICE_URL}/api/devices",
            json={
                "name": "Test LED",
                "device_type": "arduino",
                "metadata": {"location": "office"}
            },
            headers=headers
        )
        assert device_response.status_code == 201, f"Device registration failed: {device_response.text}"
        device_data = device_response.json()
        device_id = device_data["id"]
        device_token = device_data["token"]
        logger.info(f"✅ Device registered: {device_id}")
        logger.info(f"   Token: {device_token[:16]}...")
        
        # Step 4: Create rule with DEVICE_CONTROL action
        logger.info("\n[4/7] Creating rule...")
        rule_response = await client.post(
            f"{RULE_ENGINE_URL}/api/rules",
            json={
                "name": "Device Control on Gift",
                "description": "Turn on LED when receiving Rose gift",
                "event_type": "gift",
                "logic_operator": "AND",
                "conditions": [
                    {"field": "gift_name", "operator": "==", "value": "Rose"}
                ],
                "actions": [
                    {
                        "action_type": "device_control",
                        "config": {
                            "workspace_id": workspace_id,
                            "device_id": device_id,
                            "command": "turn_on",
                            "params": {"brightness": 100}
                        }
                    }
                ]
            },
            headers=headers
        )
        assert rule_response.status_code == 201, f"Rule creation failed: {rule_response.text}"
        rule_id = rule_response.json()["id"]
        logger.info(f"✅ Rule created: {rule_id}")
        
        # Activate rule
        activate_response = await client.patch(
            f"{RULE_ENGINE_URL}/api/rules/{rule_id}/activate",
            headers=headers
        )
        assert activate_response.status_code == 200, f"Rule activation failed: {activate_response.text}"
        logger.info("✅ Rule activated")
        
        # Step 5: Connect device via WebSocket
        logger.info("\n[5/7] Connecting device via WebSocket...")
        ws_url = f"ws://localhost:8004/ws/device/{device_token}"
        
        received_commands = []
        
        async def device_websocket():
            """Simulate device WebSocket connection"""
            async with websockets.connect(ws_url) as websocket:
                logger.info("✅ Device connected via WebSocket")
                
                # Listen for commands
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        logger.info(f"📨 Device received: {data}")
                        
                        if "command_id" in data:
                            received_commands.append(data)
                            
                            # Send completion response
                            response = {
                                "command_id": data["command_id"],
                                "status": "completed",
                                "result": {"state": "on", "timestamp": datetime.utcnow().isoformat()}
                            }
                            await websocket.send(json.dumps(response))
                            logger.info("📤 Device sent completion response")
                            
                            # Exit after receiving command
                            break
                
                except websockets.exceptions.ConnectionClosed:
                    logger.info("🔌 WebSocket connection closed")
        
        # Start WebSocket connection in background
        ws_task = asyncio.create_task(device_websocket())
        
        # Wait for connection to establish
        await asyncio.sleep(2)
        
        # Step 6: Publish TikTok event
        logger.info("\n[6/7] Publishing TikTok event...")
        from redis.asyncio import Redis
        
        redis = Redis(host='localhost', port=6379, decode_responses=True)
        event_id = await redis.xadd(
            f'tiktok:events:{workspace_id}',
            {
                'event_type': 'gift',
                'gift_name': 'Rose',
                'username': 'TestUser',
                'diamond_count': '100'
            }
        )
        await redis.close()
        logger.info(f"✅ Event published: {event_id}")
        
        # Step 7: Wait for device to receive command
        logger.info("\n[7/7] Waiting for device to receive command...")
        
        try:
            await asyncio.wait_for(ws_task, timeout=10)
        except asyncio.TimeoutError:
            logger.error("❌ Timeout waiting for command")
            return False
        
        # Verify command was received
        if len(received_commands) > 0:
            command = received_commands[0]
            logger.info(f"✅ Device received command: {command['command_type']}")
            logger.info(f"   Parameters: {command.get('parameters', {})}")
            
            # Verify command in database
            await asyncio.sleep(2)  # Wait for DB update
            
            commands_response = await client.get(
                f"{DEVICE_URL}/api/devices/{device_id}/commands",
                headers=headers
            )
            assert commands_response.status_code == 200
            commands = commands_response.json()
            
            if len(commands) > 0:
                logger.info(f"✅ Command logged in database: {commands[0]['status']}")
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ INTEGRATION TEST PASSED!")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ No command received by device")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_device_integration())
    exit(0 if result else 1)
