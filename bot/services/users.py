import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

async def get_or_create_user(db, user_id: int, username: str = None, first_name: str = None) -> dict:
    """Get user from database or create if not exists"""
    try:
        user = await db.users.find_one({"user_id": user_id})
        
        if not user:
            user = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "is_premium": False,
                "premium_expiry": None,
                "join_date": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "total_files": 0,
                "total_links": 0
            }
            await db.users.insert_one(user)
            logger.info(f"✅ New user created: {user_id}")
        else:
            # Update last active
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )
        
        return user
    
    except Exception as e:
        logger.error(f"❌ User creation failed BC: {e}")
        raise

async def is_premium(db, user_id: int) -> bool:
    """Check if user has active premium"""
    try:
        user = await db.users.find_one({"user_id": user_id})
        
        if not user:
            return False
        
        if not user.get("is_premium"):
            return False
        
        expiry = user.get("premium_expiry")
        if expiry and expiry < datetime.utcnow():
            # Premium expired
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_premium": False, "premium_expiry": None}}
            )
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Premium check failed: {e}")
        return False

async def add_premium(db, user_id: int, days: int):
    """Add premium to user"""
    try:
        expiry = datetime.utcnow() + timedelta(days=days)
        
        result = await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_premium": True,
                    "premium_expiry": expiry
                }
            },
            upsert=True
        )
        
        logger.info(f"✅ Premium added for user {user_id} - {days} days")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to add premium BC: {e}")
        return False

async def remove_premium(db, user_id: int):
    """Remove premium from user"""
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": False, "premium_expiry": None}}
        )
        logger.info(f"🗑 Premium removed for user {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to remove premium: {e}")
        return False

async def get_user_stats(db, user_id: int) -> dict:
    """Get user statistics"""
    try:
        user = await db.users.find_one({"user_id": user_id})
        
        if not user:
            return None
        
        # Count user's files
        files_count = await db.files.count_documents({"uploader_id": user_id})
        
        # Count user's links
        links_count = await db.links.count_documents({"user_id": user_id})
        
        return {
            "user_id": user["user_id"],
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "is_premium": user.get("is_premium", False),
            "premium_expiry": user.get("premium_expiry"),
            "join_date": user.get("join_date"),
            "total_files": files_count,
            "total_links": links_count
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to get user stats: {e}")
        return None

async def get_bot_stats(db) -> dict:
    """Get overall bot statistics"""
    try:
        total_users = await db.users.count_documents({})
        premium_users = await db.users.count_documents({"is_premium": True})
        total_files = await db.files.count_documents({})
        total_links = await db.links.count_documents({})
        
        # Get today's stats
        from datetime import datetime
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_users = await db.users.count_documents({"join_date": {"$gte": today_start}})
        today_files = await db.files.count_documents({"upload_time": {"$gte": today_start}})
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "total_files": total_files,
            "total_links": total_links,
            "today_users": today_users,
            "today_files": today_files
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to get bot stats: {e}")
        return {}
