import logging
from typing import Optional, Tuple
from bot.services.tokens import get_token_data, increment_access_count
from bot.services.security import verify_key

logger = logging.getLogger(__name__)

async def verify_access(db, token: str, key: str) -> Tuple[bool, Optional[dict], str]:
    """
    Verify if user has access to file
    Returns: (success, token_data, error_message)
    """
    try:
        # Get token data
        token_data = await get_token_data(db, token)
        
        if not token_data:
            return False, None, "invalid_token"
        
        # Verify key
        is_valid = verify_key(token, token_data["file_id"], key)
        
        if not is_valid:
            logger.warning(f"⚠️ Invalid key attempt for token: {token}")
            return False, None, "invalid_key"
        
        # Increment access count
        await increment_access_count(db, token)
        
        logger.info(f"✅ Access granted for token: {token}")
        return True, token_data, None
    
    except Exception as e:
        logger.error(f"❌ Access verification failed BC: {e}")
        return False, None, "server_error"

async def check_rate_limit(db, user_id: int, limit: int = 10, window_minutes: int = 60) -> bool:
    """
    Check if user has exceeded rate limit
    Returns: True if within limit, False if exceeded
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate time window
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Count recent accesses
        count = await db.links.count_documents({
            "user_id": user_id,
            "last_accessed": {"$gte": window_start}
        })
        
        if count >= limit:
            logger.warning(f"⚠️ Rate limit exceeded for user {user_id}")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Rate limit check failed: {e}")
        return True  # Allow on error

async def log_access_attempt(db, token: str, user_id: int, ip_address: str, success: bool, error: str = None):
    """Log access attempt for security monitoring"""
    try:
        log_doc = {
            "token": token,
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "error": error,
            "timestamp": datetime.utcnow()
        }
        
        await db.access_logs.insert_one(log_doc)
    
    except Exception as e:
        logger.error(f"❌ Failed to log access attempt: {e}")
