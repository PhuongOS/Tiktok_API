"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


# Request Schemas
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters")


class UserLogin(BaseModel):
    """User login request (for form data)"""
    email: EmailStr
    password: str


# Response Schemas
class UserResponse(BaseModel):
    """User response (without password)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
