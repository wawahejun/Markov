from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# 全局数据库连接
mongodb_client: Optional[AsyncIOMotorClient] = None
redis_client: Optional[aioredis.Redis] = None

async def init_db():
    """
    初始化数据库连接
    """
    global mongodb_client, redis_client
    
    try:
        # 初始化 MongoDB
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # 测试连接
        await mongodb_client.admin.command('ping')
        logger.info("MongoDB connected successfully")
        
        # 初始化 Redis
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # 测试 Redis 连接
        await redis_client.ping()
        logger.info("Redis connected successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_db():
    """
    关闭数据库连接
    """
    global mongodb_client, redis_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")
        
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

def get_mongodb():
    """
    获取 MongoDB 客户端
    """
    if mongodb_client is None:
        raise RuntimeError("MongoDB not initialized")
    return mongodb_client

def get_redis():
    """
    获取 Redis 客户端
    """
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client

class DatabaseManager:
    """
    数据库管理器
    """
    
    def __init__(self):
        self.mongo_client = None
        self.redis_client = None
        
    async def connect(self):
        """
        连接数据库
        """
        self.mongo_client = get_mongodb()
        self.redis_client = get_redis()
        
    def get_user_collection(self):
        """
        获取用户集合
        """
        return self.mongo_client.markov_walrus.users
        
    def get_behavior_collection(self):
        """
        获取行为集合
        """
        return self.mongo_client.markov_walrus.behaviors
        
    def get_model_collection(self):
        """
        获取模型集合
        """
        return self.mongo_client.markov_walrus.models
        
    def get_recommendation_collection(self):
        """
        获取推荐集合
        """
        return self.mongo_client.markov_walrus.recommendations
        
    async def cache_set(self, key: str, value: str, expire: int = 3600):
        """
        设置缓存
        """
        await self.redis_client.setex(key, expire, value)
        
    async def cache_get(self, key: str) -> Optional[str]:
        """
        获取缓存
        """
        return await self.redis_client.get(key)
        
    async def cache_delete(self, key: str):
        """
        删除缓存
        """
        await self.redis_client.delete(key)