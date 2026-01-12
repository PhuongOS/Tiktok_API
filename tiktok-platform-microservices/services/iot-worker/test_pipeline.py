#!/usr/bin/env python3
"""
End-to-End Pipeline Test
Tests the complete flow: Redis → IoT Worker → ThingsBoard → Device
"""
import redis
import json
import time
import sys

def test_pipeline():
    """Test the complete event processing pipeline"""
    
    print("=" * 60)
    print("End-to-End Pipeline Test")
    print("=" * 60)
    
    # Connect to Redis
    print("\n1. Connecting to Redis...")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")
        sys.exit(1)
    
    # Stream key
    stream_key = "iot:commands:workspace-123"
    
    # Test Event 1: Gift Event (Rose x10)
    print(f"\n2. Publishing test gift event to {stream_key}...")
    
    gift_event = {
        "type": "gift",
        "data": json.dumps({
            "type": "gift",
            "user": {
                "unique_id": "test_user",
                "nickname": "Test User"
            },
            "gift": {
                "name": "Rose",
                "diamond_count": 1
            },
            "repeat_count": 10,
            "workspace_id": "workspace-123",
            "livestream_id": "livestream-test"
        })
    }
    
    try:
        message_id = r.xadd(stream_key, gift_event)
        print(f"✅ Published gift event (ID: {message_id})")
        print(f"   Gift: Rose x10 (10 diamonds)")
        print(f"   Expected: Motor rotate 10 rounds @ 100 RPM")
    except Exception as e:
        print(f"❌ Failed to publish event: {str(e)}")
        sys.exit(1)
    
    # Test Event 2: Gift Event (Lion x5)
    print(f"\n3. Publishing second test event...")
    
    lion_event = {
        "type": "gift",
        "data": json.dumps({
            "type": "gift",
            "user": {
                "unique_id": "test_user2",
                "nickname": "Test User 2"
            },
            "gift": {
                "name": "Lion",
                "diamond_count": 10
            },
            "repeat_count": 5,
            "workspace_id": "workspace-123",
            "livestream_id": "livestream-test"
        })
    }
    
    try:
        message_id = r.xadd(stream_key, lion_event)
        print(f"✅ Published gift event (ID: {message_id})")
        print(f"   Gift: Lion x5 (50 diamonds)")
        print(f"   Expected: Motor rotate 500 rounds")
    except Exception as e:
        print(f"❌ Failed to publish event: {str(e)}")
    
    # Check stream length
    print(f"\n4. Checking stream status...")
    try:
        stream_length = r.xlen(stream_key)
        print(f"✅ Stream '{stream_key}' has {stream_length} messages")
    except Exception as e:
        print(f"❌ Error checking stream: {str(e)}")
    
    # Instructions
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Start IoT Worker service:")
    print("   cd services/iot-worker")
    print("   ./start.sh")
    print("")
    print("2. Watch the logs to see events being processed")
    print("")
    print("3. Check ThingsBoard for device telemetry:")
    print("   https://iot-gateway.lps.io.vn")
    print("")
    print("4. Verify device received commands")
    print("=" * 60)


if __name__ == "__main__":
    test_pipeline()
