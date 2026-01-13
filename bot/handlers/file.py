import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.files import save_file, format_file_size
from bot.services.links import generate_file_links
from bot.services.users import is_premium
from config import Config

logger = logging.getLogger(__name__)

async def file_handler(client: Client, message: Message):
    """Handle file uploads"""
    user = message.from_user
    
    # Extract file info based on message type
    file_obj = None
    file_data = {}
    
    if message.document:
        file_obj = message.document
        file_data = {
            "file_id": file_obj.file_id,
            "file_unique_id": file_obj.file_unique_id,
            "file_name": file_obj.file_name or f"document_{file_obj.file_unique_id}.bin",
            "file_size": file_obj.file_size,
            "mime_type": file_obj.mime_type or "application/octet-stream",
            "uploader_id": user.id,
        }
    elif message.video:
        file_obj = message.video
        file_data = {
            "file_id": file_obj.file_id,
            "file_unique_id": file_obj.file_unique_id,
            "file_name": getattr(file_obj, 'file_name', None) or f"video_{file_obj.file_unique_id}.mp4",
            "file_size": file_obj.file_size,
            "mime_type": file_obj.mime_type or "video/mp4",
            "uploader_id": user.id,
        }
    elif message.audio:
        file_obj = message.audio
        file_data = {
            "file_id": file_obj.file_id,
            "file_unique_id": file_obj.file_unique_id,
            "file_name": getattr(file_obj, 'file_name', None) or f"audio_{file_obj.file_unique_id}.mp3",
            "file_size": file_obj.file_size,
            "mime_type": file_obj.mime_type or "audio/mpeg",
            "uploader_id": user.id,
        }
    else:
        await message.reply_text(
            "❌ **Ye kya bhej diya BC?** 😤\n\n"
            "Send kar:\n"
            "• 🎬 Video\n"
            "• 📄 Document\n"
            "• 🎵 Audio\n"
            "• 📦 Zip/APK\n\n"
            "Dhang se file bhej chutiye! 🔥"
        )
        return
    
    # Processing message
    processing_msg = await message.reply_text(
        "⏳ **Ruk ja BC, kaam chal raha hai...**\n\n"
        "File process ho rahi hai! ⚡"
    )
    
    try:
        # Save file to database
        file_doc = await save_file(client.db, file_data)
        
        # Check premium status
        user_premium = await is_premium(client.db, user.id)
        
        # Generate links
        links = await generate_file_links(client.db, file_doc, user.id, user_premium)
        
        # Format file size
        file_size = await format_file_size(file_doc["file_size"])
        
        # Create response message
        response = (
            "🎉 **Ho gaya taiyaar MC!** ✅\n\n"
            f"📄 **FILE NAME:**\n`{file_doc['file_name']}`\n\n"
            f"📦 **FILE SIZE:** {file_size}\n\n"
            "**TAP TO COPY LINK** 👇\n\n"
            f"🔗 **TELEGRAM:**\n`{links['telegram_link']}`\n\n"
            f"🎬 **STREAM:**\n`{links['stream_link']}`\n\n"
            f"📥 **DOWNLOAD:**\n`{links['download_link']}`\n\n"
        )
        
        if links.get("expiry"):
            response += f"⏰ **Expires:** {links['expiry'].strftime('%d %b %Y, %I:%M %p')}\n\n"
        else:
            response += "⚠️ **NOTE:** Link kabhi expire nahi hoga MC! 🎯\n\n"
        
        # Create buttons
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎬 STREAM", url=links['stream_link']),
                InlineKeyboardButton("📥 DOWNLOAD", url=links['download_link'])
            ],
            [
                InlineKeyboardButton("📦 GET FILE", callback_data=f"getfile:{links['token']}")
            ],
            [
                InlineKeyboardButton("🗑 DELETE FILE", callback_data=f"delete:{links['token']}"),
                InlineKeyboardButton("❌ CLOSE", callback_data="close")
            ]
        ])
        
        # Edit processing message
        await processing_msg.edit_text(response, reply_markup=buttons)
        
        logger.info(f"✅ File processed for user {user.id}: {file_doc['file_name'][:30]}...")
    
    except Exception as e:
        logger.error(f"❌ File processing failed BC: {e}")
        await processing_msg.edit_text(
            f"❌ **Bhenchod kuch gadbad ho gayi!** 💀\n\n"
            f"Error: `{str(e)}`\n\n"
            "Dubara try kar ya owner ko bol!"
        )

def register(app: Client):
    """Register file handler"""
    app.add_handler(
        filters.private & (filters.document | filters.video | filters.audio),
        file_handler
  )
