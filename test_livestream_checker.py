#!/usr/bin/env python3
"""
Test script to check if TikTok users are currently live
"""
import asyncio
from TikTokLive import TikTokLiveClient


async def check_if_live(username: str) -> bool:
    """Check if a TikTok user is currently live"""
    try:
        client = TikTokLiveClient(unique_id=f'@{username}')
        is_live = await client.is_live()
        return is_live
    except Exception as e:
        print(f"Error checking @{username}: {str(e)[:100]}")
        return False


async def main():
    """Test livestream detection with multiple users"""
    print("=" * 60)
    print("TikTok Livestream Status Checker")
    print("=" * 60)
    
    # Test users (mix of popular and potentially live users)
    test_users = [
        'charlidamelio',
        'khaby.lame', 
        'bellapoarch',
        'boss001735',  # User from previous test
        'tiktok',
        'zachking'
    ]
    
    print(f"\nChecking {len(test_users)} TikTok users...\n")
    
    results = []
    for username in test_users:
        print(f"Checking @{username}...", end=" ", flush=True)
        is_live = await check_if_live(username)
        status = "LIVE" if is_live else "OFFLINE"
        print(status)
        results.append((username, is_live))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    live_count = sum(1 for _, is_live in results if is_live)
    print(f"Total checked: {len(results)}")
    print(f"Currently live: {live_count}")
    print(f"Offline: {len(results) - live_count}")
    
    if live_count > 0:
        print("\nLive users:")
        for username, is_live in results:
            if is_live:
                print(f"  - @{username}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
