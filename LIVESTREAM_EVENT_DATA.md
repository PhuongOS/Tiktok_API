# TikTok Livestream Event Data Structure

Đây là cấu trúc dữ liệu chi tiết của các events khi connect vào TikTok livestream.

## 1. Connect Event

```json
{
  "event_type": "connect",
  "data": {
    "unique_id": "username",
    "room_id": "7123456789012345678",
    "timestamp": "2026-01-12T09:30:00"
  }
}
```

## 2. Comment Event

```json
{
  "event_type": "comment",
  "data": {
    "user": {
      "unique_id": "user123",
      "nickname": "John Doe",
      "user_id": "123456789",
      "profile_picture": "https://..."
    },
    "comment": "Hello! Amazing stream!",
    "timestamp": "2026-01-12T09:30:15"
  }
}
```

## 3. Gift Event

```json
{
  "event_type": "gift",
  "data": {
    "user": {
      "unique_id": "user456",
      "nickname": "Jane Smith",
      "user_id": "987654321"
    },
    "gift": {
      "id": 5655,
      "name": "Rose",
      "diamond_count": 1,
      "image_url": "https://...",
      "streakable": true,
      "type": 1
    },
    "repeat_count": 5,
    "total_diamonds": 5,
    "streaking": false,
    "timestamp": "2026-01-12T09:30:30"
  }
}
```

**Gift Types:**
- `type: 1` - Streakable (can be sent multiple times in a row)
- `type: 2` - Non-streakable (one-time gifts)

**Streaking:**
- `streaking: true` - Gift streak is ongoing
- `streaking: false` - Gift streak ended (final count)

## 4. Like Event

```json
{
  "event_type": "like",
  "data": {
    "user": {
      "unique_id": "user789",
      "nickname": "Bob Wilson"
    },
    "count": 5,
    "total_likes": 12345,
    "timestamp": "2026-01-12T09:30:45"
  }
}
```

## 5. Join Event

```json
{
  "event_type": "join",
  "data": {
    "user": {
      "unique_id": "newuser",
      "nickname": "Alice Brown",
      "user_id": "555666777"
    },
    "timestamp": "2026-01-12T09:31:00"
  }
}
```

## 6. Follow Event

```json
{
  "event_type": "follow",
  "data": {
    "user": {
      "unique_id": "follower123",
      "nickname": "Charlie Davis",
      "user_id": "111222333"
    },
    "timestamp": "2026-01-12T09:31:15"
  }
}
```

## 7. Share Event

```json
{
  "event_type": "share",
  "data": {
    "user": {
      "unique_id": "sharer456",
      "nickname": "Diana Evans"
    },
    "timestamp": "2026-01-12T09:31:30"
  }
}
```

## 8. Live End Event

```json
{
  "event_type": "live_end",
  "data": {
    "timestamp": "2026-01-12T10:00:00"
  }
}
```

## 9. Disconnect Event

```json
{
  "event_type": "disconnect",
  "data": {
    "timestamp": "2026-01-12T10:00:05"
  }
}
```

---

## Event Frequency

Typical livestream với 1000 viewers:
- **Comments**: 10-50 per minute
- **Likes**: 50-200 per minute
- **Gifts**: 5-20 per minute
- **Joins**: 20-100 per minute
- **Follows**: 1-10 per minute
- **Shares**: 1-5 per minute

---

## Usage Example

```python
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent

client = TikTokLiveClient(unique_id="@username")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname}: {event.comment}")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    if not event.streaking:  # Only count when streak ends
        print(f"{event.user.nickname} sent {event.gift.name} x{event.repeat_count}")

await client.start()
```

---

## Testing Tool

Run `capture_livestream_data.py` to:
1. Check if user is live
2. Connect and capture all events
3. Display events in real-time
4. Save to `livestream_events.json`

```bash
python3 capture_livestream_data.py
```
