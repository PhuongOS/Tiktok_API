#!/usr/bin/env python3
"""
Test script to capture and display all events from a TikTok livestream
Shows detailed event data structure
"""
import asyncio
import json
from datetime import datetime
from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    CommentEvent,
    GiftEvent,
    LikeEvent,
    JoinEvent,
    FollowEvent,
    ShareEvent,
    LiveEndEvent
)


class LivestreamDataCapture:
    """Capture and display livestream event data"""
    
    def __init__(self, username: str):
        self.username = username
        self.client = TikTokLiveClient(unique_id=f'@{username}')
        self.events_captured = []
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup event handlers for all event types"""
        
        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            print("\n" + "="*60)
            print(f"🟢 CONNECTED to @{event.unique_id}")
            print(f"Room ID: {self.client.room_id}")
            print("="*60 + "\n")
            
            # Capture event data
            self.save_event("connect", {
                "unique_id": event.unique_id,
                "room_id": self.client.room_id,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            print("\n" + "="*60)
            print("🔴 DISCONNECTED")
            print("="*60 + "\n")
            self.save_event("disconnect", {"timestamp": datetime.now().isoformat()})
        
        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            print(f"💬 Comment from @{event.user.unique_id}: {event.comment}")
            
            # Detailed event data
            event_data = {
                "type": "comment",
                "user": {
                    "unique_id": event.user.unique_id,
                    "nickname": event.user.nickname,
                    "user_id": str(event.user.user_id),
                    "profile_picture": event.user.profile_picture.avatar_thumb.url_list[0] if event.user.profile_picture else None
                },
                "comment": event.comment,
                "timestamp": datetime.now().isoformat()
            }
            self.save_event("comment", event_data)
        
        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            # Handle streakable gifts
            if event.gift.streakable and not event.streaking:
                print(f"🎁 Gift from @{event.user.unique_id}: {event.gift.name} x{event.repeat_count} (Total: {event.gift.diamond_count * event.repeat_count} diamonds)")
            elif not event.gift.streakable:
                print(f"🎁 Gift from @{event.user.unique_id}: {event.gift.name} ({event.gift.diamond_count} diamonds)")
            
            # Detailed gift data
            event_data = {
                "type": "gift",
                "user": {
                    "unique_id": event.user.unique_id,
                    "nickname": event.user.nickname,
                    "user_id": str(event.user.user_id)
                },
                "gift": {
                    "id": event.gift.id,
                    "name": event.gift.name,
                    "diamond_count": event.gift.diamond_count,
                    "image_url": event.gift.image.url_list[0] if event.gift.image else None,
                    "streakable": event.gift.streakable,
                    "type": event.gift.type
                },
                "repeat_count": event.repeat_count,
                "total_diamonds": event.gift.diamond_count * event.repeat_count,
                "streaking": event.streaking,
                "timestamp": datetime.now().isoformat()
            }
            self.save_event("gift", event_data)
        
        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            print(f"❤️ Like from @{event.user.unique_id} (x{event.count})")
            
            event_data = {
                "type": "like",
                "user": {
                    "unique_id": event.user.unique_id,
                    "nickname": event.user.nickname
                },
                "count": event.count,
                "total_likes": event.total_likes,
                "timestamp": datetime.now().isoformat()
            }
            self.save_event("like", event_data)
        
        @self.client.on(JoinEvent)
        async def on_join(event: JoinEvent):
            print(f"👥 @{event.user.unique_id} joined the stream")
            
            event_data = {
                "type": "join",
                "user": {
                    "unique_id": event.user.unique_id,
                    "nickname": event.user.nickname,
                    "user_id": str(event.user.user_id)
                },
                "timestamp": datetime.now().isoformat()
            }
            self.save_event("join", event_data)
        
        @self.client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            print(f"⭐ @{event.user.unique_id} followed the streamer!")
            
            event_data = {
                "type": "follow",
                "user": {
                    "unique_id": event.user.unique_id,
                    "nickname": event.user.nickname,
                    "user_id": str(event.user.user_id)
                },
                "timestamp": datetime.now().isoformat()
            }
            self.save_event("follow", event_data)
        
        @self.client.on(ShareEvent)
        async def on_share(event: ShareEvent):
            print(f"📤 @{event.user.unique_id} shared the stream!")
            
            event_data = {
                "type": "share",
                "user": {
                    "unique_id": event.user.unique_id,
                    "nickname": event.user.nickname
                },
                "timestamp": datetime.now().isoformat()
            }
            self.save_event("share", event_data)
        
        @self.client.on(LiveEndEvent)
        async def on_live_end(event: LiveEndEvent):
            print("\n" + "="*60)
            print("📺 LIVESTREAM ENDED")
            print("="*60 + "\n")
            self.save_event("live_end", {"timestamp": datetime.now().isoformat()})
    
    def save_event(self, event_type: str, data: dict):
        """Save event to list"""
        self.events_captured.append({
            "event_type": event_type,
            "data": data
        })
    
    def print_summary(self):
        """Print summary of captured events"""
        print("\n" + "="*60)
        print("📊 EVENT SUMMARY")
        print("="*60)
        
        # Count events by type
        event_counts = {}
        for event in self.events_captured:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print(f"\nTotal events captured: {len(self.events_captured)}")
        print("\nBreakdown by type:")
        for event_type, count in sorted(event_counts.items()):
            print(f"  {event_type}: {count}")
        
        print("\n" + "="*60)
    
    def save_to_file(self, filename: str = "livestream_events.json"):
        """Save all events to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.events_captured, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Events saved to {filename}")
    
    async def run(self, duration: int = 60):
        """Run the client for specified duration"""
        print(f"🔍 Checking if @{self.username} is live...")
        
        is_live = await self.client.is_live()
        if not is_live:
            print(f"❌ @{self.username} is not currently live")
            return
        
        print(f"✅ @{self.username} is LIVE! Connecting...")
        print(f"⏱️ Will capture events for {duration} seconds\n")
        
        try:
            # Start the client
            await self.client.start()
            
            # Run for specified duration
            await asyncio.sleep(duration)
            
            # Disconnect
            await self.client.disconnect()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
            await self.client.disconnect()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        finally:
            self.print_summary()
            self.save_to_file()


async def main():
    """Main function"""
    print("="*60)
    print("TikTok Livestream Data Capture Tool")
    print("="*60)
    
    # Test with a username (you can change this)
    username = input("\nEnter TikTok username (without @): ").strip()
    if not username:
        username = "boss001735"  # Default test user
    
    duration = input("Capture duration in seconds (default 60): ").strip()
    duration = int(duration) if duration else 60
    
    capture = LivestreamDataCapture(username)
    await capture.run(duration)


if __name__ == "__main__":
    asyncio.run(main())
