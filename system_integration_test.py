import asyncio
import httpx
import uuid
import time
from datetime import datetime

# Configuration
AUTH_URL = "http://localhost:8001/api"
TIKTOK_URL = "http://localhost:8002/api"
RULE_URL = "http://localhost:8003/api"

async def test_services():
    print("🚀 Starting System Integration Test")
    print("====================================")
    
    async with httpx.AsyncClient() as client:
        # 1. Health Checks
        print("\n🏥 Checking Service Health...")
        services = {
            "Auth": "http://localhost:8001/health",
            "TikTok": "http://localhost:8002/health",
            "Rule": "http://localhost:8003/health"
        }
        
        for name, url in services.items():
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    print(f"✅ {name} Service is UP ({resp.json()})")
                else:
                    print(f"❌ {name} Service returned {resp.status_code}")
                    return
            except Exception as e:
                print(f"❌ {name} Service is DOWN: {e}")
                return

        # 2. Auth Flow
        print("\n🔐 Testing Auth Flow...")
        unique_id = str(uuid.uuid4())[:8]
        email = f"user_{unique_id}@test.com"
        password = "password123"
        
        # Register
        register_data = {
            "email": email,
            "password": password,
            "full_name": "Test Runner"
        }
        resp = await client.post(f"{AUTH_URL}/auth/register", json=register_data)
        if resp.status_code in [200, 201]:
            print(f"✅ Registered user: {email}")
        else:
            print(f"❌ Registration failed: {resp.text}")
            return

        # Login
        # OAuth2PasswordRequestForm expects form data with 'username' and 'password'
        login_data = {"username": email, "password": password}
        resp = await client.post(f"{AUTH_URL}/auth/login", data=login_data)
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print(f"✅ Login successful. Token obtained.")
        else:
            print(f"❌ Login failed: {resp.text}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # Create Workspace
        workspace_data = {
            "name": f"Test Workspace {unique_id}",
            "description": "Integration testing workspace"
        }
        resp = await client.post(f"{AUTH_URL}/workspaces", json=workspace_data, headers=headers)
        if resp.status_code in [200, 201]:
            workspace = resp.json()
            workspace_id = workspace["id"]
            print(f"✅ Created Workspace: {workspace['name']} (ID: {workspace_id})")
            
            # Update headers with Workspace ID for subsequent requests (especially Rule Engine)
            headers["X-Workspace-ID"] = workspace_id
        else:
            print(f"❌ Create workspace failed: {resp.text}")
            return

        # 3. TikTok Flow
        print("\n📺 Testing TikTok Flow...")
        # Connecting to a generic verified user just to test the connection flow (might fail if not live, but service should respond)
        # Using a username that is likely offline or random to test the 'connecting' state or 'offline' response safely
        # Or we use the @boss001735 from the README if we want to try a real connection, but safer to just test the API logic.
        tiktok_input = "@tiktok" 
        
        connect_data = {"tiktok_input": tiktok_input}
        resp = await client.post(f"{TIKTOK_URL}/livestreams/connect", json=connect_data)
        
        # Note: Depending on the implementation, this might return 200 even if offline, or error.
        # We just want to ensure the API accepts the request.
        if resp.status_code in [200, 201]:
            livestream = resp.json()
            livestream_id = livestream["id"]
            print(f"✅ Connected request sent for {tiktok_input}. ID: {livestream_id}")
            print(f"   Status: {livestream.get('status')}")
            
            # Get Details
            resp = await client.get(f"{TIKTOK_URL}/livestreams/{livestream_id}")
            if resp.status_code == 200:
                print(f"✅ Retrieved Livestream Details")
        else:
            print(f"⚠️ TikTok connection note: {resp.text} (This is expected if not actually live or scraping fails)")

        # 4. Rule Engine Flow
        print("\n⚙️  Testing Rule Engine Flow...")
        rule_data = {
            "name": f"Test Rule {unique_id}",
            "description": "Integration test rule",
            "event_type": "gift",
            "workspace_id": workspace_id, # Manually adding in case it is required as per previous debugging
            "created_by": email,
            "logic_operator": "AND",
            "conditions": [
                {
                    "field": "diamond_count",
                    "operator": ">",
                    "value": "10",
                    "order": 0
                }
            ],
            "actions": [
                {
                    "action_type": "log",
                    "config": {"message": "Test message"},
                    "order": 0
                }
            ]
        }
        
        resp = await client.post(f"{RULE_URL}/rules", json=rule_data, headers=headers)
        if resp.status_code in [200, 201]:
            rule = resp.json()
            rule_id = rule["id"]
            print(f"✅ Created Rule: {rule['name']} (ID: {rule_id})")
            
            # List Rules
            resp = await client.get(f"{RULE_URL}/rules?workspace_id={workspace_id}", headers=headers)
            if resp.status_code == 200:
                rules = resp.json()
                print(f"✅ Listed Rules. Count: {len(rules)}")
            else:
                print(f"❌ List rules failed: {resp.text}")
                
            # Activate Rule
            resp = await client.patch(f"{RULE_URL}/rules/{rule_id}/activate", headers=headers)
            if resp.status_code == 200:
                print(f"✅ Activated Rule")
            else:
                print(f"❌ Activate rule failed: {resp.text}")
                return

            # 5. Verify Event Processing (Redis)
            print("\n⚡ Testing Event Processing...")
            import redis.asyncio as redis
            r = redis.from_url("redis://localhost:6379", decode_responses=True)
            
            # Publish event manually to Redis Stream
            stream_key = f"tiktok:events:{workspace_id}"
            event_data = {
                "event_type": "gift",
                "diamond_count": "100",  # > 10 condition
                "gift_name": "Rose",
                "username": "tester",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Wait for consumer to pick up the new workspace (polling interval is 5s)
            print("⏳ Waiting 6s for Consumer to pick up new workspace...")
            await asyncio.sleep(6)
            
            print(f"📤 Publishing event to {stream_key}...")
            await r.xadd(stream_key, event_data)
            await r.close()
            
            # Poll for execution
            print("⏳ Waiting for rule execution...")
            for i in range(10):
                await asyncio.sleep(1)
                resp = await client.get(f"{RULE_URL}/rules/{rule_id}/executions", headers=headers) # Using correct headers for auth if needed, but here we mocked it in API
                # Actually API uses header? No, 'get_current_workspace' is TODO hardcoded.
                if resp.status_code == 200:
                    executions = resp.json()
                    if executions:
                        ex = executions[0]
                        print(f"✅ Rule Executed! Status: {ex['status']}")
                        print(f"   Event ID: {ex['event_id']}")
                        if ex['status'] == 'failed':
                            print(f"   Error: {ex.get('error_message')}")
                        break
                else:
                    print(f"⚠️ Check failed: {resp.status_code}")
            else:
                print("❌ Rule did not execute in time")

        else:
            print(f"❌ Create rule failed: {resp.text}")


    print("\n✅ System Integration Test Complete!")
    print("====================================")

if __name__ == "__main__":
    asyncio.run(test_services())
