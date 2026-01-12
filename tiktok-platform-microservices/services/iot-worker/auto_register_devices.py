#!/usr/bin/env python3
"""
Device Auto-Registration Script
Automatically creates devices in ThingsBoard based on configuration
"""
import sys
sys.path.insert(0, '.')

from app.thingsboard_client import ThingsBoardClient
from app.config import config
import json


def auto_register_devices():
    """Auto-register devices in ThingsBoard"""
    
    print("=" * 60)
    print("Device Auto-Registration")
    print("=" * 60)
    
    # Device configurations
    devices_config = [
        {
            "name": "motor_01",
            "type": "Motor",
            "label": "TikTok Motor 1",
            "description": "Motor controlled by TikTok gifts"
        },
        {
            "name": "led_strip_01",
            "type": "LED",
            "label": "TikTok LED Strip 1",
            "description": "LED strip controlled by TikTok comments"
        },
        {
            "name": "servo_01",
            "type": "Servo",
            "label": "TikTok Servo 1",
            "description": "Servo motor for special effects"
        }
    ]
    
    # Connect to ThingsBoard
    print("\n1. Connecting to ThingsBoard...")
    client = ThingsBoardClient(
        base_url=config.THINGSBOARD_URL,
        username=config.THINGSBOARD_USERNAME,
        password=config.THINGSBOARD_PASSWORD
    )
    
    if not client.login():
        print("❌ Failed to login to ThingsBoard")
        sys.exit(1)
    
    print(f"✅ Logged in as {config.THINGSBOARD_USERNAME}")
    print(f"   Tenant ID: {client.tenant_id}")
    
    # Get existing devices
    print("\n2. Checking existing devices...")
    existing_devices = client.list_devices()
    existing_names = {d.get('name') for d in existing_devices}
    print(f"✅ Found {len(existing_devices)} existing devices")
    
    # Register devices
    print("\n3. Registering devices...")
    registered = []
    
    for device_config in devices_config:
        device_name = device_config['name']
        
        if device_name in existing_names:
            print(f"⏭️  Device '{device_name}' already exists, skipping")
            continue
        
        print(f"\n   Creating device: {device_name}")
        device = client.create_device(
            name=device_name,
            device_type=device_config['type'],
            label=device_config['label']
        )
        
        if device:
            device_id = device.get('id', {}).get('id')
            print(f"   ✅ Created device: {device_name}")
            print(f"      ID: {device_id}")
            
            # Get credentials
            token = client.get_device_credentials(device_id)
            if token:
                print(f"      Token: {token[:20]}...")
                
                registered.append({
                    "name": device_name,
                    "id": device_id,
                    "token": token,
                    "type": device_config['type']
                })
            else:
                print(f"      ⚠️  Failed to get credentials")
        else:
            print(f"   ❌ Failed to create device: {device_name}")
    
    # Save device tokens to file
    if registered:
        print("\n4. Saving device tokens...")
        tokens_file = "device_tokens.json"
        
        with open(tokens_file, 'w') as f:
            json.dump(registered, f, indent=2)
        
        print(f"✅ Saved {len(registered)} device tokens to {tokens_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total devices registered: {len(registered)}")
    for device in registered:
        print(f"  - {device['name']} ({device['type']})")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Update gift processor mappings to use these device IDs")
    print("2. Configure physical devices with the tokens")
    print("3. Test MQTT connection from devices")
    print("4. Start IoT Worker service")
    print("=" * 60)


if __name__ == "__main__":
    auto_register_devices()
