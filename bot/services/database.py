import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(Config.DATABASE_URL)
            self.db = self.client[Config.DATABASE_NAME]
            
            # Create indexes
            await self.db.users.create_index("user_id", unique=True)
            await self.db.files.create_index("file_unique_id", unique=True)
            await self.db.links.create_index("token", unique=True)
            await self.db.links.create_index("file_id")
            await self.db.links.create_index([("expiry_at", 1)], expireAfterSeconds=0)
            
            logger.info("✅ MongoDB connected BC!")
            return self.db
        
        except Exception as e:
            logger.error(f"❌ Database connection failed MC: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Database connection closed")

# Global database instance
db_instance = Database()
