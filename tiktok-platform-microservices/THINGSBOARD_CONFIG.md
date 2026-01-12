# ThingsBoard Integration Configuration

**ThingsBoard Instance**: https://iot-gateway.lps.io.vn/  
**Date**: 2026-01-12  
**Status**: Existing Deployment

---

## 🔧 Configuration Details

### ThingsBoard Instance Info

**Base URL**: `https://iot-gateway.lps.io.vn`

**Endpoints:**
- Web UI: `https://iot-gateway.lps.io.vn`
- HTTP API: `https://iot-gateway.lps.io.vn/api`
- MQTT: `iot-gateway.lps.io.vn:1883` (or 8883 for SSL)
- WebSocket: `wss://iot-gateway.lps.io.vn/api/ws`

---

## 📋 Required Information

Để tích hợp, cần thu thập:

### 1. Authentication
- [ ] Admin username/password
- [ ] Tenant ID (nếu multi-tenant)
- [ ] API Token (hoặc tạo mới)

### 2. MQTT Configuration
- [ ] MQTT Port (1883 hoặc 8883)
- [ ] SSL/TLS enabled?
- [ ] MQTT Username/Password (nếu có)

### 3. Device Configuration
- [ ] Device Profile đã tồn tại?
- [ ] Device naming convention
- [ ] Telemetry keys đang dùng

---

## 🚀 Integration Steps

### Step 1: Tạo Service Account

```bash
# Login to ThingsBoard
curl -X POST https://iot-gateway.lps.io.vn/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
  }'

# Response: {"token": "eyJhbGc..."}
```

### Step 2: Tạo Device Profile

**Via UI:**
1. Login: https://iot-gateway.lps.io.vn
2. Device Profiles → Add Device Profile
3. Name: "TikTok IoT Device"
4. Transport: MQTT
5. Add Telemetry: `rounds_completed`, `status`, `error`
6. Add RPC Methods: `rotate`, `turn_on`, `turn_off`

**Via API:**
```bash
curl -X POST https://iot-gateway.lps.io.vn/api/deviceProfile \
  -H "X-Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TikTok IoT Device",
    "type": "DEFAULT",
    "transportType": "MQTT",
    "provisionType": "DISABLED",
    "profileData": {
      "configuration": {"type": "DEFAULT"},
      "transportConfiguration": {"type": "MQTT"}
    }
  }'
```

### Step 3: Tạo Device

```bash
curl -X POST https://iot-gateway.lps.io.vn/api/device \
  -H "X-Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Motor_01",
    "type": "Motor",
    "label": "TikTok Motor 1"
  }'

# Response: {"id": {"id": "device-uuid"}}
```

### Step 4: Lấy Device Credentials

```bash
curl -X GET https://iot-gateway.lps.io.vn/api/device/{deviceId}/credentials \
  -H "X-Authorization: Bearer $TOKEN"

# Response: {"credentialsType": "ACCESS_TOKEN", "credentialsId": "YOUR_DEVICE_TOKEN"}
```

---

## 🔌 IoT Worker Configuration

### Environment Variables

```bash
# .env file for IoT Worker
THINGSBOARD_URL=https://iot-gateway.lps.io.vn
THINGSBOARD_MQTT_HOST=iot-gateway.lps.io.vn
THINGSBOARD_MQTT_PORT=1883
THINGSBOARD_MQTT_SSL=false
THINGSBOARD_API_TOKEN=YOUR_API_TOKEN

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_STREAM_IOT_COMMANDS=iot:commands:{workspace_id}

LOG_LEVEL=INFO
```

### Config File

```yaml
# config/thingsboard.yaml
thingsboard:
  url: https://iot-gateway.lps.io.vn
  mqtt:
    host: iot-gateway.lps.io.vn
    port: 1883
    ssl: false
    keepalive: 60
    qos: 1
  api:
    token: ${THINGSBOARD_API_TOKEN}
    timeout: 30

redis:
  host: localhost
  port: 6379
  db: 0
  streams:
    iot_commands: "iot:commands:{workspace_id}"
    iot_responses: "iot:responses:{workspace_id}"

processing:
  workers: 4
  batch_size: 100
  retry_attempts: 3
  retry_delay: 1000
```

---

## 📝 Device Registration Flow

### 1. Via Admin Panel UI (Future)

```
User creates device in Admin Panel
  ↓
POST /api/devices
  ↓
Backend creates device in ThingsBoard
  ↓
Store device_id + thingsboard_token in database
  ↓
Return device info to user
```

### 2. Via API

```python
# Example: Register device
import requests

# Step 1: Create device in Platform
device_data = {
    "name": "Motor 01",
    "type": "motor",
    "workspace_id": "workspace-123"
}
response = requests.post(
    "http://localhost:8004/api/devices",
    json=device_data,
    headers={"Authorization": f"Bearer {jwt_token}"}
)
device = response.json()

# Step 2: Link to ThingsBoard
link_data = {
    "thingsboard_name": "Motor_01",
    "thingsboard_type": "Motor"
}
response = requests.post(
    f"http://localhost:8004/api/devices/{device['id']}/thingsboard/link",
    json=link_data,
    headers={"Authorization": f"Bearer {jwt_token}"}
)

# Device is now linked!
```

---

## 🧪 Testing MQTT Connection

### Test 1: Publish Telemetry

```bash
# Install mosquitto clients
brew install mosquitto  # macOS
# or
apt-get install mosquitto-clients  # Linux

# Publish telemetry
mosquitto_pub \
  -h iot-gateway.lps.io.vn \
  -p 1883 \
  -t v1/devices/me/telemetry \
  -u "YOUR_DEVICE_TOKEN" \
  -m '{"temperature": 25.5, "status": "online"}'
```

### Test 2: Subscribe to RPC

```bash
# Subscribe to RPC requests
mosquitto_sub \
  -h iot-gateway.lps.io.vn \
  -p 1883 \
  -t v1/devices/me/rpc/request/+ \
  -u "YOUR_DEVICE_TOKEN"
```

### Test 3: Send RPC Command

```bash
# Via ThingsBoard API
curl -X POST https://iot-gateway.lps.io.vn/api/rpc/oneway/{deviceId} \
  -H "X-Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "rotate",
    "params": {"rounds": 10, "speed": 100}
  }'
```

---

## 🔐 Security Considerations

### 1. SSL/TLS for MQTT

Nếu ThingsBoard hỗ trợ MQTT over SSL (port 8883):

```python
import paho.mqtt.client as mqtt
import ssl

client = mqtt.Client()
client.tls_set(
    ca_certs=None,
    certfile=None,
    keyfile=None,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.username_pw_set("DEVICE_TOKEN")
client.connect("iot-gateway.lps.io.vn", 8883, 60)
```

### 2. API Token Security

```python
# Store in environment variables
import os
THINGSBOARD_TOKEN = os.getenv("THINGSBOARD_API_TOKEN")

# Or use secrets manager
from azure.keyvault.secrets import SecretClient
secret = client.get_secret("thingsboard-token")
```

---

## 📊 Monitoring Setup

### 1. ThingsBoard Webhooks

Create webhook để nhận device responses:

```
Rule Chain: Root Rule Chain
  ↓
Rule Node: REST API Call
  ↓
Endpoint: https://api.platform.com/webhooks/thingsboard/telemetry
Method: POST
Headers: {"Authorization": "Bearer SECRET"}
```

### 2. Metrics Collection

```python
# In IoT Worker
from prometheus_client import Counter, Histogram

mqtt_messages_sent = Counter('mqtt_messages_sent_total', 'Total MQTT messages sent')
mqtt_latency = Histogram('mqtt_publish_latency_seconds', 'MQTT publish latency')

# Usage
mqtt_messages_sent.inc()
with mqtt_latency.time():
    client.publish(topic, payload)
```

---

## 🚀 Quick Start Guide

### 1. Get ThingsBoard Credentials

```bash
# Login and get token
TB_TOKEN=$(curl -s -X POST https://iot-gateway.lps.io.vn/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USER","password":"YOUR_PASS"}' \
  | jq -r '.token')

echo "Token: $TB_TOKEN"
```

### 2. Create Test Device

```bash
# Create device
DEVICE_ID=$(curl -s -X POST https://iot-gateway.lps.io.vn/api/device \
  -H "X-Authorization: Bearer $TB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test_Motor","type":"Motor"}' \
  | jq -r '.id.id')

echo "Device ID: $DEVICE_ID"

# Get credentials
DEVICE_TOKEN=$(curl -s -X GET https://iot-gateway.lps.io.vn/api/device/$DEVICE_ID/credentials \
  -H "X-Authorization: Bearer $TB_TOKEN" \
  | jq -r '.credentialsId')

echo "Device Token: $DEVICE_TOKEN"
```

### 3. Test MQTT

```bash
# Publish test telemetry
mosquitto_pub \
  -h iot-gateway.lps.io.vn \
  -p 1883 \
  -t v1/devices/me/telemetry \
  -u "$DEVICE_TOKEN" \
  -m '{"test": true, "timestamp": '$(date +%s)'}'

# Check in ThingsBoard UI
# https://iot-gateway.lps.io.vn/devices → Latest Telemetry
```

---

## 📋 Next Steps

1. **Gather Information:**
   - [ ] ThingsBoard admin credentials
   - [ ] MQTT port configuration
   - [ ] Existing device profiles

2. **Setup IoT Worker:**
   - [ ] Create service structure
   - [ ] Configure ThingsBoard connection
   - [ ] Test MQTT connectivity

3. **Integration Testing:**
   - [ ] Create test device
   - [ ] Send test commands
   - [ ] Verify responses

4. **Production Deployment:**
   - [ ] SSL/TLS configuration
   - [ ] Monitoring setup
   - [ ] Load testing

---

## 🔗 Useful Links

- ThingsBoard Docs: https://thingsboard.io/docs/
- MQTT API: https://thingsboard.io/docs/reference/mqtt-api/
- REST API: https://thingsboard.io/docs/reference/rest-api/
- Your Instance: https://iot-gateway.lps.io.vn/

---

**Ready to start integration!** 🚀
