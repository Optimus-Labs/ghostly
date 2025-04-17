import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import secrets

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key and save it (in production, this should be set manually)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"Generated new encryption key: {ENCRYPTION_KEY}")
    print("Please save this in your .env file as ENCRYPTION_KEY")

# URL settings
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Token settings
TOKEN_EXPIRY_SECONDS = int(os.getenv("TOKEN_EXPIRY_SECONDS", 3600))