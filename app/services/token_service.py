import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from urllib.parse import urlparse, parse_qs, urlencode

from app.config import ENCRYPTION_KEY, BASE_URL, TOKEN_EXPIRY_SECONDS
from app.db.database import get_db_cursor
from app.models.token import TokenCreate, TokenDB, TokenResponse, AccessLog

# Initialize Fernet cipher for encryption/decryption
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def generate_token_id():
    """Generate a unique token ID"""
    return secrets.token_urlsafe(16)

def encrypt_url(url):
    """Encrypt a URL"""
    return cipher.encrypt(url.encode()).decode()

def decrypt_url(encrypted_url):
    """Decrypt an encrypted URL"""
    return cipher.decrypt(encrypted_url.encode()).decode()

def create_token(token_data: TokenCreate) -> TokenResponse:
    """Create a new token for the given URL"""
    token_id = generate_token_id()
    encrypted_url = encrypt_url(token_data.original_url)
    
    expires_in = token_data.expires_in_seconds or TOKEN_EXPIRY_SECONDS
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO tokens (
                token_id, original_url, encrypted_url, user_id, session_id, device_id, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING created_at
        """, (
            token_id, 
            token_data.original_url, 
            encrypted_url, 
            token_data.user_id, 
            token_data.session_id, 
            token_data.device_id, 
            expires_at
        ))
        created_at = cursor.fetchone()['created_at']
    
    secure_url = f"{BASE_URL}/content/{token_id}"
    
    return TokenResponse(
        token=token_id,
        secure_url=secure_url,
        expires_at=expires_at
    )

def get_token(token_id: str) -> TokenDB:
    """Get token information from the database"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT token_id, original_url, encrypted_url, user_id, session_id, device_id, 
                   created_at, expires_at, is_active, access_count, last_accessed
            FROM tokens
            WHERE token_id = %s
        """, (token_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return None
            
        return TokenDB(**result)

def find_active_token_for_url(original_url: str, user_id: str = None, session_id: str = None, device_id: str = None) -> TokenDB:
    """Find an active token for the given URL and identifiers"""
    query = """
        SELECT token_id, original_url, encrypted_url, user_id, session_id, device_id, 
               created_at, expires_at, is_active, access_count, last_accessed
        FROM tokens
        WHERE original_url = %s 
          AND expires_at > NOW() 
          AND is_active = TRUE
    """
    params = [original_url]
    
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    
    if session_id:
        query += " AND session_id = %s"
        params.append(session_id)
        
    if device_id:
        query += " AND device_id = %s"
        params.append(device_id)
    
    query += " ORDER BY expires_at DESC LIMIT 1"
    
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if not result:
            return None
            
        return TokenDB(**result)

def update_token_usage(token_id: str) -> None:
    """Update token usage statistics"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE tokens
            SET access_count = access_count + 1, last_accessed = NOW()
            WHERE token_id = %s
        """, (token_id,))

def log_access(access_log: AccessLog) -> None:
    """Log an access attempt"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO access_logs (token_id, ip_address, user_agent, referrer, status_code)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            access_log.token_id,
            access_log.ip_address,
            access_log.user_agent,
            access_log.referrer,
            access_log.status_code
        ))

def deactivate_token(token_id: str) -> None:
    """Deactivate a token"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE tokens
            SET is_active = FALSE
            WHERE token_id = %s
        """, (token_id,))

def clean_expired_tokens() -> int:
    """Deactivate all expired tokens and return the count"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE tokens
            SET is_active = FALSE
            WHERE expires_at < NOW() AND is_active = TRUE
            RETURNING token_id
        """)
        
        expired_tokens = cursor.fetchall()
        return len(expired_tokens)