"""
Unit tests for security utilities
"""
import pytest
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$argon2")
    
    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password("wrong_password", hashed) is False
    
    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        hashed = hash_password("password")
        
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token functions"""
    
    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "user@example.com", "user_id": 123}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_decode_access_token(self):
        """Test decoding access token"""
        data = {"sub": "user@example.com", "user_id": 123}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == "user@example.com"
        assert decoded["user_id"] == 123
        assert "exp" in decoded
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_expired_token(self):
        """Test decoding expired token"""
        from datetime import timedelta
        
        data = {"sub": "user@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        import time
        time.sleep(1)
        
        decoded = decode_access_token(token)
        
        assert decoded is None


# Run with: pytest tests/test_security.py -v
