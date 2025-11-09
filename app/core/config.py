from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Walrus 配置
    WALRUS_RPC_URL: str = os.getenv("WALRUS_RPC_URL", "")
    WALRUS_CONTRACT_ADDRESS: str = os.getenv("WALRUS_CONTRACT_ADDRESS", "")
    WALRUS_STORAGE_NODE: str = os.getenv("WALRUS_STORAGE_NODE", "")
    
    # Sui 网络配置
    SUI_RPC_URL: str = os.getenv("SUI_RPC_URL", "")
    SUI_NETWORK: str = os.getenv("SUI_NETWORK", "testnet")
    
    # 应用配置
    APP_NAME: str = os.getenv("APP_NAME", "MarkovWalrusRecommender")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 数据库配置
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/markov_walrus")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key")
    
    # API 配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    class Config:
        env_file = ".env"

settings = Settings()