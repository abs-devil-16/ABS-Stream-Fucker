import hashlib
import hmac
import secrets
import base64
from config import Config
from typing import Tuple

def generate_token() -> str:
    """Generate random secure token"""
    return secrets.token_urlsafe(16)

def generate_key(token: str, file_id: str) -> str:
    """Generate HMAC-based secure key"""
    data = f"{token}:{file_id}:{Config.MASTER_SECRET}"
    
    key = hmac.new(
        Config.MASTER_SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return key[:32]

def verify_key(token: str, file_id: str, provided_key: str) -> bool:
    """Verify if the provided key is valid"""
    expected_key = generate_key(token, file_id)
    return hmac.compare_digest(expected_key, provided_key)

def create_secure_link(token: str, key: str, endpoint: str) -> str:
    """Create secure link with token and key"""
    return f"{Config.WEB_BASE_URL}/{endpoint}/{token}?key={key}"

def encode_file_id(file_id: str) -> str:
    """Encode file_id for additional security"""
    encoded = base64.urlsafe_b64encode(file_id.encode()).decode()
    return encoded

def decode_file_id(encoded: str) -> str:
    """Decode file_id"""
    try:
        decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
        return decoded
    except Exception:
        return None
