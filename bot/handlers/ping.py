import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime

logger = logging.getLogger(__name__)

async def ping_handler(client: Client, message: Message):
    """Handle /ping command"""
    start_time = datetime.now()
    
    sent_msg = await message.reply_text("🏓 **Pinging BC...**")
    
    end_time = datetime.now()
    ping_time = (end_time - start_time).total_seconds() * 1000
    
    await sent_msg.edit_text(
        f"🏓 **Pong bhenchod!** ⚡\n\n"
        f"**Response Time:** `{ping_time:.2f}ms`\n\n"
        f"Bot ekdum alive hai aur teri maa ki kasam kaam kar raha hai! 🔥\n\n"
        f"**Status:** ✅ Online\n"
        f"**Server:** Heroku\n"
        f"**Uptime:** Running smoothly MC! 💪"
    )

def register(app: Client):
    """Register ping handler"""
    app.add_handler(filters.command("ping") & filters.private, ping_handler)
