from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TokenBase(BaseModel):
    original_url: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    expires_in_seconds: int = 3600  # Default: 1 hour

class TokenCreate(TokenBase):
    pass

class TokenResponse(BaseModel):
    token: str
    secure_url: str
    expires_at: datetime

class TokenDB(BaseModel):
    token_id: str
    original_url: str
    encrypted_url: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class AccessLog(BaseModel):
    token_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    status_code: int = 200