"""
Virtual Device Simulator for Testing

This script simulates an IoT device connecting to the Device Service via WebSocket.
It can receive commands and send back results.

Usage:
    python device_simulator.py --token YOUR_DEVICE_TOKEN
    
    Optional arguments:
    --host HOST          Device Service host (default: localhost)
    --port PORT          Device Service port (default: 8004)
    --name NAME          Device name for logging (default: Simulator)
"""
import asyncio
import websockets
import json
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DeviceSimulator")


class DeviceSimulator:
    """Virtual device simulator"""
    
    def __init__(self, token: str, host: str = "localhost", port: int = 8004, name: str = "Simulator"):
        self.token = token
        self.host = host
        self.port = port
        self.name = name
        self.ws_url = f"ws://{host}:{port}/ws/device/{token}"
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to Device Service"""
        try:
            logger.info(f"🔌 Connecting to {self.ws_url}...")
            self.websocket = await websockets.connect(self.ws_url)
            self.running = True
            logger.info(f"✅ Connected as {self.name}")
            
            # Start heartbeat task
            asyncio.create_task(self.send_heartbeat())
            
            # Listen for commands
            await self.listen_for_commands()
        
        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"❌ Connection failed: {e}")
            logger.error("Invalid token or server error")
        
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
    
    async def listen_for_commands(self):
        """Listen for commands from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"📨 Received: {data}")
                    
                    # Handle command
                    if "command_id" in data:
                        await self.handle_command(data)
                    
                    # Handle pong
                    elif data.get("type") == "pong":
                        logger.debug("💓 Heartbeat acknowledged")
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {message}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Connection closed by server")
            self.running = False
        
        except Exception as e:
            logger.error(f"❌ Error listening for commands: {e}")
            self.running = False
    
    async def handle_command(self, command: dict):
        """
        Handle a command from the server
        
        Simulates command execution and sends result back
        """
        command_id = command["command_id"]
        command_type = command["command_type"]
        parameters = command.get("parameters", {})
        
        logger.info(f"⚡ Executing command: {command_type}")
        logger.info(f"   Parameters: {parameters}")
        
        # Simulate command execution
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Simulate different command types
        if command_type == "turn_on":
            result = {"state": "on", "timestamp": datetime.utcnow().isoformat()}
            status = "completed"
            error = None
            logger.info("💡 Device turned ON")
        
        elif command_type == "turn_off":
            result = {"state": "off", "timestamp": datetime.utcnow().isoformat()}
            status = "completed"
            error = None
            logger.info("💡 Device turned OFF")
        
        elif command_type == "set_brightness":
            brightness = parameters.get("brightness", 100)
            result = {"brightness": brightness, "timestamp": datetime.utcnow().isoformat()}
            status = "completed"
            error = None
            logger.info(f"🔆 Brightness set to {brightness}%")
        
        elif command_type == "custom":
            result = {"message": "Custom command executed", "parameters": parameters}
            status = "completed"
            error = None
            logger.info("🔧 Custom command executed")
        
        else:
            result = None
            status = "failed"
            error = f"Unknown command type: {command_type}"
            logger.error(f"❌ {error}")
        
        # Send result back to server
        response = {
            "command_id": command_id,
            "status": status,
            "result": result,
            "error": error
        }
        
        await self.websocket.send(json.dumps(response))
        logger.info(f"📤 Sent result: {status}")
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to server"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                if self.websocket and not self.websocket.closed:
                    await self.websocket.send(json.dumps({"type": "ping"}))
                    logger.debug("💓 Heartbeat sent")
            
            except Exception as e:
                logger.error(f"❌ Heartbeat error: {e}")
                break
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("🔌 Disconnected")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Virtual Device Simulator")
    parser.add_argument("--token", required=True, help="Device authentication token")
    parser.add_argument("--host", default="localhost", help="Device Service host")
    parser.add_argument("--port", type=int, default=8004, help="Device Service port")
    parser.add_argument("--name", default="Simulator", help="Device name for logging")
    
    args = parser.parse_args()
    
    simulator = DeviceSimulator(
        token=args.token,
        host=args.host,
        port=args.port,
        name=args.name
    )
    
    try:
        await simulator.connect()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
        await simulator.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
