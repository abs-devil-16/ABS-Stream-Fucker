import logging
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from bot.services.access import verify_access
from web.errors import error_page

logger = logging.getLogger(__name__)

# Global database connection
db_client = None
db = None

async def init_db():
    """Initialize database connection for web server"""
    global db_client, db
    
    if db is None:
        db_client = AsyncIOMotorClient(Config.DATABASE_URL)
        db = db_client[Config.DATABASE_NAME]
        logger.info("✅ Web server database connected")
    
    return db

async def verify_request(request: Request, token: str, key: str) -> tuple:
    """
    Verify request token and key
    Returns: (success, token_data, error_type)
    """
    try:
        # Initialize database if needed
        db = await init_db()
        
        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Verify access
        success, token_data, error = await verify_access(db, token, key)
        
        if not success:
            logger.warning(f"⚠️ Access denied from {client_ip}: {error}")
            return False, None, error
        
        logger.info(f"✅ Access granted from {client_ip} for token {token[:10]}...")
        return True, token_data, None
    
    except Exception as e:
        logger.error(f"❌ Request verification failed BC: {e}")
        return False, None, "server_error"

async def handle_error(error_type: str) -> HTMLResponse:
    """Handle and return error page"""
    return error_page(error_type, "Access denied")

async def get_db():
    """Get database instance"""
    return await init_db()
