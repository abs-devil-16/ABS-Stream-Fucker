import logging
from typing import Optional
from config import Config
from bot.services.tokens import create_file_token
from bot.services.security import create_secure_link

logger = logging.getLogger(__name__)

async def generate_file_links(db, file_doc: dict, user_id: int, is_premium: bool) -> dict:
    """Generate all links for a file"""
    try:
        # Create token and key
        token_data = await create_file_token(
            db,
            file_doc["file_id"],
            file_doc["file_unique_id"],
            user_id,
            is_premium
        )
        
        token = token_data["token"]
        key = token_data["key"]
        
        # Generate links
        telegram_link = f"https://t.me/{Config.BOT_USERNAME}?start={token}"
        stream_link = create_secure_link(token, key, "stream")
        download_link = create_secure_link(token, key, "download")
        
        links = {
            "token": token,
            "key": key,
            "telegram_link": telegram_link,
            "stream_link": stream_link,
            "download_link": download_link,
            "is_premium": is_premium,
            "expiry": token_data.get("expiry_at")
        }
        
        logger.info(f"✅ Links generated for file {file_doc['file_id'][:10]}...")
        return links
    
    except Exception as e:
        logger.error(f"❌ Link generation failed BC: {e}")
        raise

async def get_link_by_token(db, token: str) -> Optional[dict]:
    """Get link data by token"""
    try:
        link = await db.links.find_one({"token": token})
        return link
    except Exception as e:
        logger.error(f"❌ Link lookup failed: {e}")
        return None

async def get_file_from_token(db, token: str) -> Optional[dict]:
    """Get file associated with token"""
    try:
        link = await get_link_by_token(db, token)
        
        if not link:
            return None
        
        from bot.services.files import get_file_by_id
        file_doc = await get_file_by_id(db, link["file_id"])
        
        return file_doc
    except Exception as e:
        logger.error(f"❌ Failed to get file from token: {e}")
        return None

async def delete_link(db, token: str, user_id: int) -> bool:
    """Delete a specific link"""
    try:
        from config import Config
        
        # Get link
        link = await get_link_by_token(db, token)
        
        if not link:
            return False
        
        # Check ownership
        if link["user_id"] != user_id and user_id != Config.OWNER_ID:
            logger.warning(f"⚠️ Unauthorized link delete by user {user_id}")
            return False
        
        # Delete
        result = await db.links.delete_one({"token": token})
        
        logger.info(f"🗑 Link deleted: {token}")
        return result.deleted_count > 0
    
    except Exception as e:
        logger.error(f"❌ Link deletion failed: {e}")
        return False

async def get_user_links(db, user_id: int, limit: int = 10) -> list:
    """Get links created by user"""
    try:
        cursor = db.links.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        links = await cursor.to_list(length=limit)
        return links
    except Exception as e:
        logger.error(f"❌ Failed to get user links: {e}")
        return []
