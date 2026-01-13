import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.users import get_or_create_user, is_premium
from bot.services.links import get_file_from_token, get_link_by_token
from bot.services.files import format_file_size
from config import Config

logger = logging.getLogger(__name__)

async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    user = message.from_user
    
    # Register user
    await get_or_create_user(
        client.db,
        user.id,
        user.username,
        user.first_name
    )
    
    # Check if this is a file access token
    if len(message.command) > 1:
        token = message.command[1]
        await handle_file_access(client, message, token)
        return
    
    # Normal welcome message with gaali
    premium_status = await is_premium(client.db, user.id)
    status_text = "💎 Premium MC" if premium_status else "🆓 Free User"
    
    welcome_text = (
        f"👋 **हे {user.first_name} भोसडीके!** 😈\n\n"
        f"🔥 **ABS-Stream-Fucker** me welcome MC!\n\n"
        f"**I AM THE ULTIMATE FILE TO LINK CONVERTER BOT!** 🤖\n\n"
        f"📂 **Send karo kuch bhi:**\n"
        f"• 🎬 Video\n"
        f"• 📄 Document\n"
        f"• 🎵 Audio\n"
        f"• 📦 Zip/APK\n\n"
        f"**Mai turant generate karunga:**\n"
        f"• 🚀 High-Speed Download Link\n"
        f"• 📺 HD Streaming Link\n"
        f"• ⚡ No Buffering, No Ads BC!\n\n"
        f"**Teri Status:** {status_text}\n\n"
        f"⚠️ **Ruk mat, file bhej MC!** 🚀"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Stats", callback_data="my_stats"),
            InlineKeyboardButton("💎 Premium", callback_data="premium_info")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("🔥 Channel", url="https://t.me/your_channel")
        ]
    ])
    
    await message.reply_text(welcome_text, reply_markup=buttons)

async def handle_file_access(client: Client, message: Message, token: str):
    """Handle file access via token"""
    try:
        user_id = message.from_user.id
        
        # Get link data
        link_data = await get_link_by_token(client.db, token)
        
        if not link_data:
            await message.reply_text(
                "❌ **Bhenchod invalid link hai!** 🚫\n\n"
                "Ye link:\n"
                "• Delete ho gaya\n"
                "• Expire ho gaya\n"
                "• Galat type kiya tune\n\n"
                "Owner se nayi link maang MC! 💀"
            )
            return
        
        # Get file
        file_doc = await get_file_from_token(client.db, token)
        
        if not file_doc:
            await message.reply_text(
                "❌ **File nahi mili BC!** 😤\n\n"
                "Owner ne delete kar diya hoga!\n"
                "Contact kar usse: /start"
            )
            return
        
        # Check premium status
        user_premium = await is_premium(client.db, user_id)
        
        # Format file info
        file_size = await format_file_size(file_doc["file_size"])
        
        file_info = (
            "**🎉 YOUR LINK GENERATED BC!** ✅\n\n"
            f"📄 **FILE NAME:**\n`{file_doc['file_name']}`\n\n"
            f"📦 **FILE SIZE:** {file_size}\n\n"
            "**TAP TO COPY LINK** 👇\n\n"
            f"🔗 **TELEGRAM:**\n`{link_data.get('telegram_link', 'N/A')}`\n\n"
            f"🎬 **STREAM:**\n`{link_data.get('stream_link', 'N/A')}`\n\n"
            f"📥 **DOWNLOAD:**\n`{link_data.get('download_link', 'N/A')}`\n\n"
        )
        
        if link_data.get("expiry_at"):
            file_info += f"⏰ **Expires:** {link_data['expiry_at'].strftime('%d %b %Y, %I:%M %p')}\n\n"
        else:
            file_info += "⚠️ **NOTE:** Link kabhi expire nahi hoga MC! 🎯\n\n"
        
        # Create buttons
        buttons = []
        
        row1 = [
            InlineKeyboardButton("🎬 STREAM", url=link_data.get("stream_link", "https://t.me/your_channel")),
            InlineKeyboardButton("📥 DOWNLOAD", url=link_data.get("download_link", "https://t.me/your_channel"))
        ]
        buttons.append(row1)
        
        row2 = [
            InlineKeyboardButton("📦 GET FILE", callback_data=f"getfile:{token}")
        ]
        buttons.append(row2)
        
        # Delete button (only for uploader or owner)
        if file_doc["uploader_id"] == user_id or user_id == Config.OWNER_ID:
            row3 = [
                InlineKeyboardButton("🗑 DELETE FILE", callback_data=f"delete:{token}"),
                InlineKeyboardButton("❌ CLOSE", callback_data="close")
            ]
        else:
            row3 = [
                InlineKeyboardButton("❌ CLOSE", callback_data="close")
            ]
        buttons.append(row3)
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Send file info
        await message.reply_text(file_info, reply_markup=keyboard)
    
    except Exception as e:
        logger.error(f"❌ File access handler failed BC: {e}")
        await message.reply_text(
            "❌ **Kuch gadbad ho gayi BC!** 💀\n\n"
            "Try again later ya owner ko bol!\n"
            "/start"
        )

def register(app: Client):
    """Register start handler"""
    app.add_handler(filters.command("start") & filters.private, start_handler)
