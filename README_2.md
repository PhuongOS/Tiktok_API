# TikTok LIVE Realtime Interaction Platform

> Nền tảng SaaS realtime cho phép **nhiều người dùng** kết nối livestream TikTok của họ, tracking comment / gift / event và **điều khiển phần cứng (Arduino / ESP32)** với độ trễ thấp.

---

## 1. Mục tiêu sản phẩm (Product Vision)

* Cho phép **bất kỳ streamer nào** kết nối live TikTok chỉ bằng link / username
* Tạo rule: *comment → hành động vật lý*
* Realtime, ổn định, scale được cho nhiều người dùng
* Đóng gói dưới dạng **SaaS + Edge Agent**

Ví dụ:

* Comment `spin` → motor quay
* Gift `rose` → bật đèn
* 100 comment → kích hoạt camera

---

## 2. Mô hình triển khai tổng thể

### 2.1 Kiến trúc được chọn

👉 **Hybrid Client–Server + Microservice**

* **Cloud (Server)**: xử lý TikTok, rule, user, realtime
* **Edge Client (máy user)**: kết nối phần cứng

Không điều khiển phần cứng trực tiếp từ cloud.

---

## 3. Kiến trúc hệ thống (High-level Architecture)

```
                    ┌────────────────────┐
                    │   Load Balancer    │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ API Gateway  │     │ API Gateway  │     │ API Gateway  │
│ (Stateless)  │     │ (Stateless)  │     │ (Stateless)  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────┐
│            Auth / User / Workspace / Billing            │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│         Live Connector Pool (TikTokLive)                │
│       (1 livestream = 1 async worker)                   │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│            Event Bus (Redis Streams / NATS)             │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│                   Rule Engine                           │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│        Realtime Command Service (WS / MQTT)             │
└────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   Edge Client App  │
                    │ (Local Machine)   │
                    └─────────┬──────────┘
                              ▼
                      Arduino / ESP32
```

---

## 4. Phân tách trách nhiệm

### 4.1 Cloud Server

* Đăng ký / đăng nhập
* Quản lý user, workspace
* Kết nối TikTok LIVE
* Xử lý rule & anti-spam
* Realtime event routing
* Billing & quota

📌 Cloud **không truy cập phần cứng**.

---

### 4.2 Edge Client (Agent)

* Chạy trên máy user (Windows / macOS / Linux)
* Login bằng **Agent Token**
* Kết nối WebSocket / MQTT tới cloud
* Điều khiển:

  * Arduino (USB Serial)
  * ESP32 (MQTT)
* Kill-switch & safety

📌 Edge client **không xử lý TikTok**.

---

## 5. Realtime Flow

```
TikTok Comment
   ↓
Live Connector (~100ms)
   ↓
Event Bus (~5ms)
   ↓
Rule Engine (~10ms)
   ↓
Command Service
   ↓
WebSocket / MQTT (~20ms)
   ↓
Edge Client
   ↓
Hardware (1–5ms)
```

➡️ Tổng latency trung bình: **< 200ms**

---

## 6. Microservices chi tiết

### 6.1 API Gateway

* Stateless
* JWT authentication
* Rate limit

API ví dụ:

```
POST /auth/login
POST /live/connect
POST /live/disconnect
GET  /live/status
```

---

### 6.2 Live Connector Service

* Dùng `TikTokLive`
* Mỗi livestream = 1 worker
* Chuẩn hóa event JSON

Event mẫu:

```json
{
  "workspace_id": "ws_01",
  "stream_id": "live_abc",
  "event_type": "comment",
  "payload": { "text": "spin" },
  "ts": 1700000000
}
```

---

### 6.3 Event Bus

* Redis Streams (MVP)
* NATS / Kafka (scale)

Topic mẫu:

```
stream:tiktok:live_abc
```

---

### 6.4 Rule Engine

* Subscribe event bus
* Áp rule theo user
* Cooldown / throttle

Rule mẫu:

```json
{
  "when": { "event": "comment", "contains": "spin" },
  "then": { "command": "MOTOR_SPIN", "duration": 1000 }
}
```

---

### 6.5 Realtime Command Service

* WebSocket (local agent)
* MQTT (ESP32)

Command mẫu:

```json
{
  "device_id": "arduino_01",
  "cmd": "LED_ON"
}
```

---

## 7. Lưu trữ dữ liệu (Multi-tenant)

### 7.1 Database chính – PostgreSQL

```sql
users(id, email, password_hash)
workspaces(id, owner_id)
livestreams(id, workspace_id)
rules(id, livestream_id)
devices(id, workspace_id)
```

📌 `workspace_id` = tenant boundary

---

### 7.2 Dữ liệu realtime

* Comment / gift: **KHÔNG lưu DB**
* Xử lý trong memory / stream

---

## 8. Authentication & Security

* JWT cho Web UI
* Refresh token
* Agent token cho Edge Client
* Revoke agent token khi cần

---

## 9. Load Balancing & Scaling

* NGINX / Cloud Load Balancer
* API stateless → scale ngang
* Live Connector auto-scale
* Redis Cluster / NATS

---

## 10. Đóng gói sản phẩm (Product Packaging)

### Cloud SaaS

* Web dashboard
* Rule builder
* Live monitoring

### Edge Client

* Installer
* Auto reconnect
* Auto update

---

## 11. Lộ trình phát triển

### Phase 1 – MVP

* 1 server
* Redis + Postgres
* Arduino USB

### Phase 2 – Scale

* MQTT + ESP32
* Multi user
* Auto scale

### Phase 3 – Commercial

* Billing
* Preset mini-game
* Multi platform

---

## 12. Kết luận

Hệ thống được thiết kế theo:

* Event-driven
* Cloud-controlled
* Edge-executed
* Multi-tenant SaaS

➡️ Phù hợp triển khai **sản phẩm thương mại**, không phải demo.

---

*End of README*

---

## 🔐 User & Permission Management (RBAC + Workspace)

### 🎯 Design Goals

* Đảm bảo **an toàn tuyệt đối cho thiết bị phần cứng**
* Hỗ trợ **multi-user, multi-team (multi-tenant)**
* Phù hợp để triển khai **SaaS thương mại**

> Nguyên tắc cốt lõi: **KHÔNG phân quyền theo user đơn lẻ – phân quyền theo Workspace (Tenant)**

---

### 🧩 Workspace Model

```
User ── belongs to ── Workspace ── owns ── Resources
```

**Resources trong mỗi Workspace:**

* Livestream TikTok
* Rule Engine
* Thiết bị phần cứng (Arduino / ESP32)
* Edge Client (Agent)

Mỗi Workspace là **ranh giới bảo mật tuyệt đối** giữa các user.

---

### 🎭 Role-Based Access Control (RBAC)

| Role     | Quyền                                    |
| -------- | ---------------------------------------- |
| Owner    | Toàn quyền (billing, device, rule, user) |
| Admin    | Quản lý live, rule, device               |
| Operator | Bật / tắt rule                           |
| Viewer   | Chỉ xem dashboard                        |

---

### 🗂 Permission Matrix (đề xuất)

| Action                | Owner | Admin | Operator | Viewer |
| --------------------- | ----- | ----- | -------- | ------ |
| Connect TikTok Live   | ✅     | ✅     | ❌        | ❌      |
| Create / Edit Rule    | ✅     | ✅     | ❌        | ❌      |
| Enable / Disable Rule | ✅     | ✅     | ✅        | ❌      |
| Register Device       | ✅     | ✅     | ❌        | ❌      |
| View Logs             | ✅     | ✅     | ✅        | ✅      |

---

### 🔐 3-Tier Security Model

#### 1️⃣ API Layer (Backend)

* Authentication bằng **JWT**
* Mỗi request phải xác minh:

  * user_id
  * workspace_id
  * role & permission

```
JWT → Workspace → Role → Permission
```

---

#### 2️⃣ Realtime Command Layer

> ⚠️ User **KHÔNG BAO GIỜ** gửi lệnh trực tiếp xuống phần cứng

Luồng chuẩn:

```
User UI → API → Rule Engine → Event Bus → Hardware Gateway
```

Rule Engine là **điểm duy nhất** được phép phát command.

---

#### 3️⃣ Edge Client / Hardware Layer

Edge Client (máy local hoặc thiết bị nhúng):

* Không tin cloud tuyệt đối
* Tự xác minh:

  * workspace_id
  * device_id
  * command allow-list
  * rate limit

Ví dụ command payload:

```json
{
  "workspace_id": "ws_01",
  "device_id": "arduino_01",
  "cmd": "MOTOR_SPIN",
  "duration_ms": 500
}
```

---

### 🔑 Agent Token (Bảo mật phần cứng)

❌ Không dùng user JWT cho thiết bị

✅ Sử dụng **Agent Token**:

* Gắn với **1 device + 1 workspace**
* Không đăng nhập UI
* Có thể revoke bất kỳ lúc nào

**Flow đăng ký thiết bị:**

```
Owner tạo device
 → Server sinh agent_token
 → User nhập token vào Edge Client
 → Edge Client kết nối cloud
```

---

### 🧯 Safety & Anti-Abuse

* Kill-switch: Owner tắt toàn bộ hardware
* Rule cooldown (anti-spam)
* Rate limit command
* Audit log:

  * ai
  * khi nào
  * rule nào
  * device nào

---

### 🗄 Database Schema (RBAC Core)

```sql
users(id, email, password_hash)

workspaces(id, owner_id)

workspace_members(
  workspace_id,
  user_id,
  role
)

devices(id, workspace_id)

agent_tokens(
  device_id,
  token_hash,
  revoked
)
```

---

### ✅ Key Takeaways

* Workspace = Tenant boundary
* RBAC đơn giản nhưng đủ mạnh
* Rule Engine là **trung tâm quyền lực**
* Phần cứng luôn ở chế độ **zero-trust**

Kiến trúc này đảm bảo hệ thống **an toàn – realtime – scale tốt – sẵn sàng thương mại hóa**.
