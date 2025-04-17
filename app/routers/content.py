from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional

from app.models.token import TokenCreate, TokenResponse
from app.services.token_service import create_token, find_active_token_for_url
from app.services.url_service import process_token_access, validate_url

router = APIRouter()

@router.post("/api/token", response_model=TokenResponse)
async def generate_token(token_data: TokenCreate):
    """
    Generate a secure token for content access
    
    - Returns an existing token if one exists for the same URL and identifiers
    - Creates a new token if none exists or if the existing one is expired
    """
    # Validate the URL
    if not validate_url(token_data.original_url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Check if an active token already exists for this URL and identifiers
    existing_token = find_active_token_for_url(
        token_data.original_url,
        token_data.user_id,
        token_data.session_id,
        token_data.device_id
    )
    
    if existing_token:
        # Return the existing token
        return TokenResponse(
            token=existing_token.token_id,
            secure_url=f"{router.url_path_for('access_content', token_id=existing_token.token_id)}",
            expires_at=existing_token.expires_at
        )
    
    # Create a new token
    return create_token(token_data)

@router.get("/content/{token_id}")
async def access_content(token_id: str, request: Request):
    """
    Access content using a secure token
    
    - Validates the token
    - Tracks access statistics
    - Redirects to the original content if valid
    - Handles expired tokens with automatic redirection if newer tokens exist
    """
    return process_token_access(token_id, request)

@router.get("/api/token/{token_id}/status")
async def token_status(token_id: str):
    """Get status information about a token"""
    token = get_token(token_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return {
        "token_id": token.token_id,
        "created_at": token.created_at,
        "expires_at": token.expires_at,
        "is_active": token.is_active,
        "access_count": token.access_count,
        "last_accessed": token.last_accessed
    }