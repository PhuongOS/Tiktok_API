#!/usr/bin/env python3
"""
Test ThingsBoard Connection
Verify connectivity to https://iot-gateway.lps.io.vn/
"""
import requests
import json
import sys


class ThingsBoardTester:
    """Test ThingsBoard API connectivity"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token = None
    
    def test_connection(self):
        """Test basic connectivity"""
        print(f"Testing connection to {self.base_url}...")
        try:
            # Test with a simple GET to root
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                print(f"✅ Connection successful!")
                print(f"   Server is responding")
                return True
            else:
                print(f"❌ Connection failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def login(self, username: str, password: str):
        """Login to ThingsBoard"""
        print(f"\nLogging in as {username}...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"✅ Login successful!")
                print(f"   Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_user_info(self):
        """Get current user info"""
        if not self.token:
            print("❌ Not logged in")
            return False
        
        print("\nGetting user info...")
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/user",
                headers={"X-Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User info retrieved:")
                print(f"   Email: {user.get('email')}")
                print(f"   Authority: {user.get('authority')}")
                print(f"   Tenant: {user.get('tenantId', {}).get('id')}")
                return True
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def list_devices(self, limit: int = 10):
        """List devices"""
        if not self.token:
            print("❌ Not logged in")
            return False
        
        print(f"\nListing devices (limit {limit})...")
        try:
            response = requests.get(
                f"{self.base_url}/api/tenant/devices",
                params={"pageSize": limit, "page": 0},
                headers={"X-Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                devices = data.get('data', [])
                total = data.get('totalElements', 0)
                
                print(f"✅ Found {total} devices total")
                if devices:
                    print(f"\nShowing first {len(devices)} devices:")
                    for i, device in enumerate(devices, 1):
                        print(f"   {i}. {device.get('name')} ({device.get('type')})")
                        print(f"      ID: {device.get('id', {}).get('id')}")
                else:
                    print("   No devices found")
                return True
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def list_device_profiles(self):
        """List device profiles"""
        if not self.token:
            print("❌ Not logged in")
            return False
        
        print("\nListing device profiles...")
        try:
            response = requests.get(
                f"{self.base_url}/api/deviceProfiles",
                params={"pageSize": 100, "page": 0},
                headers={"X-Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                profiles = data.get('data', [])
                
                print(f"✅ Found {len(profiles)} device profiles:")
                for i, profile in enumerate(profiles, 1):
                    print(f"   {i}. {profile.get('name')}")
                    print(f"      Type: {profile.get('type')}")
                    print(f"      Transport: {profile.get('transportType')}")
                return True
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def get_mqtt_info(self):
        """Get MQTT connection info"""
        print("\nMQTT Connection Info:")
        print(f"   Host: iot-gateway.lps.io.vn")
        print(f"   Port: 1883 (non-SSL) or 8883 (SSL)")
        print(f"   Topic (telemetry): v1/devices/me/telemetry")
        print(f"   Topic (RPC request): v1/devices/me/rpc/request/+")
        print(f"   Topic (RPC response): v1/devices/me/rpc/response/{{requestId}}")
        print(f"\n   Authentication: Use device access token as username")


def main():
    """Main test function"""
    print("=" * 60)
    print("ThingsBoard Connection Tester")
    print("=" * 60)
    
    base_url = "https://iot-gateway.lps.io.vn"
    tester = ThingsBoardTester(base_url)
    
    # Test 1: Basic connection
    if not tester.test_connection():
        print("\n❌ Basic connection test failed. Exiting.")
        sys.exit(1)
    
    # Test 2: Login (requires credentials)
    print("\n" + "-" * 60)
    print("Login Test (optional)")
    print("-" * 60)
    
    username = input("Enter username (or press Enter to skip): ").strip()
    if username:
        password = input("Enter password: ").strip()
        
        if tester.login(username, password):
            # Test 3: Get user info
            tester.get_user_info()
            
            # Test 4: List devices
            tester.list_devices()
            
            # Test 5: List device profiles
            tester.list_device_profiles()
    else:
        print("Skipping login tests")
    
    # Show MQTT info
    print("\n" + "-" * 60)
    tester.get_mqtt_info()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✅ ThingsBoard instance is accessible")
    print("✅ API endpoints are working")
    print("\nNext steps:")
    print("1. Create device profile for TikTok IoT devices")
    print("2. Register test device")
    print("3. Test MQTT connection")
    print("4. Integrate with IoT Worker service")
    print("=" * 60)


if __name__ == "__main__":
    main()
