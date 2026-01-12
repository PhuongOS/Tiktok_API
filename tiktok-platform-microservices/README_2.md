# 🚀 Realtime Event Processing System with ThingsBoard

## 📌 Mục tiêu

Cải tiến hệ thống xử lý sự kiện (ví dụ: quà tặng livestream có giá trị diamond khác nhau) theo hướng **realtime, chịu tải cao, không sập khi có vài nghìn người dùng đồng thời**.

Hệ thống đảm bảo:

* Phản hồi thời gian thực (low latency)
* Không mất sự kiện
* Dễ scale ngang (horizontal scaling)
* Phân tách rõ ràng giữa xử lý nghiệp vụ và IoT

---

## 🧠 Tổng quan kiến trúc

```
[Client / TikTok Event]
          ↓
     [Backend API]
          ↓
   [Message Queue]
          ↓
   [Worker / Processor]
          ↓
     [ThingsBoard]
          ↓
     [MQTT RPC]
          ↓
        [Device]
```

---

## 🔥 Nguyên tắc thiết kế

### ❌ Không làm

* Client kết nối trực tiếp ThingsBoard
* Xử lý logic nghiệp vụ trong ThingsBoard
* Dùng REST API cho realtime tải lớn

### ✅ Bắt buộc làm

* Backend xử lý toàn bộ logic
* Dùng Message Queue để chống burst traffic
* Giao tiếp với ThingsBoard bằng MQTT

---

## 🧩 Các thành phần chính

### 1️⃣ Backend API

**Nhiệm vụ**:

* Nhận event realtime (TikTok, Webhook, WebSocket...)
* Validate dữ liệu
* Chuẩn hóa event
* Đẩy event vào Queue

**Ví dụ payload chuẩn hóa**:

```json
{
  "event": "gift",
  "platform": "tiktok",
  "userId": "user_123",
  "giftName": "Motor",
  "diamond": 10,
  "quantity": 1,
  "timestamp": 1700000000000
}
```

---

### 2️⃣ Message Queue (BẮT BUỘC)

**Mục đích**:

* Chống quá tải khi traffic tăng đột biến
* Không mất sự kiện
* Scale worker độc lập

**Khuyến nghị**:

| Queue         | Khi dùng         |
| ------------- | ---------------- |
| Redis Streams | Nhẹ, realtime    |
| RabbitMQ      | Độ chính xác cao |
| Kafka         | Rất lớn          |
| NATS          | Siêu nhanh       |

---

### 3️⃣ Worker / Processor

**Nhiệm vụ**:

* Lấy event từ Queue
* Xử lý logic nghiệp vụ
* Quy đổi diamond → số vòng quay

**Ví dụ logic**:

```js
rounds = diamond * quantity
```

**Kết quả xử lý**:

```json
{
  "deviceId": "motor_01",
  "action": "rotate",
  "rounds": 10
}
```

---

### 4️⃣ ThingsBoard (IoT Layer)

**Vai trò**:

* Quản lý device
* Nhận telemetry / RPC
* Điều phối lệnh tới phần cứng

⚠️ **ThingsBoard KHÔNG xử lý logic nghiệp vụ**

---

### 5️⃣ Giao tiếp MQTT (RPC)

**Ưu điểm**:

* Kết nối persistent
* Latency rất thấp (10–20ms)
* Scale tốt

**Ví dụ MQTT RPC**:

```
Topic: v1/devices/me/rpc/request/123
Payload:
{
  "method": "rotate",
  "params": {
    "rounds": 10
  }
}
```

---

### 6️⃣ Phản hồi realtime cho client

**Cách khuyến nghị**:

```
Device → ThingsBoard → Rule Engine → Webhook → Backend → WebSocket → Client
```

❌ Không cho client subscribe trực tiếp ThingsBoard

---

## ⚖️ So sánh các phương án

| Phương án    | Realtime | Scale | Khuyến nghị          |
| ------------ | -------- | ----- | -------------------- |
| REST API     | ❌        | ❌     | Không dùng           |
| REST + Queue | ⚠        | ⚠     | Hệ nhỏ               |
| MQTT         | ✅        | ✅     | Tốt                  |
| MQTT + Queue | 🚀       | 🚀    | **Chuẩn production** |

---

## 🧱 Cấu hình ThingsBoard cho tải lớn

* MQTT over TCP (1883)
* Rule Engine async
* PostgreSQL tuning
* Redis cache
* Disable debug logs

---

## 📊 Hiệu năng thực tế (tham khảo)

* 3.000–5.000 user realtime
* 10.000–30.000 event/phút
* Latency: 50–150ms
* Không mất event

---

## 🛠️ Stack khuyến nghị

| Layer        | Công nghệ              |
| ------------ | ---------------------- |
| Backend API  | Fastify / NestJS       |
| Queue        | Redis Streams / BullMQ |
| Worker       | Node.js / Python       |
| MQTT Broker  | EMQX / Mosquitto       |
| IoT Platform | ThingsBoard            |
| Realtime     | Socket.IO              |
| Cache        | Redis                  |

---

## ✅ Kết luận

✔ Backend là trung tâm xử lý logic
✔ Message Queue là bắt buộc cho scale
✔ MQTT là lựa chọn tối ưu cho realtime
✔ ThingsBoard chỉ đóng vai trò IoT

---

📌 **Hệ thống này sẵn sàng mở rộng từ vài nghìn lên hàng chục nghìn user mà không cần thay đổi kiến trúc.**
