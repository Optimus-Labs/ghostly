import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.config import DATABASE_URL

def create_tables():
    """Create necessary tables if they don't exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Create tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    id SERIAL PRIMARY KEY,
                    token_id VARCHAR(255) UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    encrypted_url TEXT NOT NULL,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    device_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            """)
            
            # Create access_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id SERIAL PRIMARY KEY,
                    token_id VARCHAR(255) REFERENCES tokens(token_id),
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    referrer TEXT,
                    status_code INTEGER
                )
            """)
            
            conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    """Context manager for database cursors."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e