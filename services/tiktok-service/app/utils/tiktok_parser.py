"""
Parse various TikTok input formats
"""
import re
from typing import Tuple


class TikTokInputParser:
    """Parse username, room ID, or TikTok LIVE URL"""
    
    # Regex patterns
    USERNAME_PATTERN = re.compile(r'^@?([a-zA-Z0-9._]+)$')
    ROOM_ID_PATTERN = re.compile(r'^\d{19}$')  # TikTok room IDs are 19 digits
    
    # URL patterns
    LIVE_URL_PATTERNS = [
        r'tiktok\.com/@([^/]+)/live',
        r'tiktok\.com/live/([^/?]+)',
        r'vm\.tiktok\.com/([^/?]+)',
    ]
    
    @classmethod
    def parse(cls, input_str: str) -> Tuple[str, str]:
        """
        Parse TikTok input
        
        Returns:
            (input_type, value)
            - input_type: 'username', 'room_id', or 'short_url'
            - value: Cleaned value
        
        Raises:
            ValueError: Invalid format
        """
        input_str = input_str.strip()
        
        # Check URL
        if input_str.startswith('http://') or input_str.startswith('https://'):
            return cls._parse_url(input_str)
        
        # Check room ID (19 digits)
        if cls.ROOM_ID_PATTERN.match(input_str):
            return ('room_id', input_str)
        
        # Check username
        match = cls.USERNAME_PATTERN.match(input_str)
        if match:
            return ('username', match.group(1))
        
        raise ValueError(
            "Invalid input. Supported formats:\n"
            "- Username: @username or username\n"
            "- Room ID: 19-digit number\n"
            "- URL: https://www.tiktok.com/@username/live"
        )
    
    @classmethod
    def _parse_url(cls, url: str) -> Tuple[str, str]:
        """Parse TikTok URL"""
        for pattern in cls.LIVE_URL_PATTERNS:
            match = re.search(pattern, url)
            if match:
                identifier = match.group(1)
                
                # Short link
                if 'vm.tiktok.com' in url:
                    return ('short_url', identifier)
                
                # Username
                return ('username', identifier)
        
        raise ValueError("Invalid TikTok URL")
