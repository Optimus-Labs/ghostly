from datetime import datetime
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse

from app.services.token_service import get_token, decrypt_url, update_token_usage, log_access, find_active_token_for_url
from app.models.token import AccessLog


def process_token_access(token_id: str, request: Request) -> RedirectResponse:
    """Process a token access request and return a redirect response"""
    # Get token information
    token = get_token(token_id)
    
    # Handle token not found
    if not token:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if token is active
    if not token.is_active:
        # Try to find a newer active token for the same URL
        new_token = find_active_token_for_url(
            token.original_url,
            token.user_id,
            token.session_id,
            token.device_id
        )
        
        if new_token:
            # Log the access with a redirect status code
            log_access(AccessLog(
                token_id=token_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                referrer=request.headers.get("referer"),
                status_code=301  # Moved Permanently
            ))
            
            # Redirect to the new token URL
            return RedirectResponse(
                url=f"/content/{new_token.token_id}",
                status_code=301
            )
        else:
            # No active token found
            raise HTTPException(status_code=410, detail="Content link has expired")
    
    # Check if token has expired
    if token.expires_at < datetime.now():
        # Log the access as expired
        log_access(AccessLog(
            token_id=token_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            referrer=request.headers.get("referer"),
            status_code=410  # Gone
        ))
        
        # Try to find a newer active token
        new_token = find_active_token_for_url(
            token.original_url,
            token.user_id,
            token.session_id,
            token.device_id
        )
        
        if new_token:
            # Redirect to the new token URL
            return RedirectResponse(
                url=f"/content/{new_token.token_id}",
                status_code=301
            )
        else:
            # No active token found
            raise HTTPException(status_code=410, detail="Content link has expired")
    
    # Token is valid, update usage statistics
    update_token_usage(token_id)
    
    # Log the successful access
    log_access(AccessLog(
        token_id=token_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
        status_code=200  # OK
    ))
    
    # Decrypt the URL and redirect
    original_url = decrypt_url(token.encrypted_url)
    return RedirectResponse(url=original_url)


def validate_url(url: str) -> bool:
    """Validate that a URL is properly formed"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False