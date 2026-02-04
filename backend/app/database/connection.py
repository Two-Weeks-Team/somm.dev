"""MongoDB connection management with Motor async driver"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

client: AsyncIOMotorClient | None = None

# Connection pool settings
CONNECTION_POOL_SETTINGS = {
    "maxPoolSize": 50,
    "minPoolSize": 10,
    "maxIdleTimeMS": 30000,
    "waitQueueTimeoutMS": 30000,
}


async def connect_to_mongo() -> None:
    """Establish connection to MongoDB using Motor async driver"""
    global client
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI, **CONNECTION_POOL_SETTINGS)
        await client.admin.command("ping")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")


async def close_mongo_connection() -> None:
    """Close MongoDB connection and cleanup resources"""
    global client
    if client:
        try:
            client.close()
        except Exception:
            pass
        finally:
            client = None


def get_database() -> AsyncIOMotorDatabase:
    """Get the MongoDB database instance"""
    if client is None:
        raise RuntimeError(
            "Database client not initialized. Call connect_to_mongo first."
        )
    return client[settings.MONGO_DB]


def is_connected() -> bool:
    """Check if the database connection is active"""
    return client is not None
