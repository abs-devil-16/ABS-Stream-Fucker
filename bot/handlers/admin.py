import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.services.users import add_premium, remove_premium, get_bot_stats
from bot.services.files import delete_file
from config import Config

logger = logging.getLogger(__name__)

def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    return user_id == Config.OWNER_ID

async def stats_handler(client: Client, message: Message):
    """Handle /stats command (Owner only)"""
    if not is_owner(message.from_user.id):
        await message.reply_text(
            "🚫 **Tu owner nahi hai BC!**\n\n"
            "Haath mat laga! 😤"
        )
        return
    
    try:
        stats = await get_bot_stats(client.db)
        
        stats_text = (
            "📊 **Bot Statistics MC:** 🔥\n\n"
            f"👥 **Total Users:** {stats.get('total_users', 0)}\n"
            f"💎 **Premium Users:** {stats.get('premium_users', 0)}\n"
            f"📁 **Total Files:** {stats.get('total_files', 0)}\n"
            f"🔗 **Total Links:** {stats.get('total_links', 0)}\n\n"
            f"📈 **Today:**\n"
            f"• New Users: {stats.get('today_users', 0)}\n"
            f"• New Files: {stats.get('today_files', 0)}\n\n"
            "Bot ekdum jhakaas chal raha hai MC! 🚀"
        )
        
        await message.reply_text(stats_text)
    
    except Exception as e:
        logger.error(f"❌ Stats handler failed: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

async def addpremium_handler(client: Client, message: Message):
    """Handle /addpremium command (Owner only)"""
    if not is_owner(message.from_user.id):
        await message.reply_text("🚫 **Owner nahi hai tu BC!** 😤")
        return
    
    try:
        # Parse command: /addpremium user_id days
        if len(message.command) < 3:
            await message.reply_text(
                "❌ **Galat format BC!**\n\n"
                "**Usage:** `/addpremium user_id days`\n"
                "**Example:** `/addpremium 123456789 30`"
            )
            return
        
        user_id = int(message.command[1])
        days = int(message.command[2])
        
        if days <= 0:
            await message.reply_text("❌ Days positive hona chahiye chutiye!")
            return
        
        # Add premium
        success = await add_premium(client.db, user_id, days)
        
        if success:
            await message.reply_text(
                f"✅ **Premium added BC!** 💎\n\n"
                f"**User ID:** `{user_id}`\n"
                f"**Days:** {days}\n\n"
                "User ko notify kar diya! 🔥"
            )
            
            # Notify user
            try:
                await client.send_message(
                    user_id,
                    f"🎉 **Congratulations MC!** 💎\n\n"
                    f"Tu ab premium member hai!\n\n"
                    f"**Benefits:**\n"
                    f"✅ No wait time\n"
                    f"✅ Links never expire\n"
                    f"✅ Max speed\n"
                    f"✅ Priority support\n\n"
                    f"**Duration:** {days} days\n\n"
                    "Enjoy kar bhenchod! 🔥"
                )
            except Exception as e:
                logger.error(f"Failed to notify user: {e}")
        else:
            await message.reply_text("❌ Failed to add premium BC!")
    
    except ValueError:
        await message.reply_text("❌ Invalid user_id or days!")
    except Exception as e:
        logger.error(f"❌ Addpremium failed: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

async def removepremium_handler(client: Client, message: Message):
    """Handle /removepremium command (Owner only)"""
    if not is_owner(message.from_user.id):
        await message.reply_text("🚫 **Owner nahi hai tu BC!** 😤")
        return
    
    try:
        # Parse command: /removepremium user_id
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Galat format BC!**\n\n"
                "**Usage:** `/removepremium user_id`\n"
                "**Example:** `/removepremium 123456789`"
            )
            return
        
        user_id = int(message.command[1])
        
        # Remove premium
        success = await remove_premium(client.db, user_id)
        
        if success:
            await message.reply_text(
                f"✅ **Premium removed BC!** 🗑\n\n"
                f"**User ID:** `{user_id}`\n\n"
                "Ab wo free user hai! 💀"
            )
            
            # Notify user
            try:
                await client.send_message(
                    user_id,
                    "⚠️ **Premium removed BC!** 😔\n\n"
                    "Owner ne tera premium hata diya!\n\n"
                    "Ab tu free user hai:\n"
                    "• Wait time lagega\n"
                    "• Links expire honge\n"
                    "• Slow speed\n\n"
                    "Contact owner for details: /start"
                )
            except Exception as e:
                logger.error(f"Failed to notify user: {e}")
        else:
            await message.reply_text("❌ Failed to remove premium!")
    
    except ValueError:
        await message.reply_text("❌ Invalid user_id!")
    except Exception as e:
        logger.error(f"❌ Removepremium failed: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

async def broadcast_handler(client: Client, message: Message):
    """Handle /broadcast command (Owner only)"""
    if not is_owner(message.from_user.id):
        await message.reply_text("🚫 **Owner nahi hai tu BC!** 😤")
        return
    
    try:
        # Get broadcast message
        if not message.reply_to_message:
            await message.reply_text(
                "❌ **Koi message reply kar BC!**\n\n"
                "Jo message broadcast karna hai usko reply kar with /broadcast"
            )
            return
        
        broadcast_msg = message.reply_to_message
        
        # Get all users
        users = await client.db.users.find({}).to_list(length=None)
        
        sent = 0
        failed = 0
        
        status_msg = await message.reply_text(
            f"📢 **Broadcasting MC...**\n\n"
            f"Total users: {len(users)}\n"
            f"Sent: {sent}\n"
            f"Failed: {failed}"
        )
        
        for user in users:
            try:
                await broadcast_msg.copy(user["user_id"])
                sent += 1
                
                # Update status every 10 users
                if sent % 10 == 0:
                    await status_msg.edit_text(
                        f"📢 **Broadcasting MC...**\n\n"
                        f"Total: {len(users)}\n"
                        f"Sent: {sent}\n"
                        f"Failed: {failed}"
                    )
            except Exception as e:
                failed += 1
                logger.error(f"Broadcast failed for {user['user_id']}: {e}")
        
        await status_msg.edit_text(
            f"✅ **Broadcast complete BC!** 🔥\n\n"
            f"Total: {len(users)}\n"
            f"Sent: {sent}\n"
            f"Failed: {failed}"
        )
    
    except Exception as e:
        logger.error(f"❌ Broadcast failed: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

def register(app: Client):
    """Register admin handlers"""
    app.add_handler(filters.command("stats") & filters.private, stats_handler)
    app.add_handler(filters.command("addpremium") & filters.private, addpremium_handler)
    app.add_handler(filters.command("removepremium") & filters.private, removepremium_handler)
    app.add_handler(filters.command("broadcast") & filters.private, broadcast_handler)
