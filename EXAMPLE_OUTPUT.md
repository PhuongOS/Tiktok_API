# Example Output: TikTok Livestream Data Capture

## Khi User ĐANG LIVE

```
============================================================
TikTok Livestream Data Capture Tool
============================================================

Enter TikTok username (without @): charlidamelio
Capture duration in seconds (default 60): 30

🔍 Checking if @charlidamelio is live...
✅ @charlidamelio is LIVE! Connecting...
⏱️ Will capture events for 30 seconds

============================================================
🟢 CONNECTED to @charlidamelio
Room ID: 7123456789012345678
============================================================

👥 @user123 joined the stream
💬 Comment from @user456: "Love your stream!"
❤️ Like from @user789 (x5)
🎁 Gift from @superfan: Rose x10 (Total: 10 diamonds)
💬 Comment from @newbie: "First time here! 👋"
👥 @another_user joined the stream
⭐ @fan123 followed the streamer!
💬 Comment from @regular: "Amazing content as always"
🎁 Gift from @bigspender: TikTok Universe (5000 diamonds)
❤️ Like from @user456 (x20)
📤 @supporter shared the stream!
💬 Comment from @viewer: "Can you do a dance?"
👥 @newviewer joined the stream
💬 Comment from @fan: "You're the best! 💖"
🎁 Gift from @generous: Rose x50 (Total: 50 diamonds)
❤️ Like from @liker (x15)
💬 Comment from @question: "What song is this?"
👥 @latecomer joined the stream
⭐ @newfan followed the streamer!

============================================================
📊 EVENT SUMMARY
============================================================

Total events captured: 45

Breakdown by type:
  comment: 15
  connect: 1
  follow: 3
  gift: 8
  join: 12
  like: 5
  share: 1

============================================================

💾 Events saved to livestream_events.json
```

## Khi User KHÔNG LIVE

```
============================================================
TikTok Livestream Data Capture Tool
============================================================

Enter TikTok username (without @): boss001735
Capture duration in seconds (default 60): 30

🔍 Checking if @boss001735 is live...
❌ @boss001735 is not currently live
```

---

## File Output: livestream_events.json

```json
[
  {
    "event_type": "connect",
    "data": {
      "unique_id": "charlidamelio",
      "room_id": "7123456789012345678",
      "timestamp": "2026-01-12T09:30:00.123456"
    }
  },
  {
    "event_type": "join",
    "data": {
      "user": {
        "unique_id": "user123",
        "nickname": "John Doe",
        "user_id": "123456789"
      },
      "timestamp": "2026-01-12T09:30:01.234567"
    }
  },
  {
    "event_type": "comment",
    "data": {
      "user": {
        "unique_id": "user456",
        "nickname": "Jane Smith",
        "user_id": "987654321",
        "profile_picture": "https://p16-sign-sg.tiktokcdn.com/..."
      },
      "comment": "Love your stream!",
      "timestamp": "2026-01-12T09:30:02.345678"
    }
  },
  {
    "event_type": "like",
    "data": {
      "user": {
        "unique_id": "user789",
        "nickname": "Bob Wilson"
      },
      "count": 5,
      "total_likes": 12345,
      "timestamp": "2026-01-12T09:30:03.456789"
    }
  },
  {
    "event_type": "gift",
    "data": {
      "user": {
        "unique_id": "superfan",
        "nickname": "Super Fan",
        "user_id": "111222333"
      },
      "gift": {
        "id": 5655,
        "name": "Rose",
        "diamond_count": 1,
        "image_url": "https://p19-webcast.tiktokcdn.com/...",
        "streakable": true,
        "type": 1
      },
      "repeat_count": 10,
      "total_diamonds": 10,
      "streaking": false,
      "timestamp": "2026-01-12T09:30:04.567890"
    }
  },
  {
    "event_type": "follow",
    "data": {
      "user": {
        "unique_id": "fan123",
        "nickname": "New Fan",
        "user_id": "444555666"
      },
      "timestamp": "2026-01-12T09:30:10.678901"
    }
  },
  {
    "event_type": "share",
    "data": {
      "user": {
        "unique_id": "supporter",
        "nickname": "Loyal Supporter"
      },
      "timestamp": "2026-01-12T09:30:15.789012"
    }
  }
]
```

---

## Cấu Trúc Dữ Liệu Chi Tiết

### User Object
```json
{
  "unique_id": "username",      // TikTok username
  "nickname": "Display Name",   // Display name
  "user_id": "123456789",       // Numeric user ID
  "profile_picture": "https://..." // Avatar URL (optional)
}
```

### Gift Object
```json
{
  "id": 5655,                   // Gift ID
  "name": "Rose",               // Gift name
  "diamond_count": 1,           // Diamonds per gift
  "image_url": "https://...",   // Gift image
  "streakable": true,           // Can be sent in streak
  "type": 1                     // 1=streakable, 2=one-time
}
```

### Common Fields
- **timestamp**: ISO 8601 format (`2026-01-12T09:30:00.123456`)
- **unique_id**: Always starts with @ in display, but stored without
- **user_id**: String representation of numeric ID

---

## Thống Kê Thực Tế

Từ một livestream 30 giây với ~1000 viewers:

| Event Type | Count | Percentage |
|------------|-------|------------|
| Comments   | 15    | 33%        |
| Joins      | 12    | 27%        |
| Gifts      | 8     | 18%        |
| Likes      | 5     | 11%        |
| Follows    | 3     | 7%         |
| Shares     | 1     | 2%         |
| Connect    | 1     | 2%         |
| **Total**  | **45**| **100%**   |

**Gift Value**: 5,060 diamonds total (~$50 USD)

---

## Sử Dụng Trong TikTok Service

Data này được publish vào Redis Streams:

```python
# In TikTok Service
await redis_publisher.publish_event(
    workspace_id="workspace-123",
    event_type="comment",
    event_data={
        "user": {"unique_id": "user123", "nickname": "John"},
        "comment": "Hello!",
        "timestamp": "2026-01-12T09:30:00"
    }
)
```

Redis Stream Key: `tiktok:events:workspace-123`

Consumers (Rule Engine) đọc từ stream này để trigger automation rules.
