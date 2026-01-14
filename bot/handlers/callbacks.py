import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.users import is_premium, get_user_stats
from bot.services.files import get_file_by_id, delete_file, get_user_files, format_file_size
from bot.services.links import get_link_by_token, get_file_from_token, get_user_links, delete_link
from config import Config

logger = logging.getLogger(__name__)

async def callback_handler(client: Client, callback: CallbackQuery):
    """Handle all callback queries"""
    data = callback.data
    user_id = callback.from_user.id
    
    try:
        if data == "close":
            await callback.message.delete()
            return
        
        elif data == "my_stats":
            await handle_my_stats(client, callback)
        
        elif data == "premium_info":
            await handle_premium_info(client, callback)
        
        elif data == "help":
            await handle_help(client, callback)
        
        elif data == "about":
            await handle_about(client, callback)
        
        elif data == "my_files":
            await handle_my_files(client, callback)
        
        elif data == "my_links":
            await handle_my_links(client, callback)
        
        elif data.startswith("getfile:"):
            await handle_get_file(client, callback)
        
        elif data.startswith("delete:"):
            await handle_delete_file(client, callback)
        
        elif data.startswith("confirm_delete:"):
            await handle_confirm_delete(client, callback)
        
        else:
            await callback.answer("❌ Unknown action BC!", show_alert=True)
    
    except Exception as e:
        logger.error(f"❌ Callback handler failed BC: {e}")
        await callback.answer("❌ Error ho gaya MC!", show_alert=True)

async def handle_my_stats(client: Client, callback: CallbackQuery):
    """Handle my_stats callback"""
    user_id = callback.from_user.id
    
    stats = await get_user_stats(client.db, user_id)
    
    if not stats:
        await callback.answer("❌ Stats nahi mile!", show_alert=True)
        return
    
    premium = stats.get("is_premium", False)
    premium_text = "💎 Premium" if premium else "🆓 Free"
    
    stats_text = (
        f"📊 **Teri Stats MC:** 🔥\n\n"
        f"**Status:** {premium_text}\n"
        f"**Files:** {stats.get('total_files', 0)}\n"
        f"**Links:** {stats.get('total_links', 0)}\n\n"
        "Aur kya chahiye? 😎"
    )
    
    await callback.answer(stats_text, show_alert=True)

async def handle_premium_info(client: Client, callback: CallbackQuery):
    """Handle premium_info callback"""
    premium_text = (
        "💎 **Premium Kyu Le MC?** 🔥\n\n"
        "🚀 **Free User:**\n"
        "• Wait time (15 sec)\n"
        "• Links expire (24h)\n"
        "• Slow speed\n"
        "• Basic features\n\n"
        "⚡ **Premium User:**\n"
        "• Zero wait (instant)\n"
        "• Links never expire\n"
        "• Max speed\n"
        "• Priority support\n"
        "• VIP treatment\n\n"
        "**Contact owner:** /start\n\n"
        "Soch mat, invest kar BC! 🔥"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact Owner", url=f"https://t.me/{Config.BOT_USERNAME}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])
    
    await callback.message.edit_text(premium_text, reply_markup=buttons)

async def handle_help(client: Client, callback: CallbackQuery):
    """Handle help callback"""
    help_text = (
        "❓ **Help Menu MC:** 📖\n\n"
        "**Commands:**\n"
        "• /start - Bot start karo\n"
        "• /ping - Bot check karo\n"
        "• /profile - Apni profile dekho\n"
        "• /stats - Bot stats (owner only)\n\n"
        "**How to use:**\n"
        "1. Bot ko file bhejo\n"
        "2. Links mil jayenge\n"
        "3. Stream ya download karo\n"
        "4. Enjoy BC! 🔥\n\n"
        "**Support:** @your_channel"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back", callback_data="back_to_start")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=buttons)

async def handle_about(client: Client, callback: CallbackQuery):
    """Handle about callback"""
    about_text = (
        "ℹ️ **About ABS-Stream-Fucker** 🔥\n\n"
        "**Bot Name:** ABS-Stream-Fucker\n"
        "**Version:** 1.0.0\n"
        "**Developer:** @ABS_Devil\n\n"
        "**Features:**\n"
        "• File to Link converter\n"
        "• HD Streaming\n"
        "• Fast Downloads\n"
        "• Premium system\n"
        "• Secure links\n\n"
        "**Tech Stack:**\n"
        "• Python + Pyrogram\n"
        "• FastAPI\n"
        "• MongoDB\n"
        "• Heroku\n\n"
        "Made with 💀 and gaali!"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back", callback_data="back_to_start")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])
    
    await callback.message.edit_text(about_text, reply_markup=buttons)

async def handle_my_files(client: Client, callback: CallbackQuery):
    """Handle my_files callback"""
    user_id = callback.from_user.id
    
    files = await get_user_files(client.db, user_id, limit=5)
    
    if not files:
        await callback.answer("❌ Abhi tak koi file upload nahi ki!", show_alert=True)
        return
    
    files_text = "📁 **Teri Recent Files MC:**\n\n"
    
    for i, file in enumerate(files, 1):
        size = await format_file_size(file["file_size"])
        files_text += f"{i}. `{file['file_name'][:30]}...`\n   Size: {size}\n\n"
    
    files_text += "Upload karte raho BC! 🔥"
    
    await callback.answer(files_text, show_alert=True)

async def handle_my_links(client: Client, callback: CallbackQuery):
    """Handle my_links callback"""
    user_id = callback.from_user.id
    
    links = await get_user_links(client.db, user_id, limit=5)
    
    if not links:
        await callback.answer("❌ Abhi tak koi link generate nahi kiya!", show_alert=True)
        return
    
    links_text = "🔗 **Teri Recent Links MC:**\n\n"
    
    for i, link in enumerate(links, 1):
        links_text += f"{i}. Token: `{link['token'][:10]}...`\n   Access: {link.get('access_count', 0)} times\n\n"
    
    links_text += "Links share karte raho! 🚀"
    
    await callback.answer(links_text, show_alert=True)

async def handle_get_file(client: Client, callback: CallbackQuery):
    """Handle getfile callback"""
    user_id = callback.from_user.id
    token = callback.data.split(":")[1]
    
    try:
        # Check premium
        user_premium = await is_premium(client.db, user_id)
        
        if not user_premium:
            # Free user - show wait message
            wait_msg = await callback.message.reply_text(
                f"⏰ **Ruk ja BC, itni jaldi kya hai?** 😏\n\n"
                f"Free user hai na tu?\n"
                f"Thoda wait kar le, {Config.FREE_USER_WAIT_TIME} seconds...\n\n"
                f"💎 Premium le le agar jaldi hai!\n\n"
                f"⏳ Countdown: {Config.FREE_USER_WAIT_TIME}"
            )
            
            # Countdown
            for i in range(Config.FREE_USER_WAIT_TIME, 0, -1):
                await asyncio.sleep(1)
                try:
                    await wait_msg.edit_text(
                        f"⏰ **Ruk ja BC, itni jaldi kya hai?** 😏\n\n"
                        f"Free user hai na tu?\n"
                        f"Thoda wait kar le...\n\n"
                        f"💎 Premium le le agar jaldi hai!\n\n"
                        f"⏳ Countdown: {i-1}"
                    )
                except:
                    pass
            
            await wait_msg.delete()
        
        # Get file
        file_doc = await get_file_from_token(client.db, token)
        
        if not file_doc:
            await callback.answer("❌ File nahi mili BC!", show_alert=True)
            return
        
        # Send file
        await callback.message.reply_document(
            document=file_doc["file_id"],
            caption=(
                f"📦 **File mil gayi MC!** ✅\n\n"
                f"**Name:** `{file_doc['file_name']}`\n\n"
                "Enjoy kar bhenchod! 🔥"
            )
        )
        
        await callback.answer("✅ File bhej di!", show_alert=False)
    
    except Exception as e:
        logger.error(f"❌ Get file failed: {e}")
        await callback.answer("❌ Error ho gaya BC!", show_alert=True)

async def handle_delete_file(client: Client, callback: CallbackQuery):
    """Handle delete file callback"""
    token = callback.data.split(":")[1]
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Haan Delete Kar", callback_data=f"confirm_delete:{token}"),
            InlineKeyboardButton("❌ Nahi Rehne De", callback_data="close")
        ]
    ])
    
    await callback.message.reply_text(
        "🗑 **Delete kar dun BC?** ⚠️\n\n"
        "Pakka hai? Wapas nahi aayegi!\n\n"
        "Confirm kar:",
        reply_markup=buttons
    )

async def handle_confirm_delete(client: Client, callback: CallbackQuery):
    """Handle confirm delete callback"""
    user_id = callback.from_user.id
    token = callback.data.split(":")[1]
    
    try:
        # Get link
        link = await get_link_by_token(client.db, token)
        
        if not link:
            await callback.answer("❌ Link nahi mili!", show_alert=True)
            return
        
        # Delete file
        success = await delete_file(client.db, link["file_id"], user_id)
        
        if success:
            await callback.message.edit_text(
                "✅ **File delete ho gayi BC!** 🗑\n\n"
                "Sab links bhi delete ho gaye!\n\n"
                "Next time dhyan se delete karna! 💀"
            )
        else:
            await callback.answer("❌ Delete nahi hua BC!", show_alert=True)
    
    except Exception as e:
        logger.error(f"❌ Confirm delete failed: {e}")
        await callback.answer("❌ Error ho gaya!", show_alert=True)

def register(app: Client):
    """Register callback handler"""
    app.add_handler(filters.callback_query, callback_handler)
