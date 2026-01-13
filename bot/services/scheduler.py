import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def check_premium_expiry(app):
    """Check and notify expired premium users"""
    try:
        db = app.db
        
        # Find expired premium users
        expired_users = await db.users.find({
            "is_premium": True,
            "premium_expiry": {"$lt": datetime.utcnow()}
        }).to_list(length=None)
        
        for user in expired_users:
            # Update status
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"is_premium": False, "premium_expiry": None}}
            )
            
            # Notify user
            try:
                await app.send_message(
                    user["user_id"],
                    "⚠️ **Arre yaar BC!** 😔\n\n"
                    "Tera premium khatam ho gaya MC!\n\n"
                    "**Ab kya hoga:**\n"
                    "• Wait time lagega\n"
                    "• Links expire honge\n"
                    "• Slow speed milega\n\n"
                    "💎 **Renew kar le:**\n"
                    "Owner se contact kar: /start\n\n"
                    "Warna free user ban jayega bhenchod! 💀"
                )
                logger.info(f"✅ Notified user {user['user_id']} about premium expiry")
            except Exception as e:
                logger.error(f"❌ Failed to notify user {user['user_id']}: {e}")
        
        if expired_users:
            logger.info(f"✅ Processed {len(expired_users)} expired premium users MC!")
    
    except Exception as e:
        logger.error(f"❌ Premium expiry check failed BC: {e}")

async def cleanup_expired_links(app):
    """Clean up expired links from database"""
    try:
        db = app.db
        
        # Delete expired links
        result = await db.links.delete_many({
            "expiry_at": {"$lt": datetime.utcnow(), "$ne": None}
        })
        
        if result.deleted_count > 0:
            logger.info(f"🗑 Cleaned up {result.deleted_count} expired links MC!")
    
    except Exception as e:
        logger.error(f"❌ Link cleanup failed: {e}")

def start_scheduler(app):
    """Start the scheduler"""
    if scheduler.running:
        logger.warning("⚠️ Scheduler already running MC!")
        return
    
    # Check premium expiry every 6 hours
    scheduler.add_job(
        check_premium_expiry,
        trigger=IntervalTrigger(hours=6),
        args=[app],
        id="check_premium_expiry",
        replace_existing=True
    )
    
    # Cleanup expired links every 12 hours
    scheduler.add_job(
        cleanup_expired_links,
        trigger=IntervalTrigger(hours=12),
        args=[app],
        id="cleanup_expired_links",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started BC! 🔥")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")
