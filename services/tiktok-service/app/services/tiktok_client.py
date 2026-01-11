"""
TikTok LIVE connection manager with Proto Events
"""
from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    LiveEndEvent,
    CommentEvent,
    GiftEvent,
    LikeEvent,
    JoinEvent,
    FollowEvent,
    ShareEvent
)
import asyncio
from typing import Dict, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TikTokConnectionManager:
    """Manages TikTok LIVE connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, TikTokLiveClient] = {}
    
    async def connect(
        self,
        livestream_id: str,
        unique_id: str = None,
        room_id: str = None,
        event_callback: Callable = None
    ) -> TikTokLiveClient:
        """
        Connect to TikTok LIVE
        
        Args:
            livestream_id: Internal livestream ID
            unique_id: TikTok username (optional)
            room_id: TikTok room ID (optional)
            event_callback: Async callback(event_type, event_data)
        """
        if livestream_id in self.active_connections:
            raise ValueError(f"Already connected: {livestream_id}")
        
        # Create client (username OR room_id)
        if unique_id:
            client = TikTokLiveClient(unique_id=unique_id)
        elif room_id:
            client = TikTokLiveClient(room_id=room_id)
        else:
            raise ValueError("Must provide unique_id or room_id")
        
        # === Connection Events ===
        
        @client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            logger.info(f"✅ Connected: {event.unique_id} (Room: {event.room_id})")
            await event_callback("connect", {
                "livestream_id": livestream_id,
                "unique_id": event.unique_id,
                "room_id": str(event.room_id),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            logger.info(f"❌ Disconnected: {livestream_id}")
            await event_callback("disconnect", {
                "livestream_id": livestream_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(LiveEndEvent)
        async def on_live_end(event: LiveEndEvent):
            logger.info(f"🔴 Stream ended: {livestream_id}")
            await event_callback("live_end", {
                "livestream_id": livestream_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # === Interaction Events ===
        
        @client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            await event_callback("comment", {
                "livestream_id": livestream_id,
                "user_id": str(event.user.id),
                "username": event.user.nickname,
                "comment": event.comment,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            await event_callback("gift", {
                "livestream_id": livestream_id,
                "user_id": str(event.user.id),
                "username": event.user.nickname,
                "gift_id": event.gift.id,
                "gift_name": event.gift.name,
                "gift_count": event.repeat_count,
                "diamond_count": event.gift.diamond_count,
                "streaking": event.streaking,
                "value_usd": event.value,  # None if streaking
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            await event_callback("like", {
                "livestream_id": livestream_id,
                "user_id": str(event.user.id),
                "username": event.user.nickname,
                "like_count": event.count,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(JoinEvent)
        async def on_join(event: JoinEvent):
            await event_callback("join", {
                "livestream_id": livestream_id,
                "user_id": str(event.user.id),
                "username": event.user.nickname,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            await event_callback("follow", {
                "livestream_id": livestream_id,
                "user_id": str(event.user.id),
                "username": event.user.nickname,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @client.on(ShareEvent)
        async def on_share(event: ShareEvent):
            await event_callback("share", {
                "livestream_id": livestream_id,
                "user_id": str(event.user.id),
                "username": event.user.nickname,
                "users_joined": event.users_joined,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Store & start
        self.active_connections[livestream_id] = client
        asyncio.create_task(client.start())
        
        return client
    
    async def disconnect(self, livestream_id: str):
        """Disconnect from stream"""
        if livestream_id not in self.active_connections:
            raise ValueError(f"Not connected: {livestream_id}")
        
        client = self.active_connections[livestream_id]
        await client.stop()
        del self.active_connections[livestream_id]
    
    def is_connected(self, livestream_id: str) -> bool:
        return livestream_id in self.active_connections


# Global instance
tiktok_manager = TikTokConnectionManager()
