import httpx
import json
import base64
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet

from app.core.config import settings

logger = logging.getLogger(__name__)

class WalrusStorage:
    """
    Walrus 去中心化存储集成类
    """
    
    def __init__(self):
        self.storage_node = settings.WALRUS_STORAGE_NODE
        self.rpc_url = settings.WALRUS_RPC_URL
        self.contract_address = settings.WALRUS_CONTRACT_ADDRESS
        # 生成有效的Fernet密钥
        key_bytes = settings.SECRET_KEY.encode()
        key_base32 = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b'0'))
        self.cipher = Fernet(key_base32)
        self.model_cache = {}  # 本地模型缓存
        self.storage_nodes = [
            "https://walrus-testnet.storage.googleapis.com",
            "https://walrus-testnet-2.storage.googleapis.com"
        ]
    
    async def store_data(self, data: Dict[str, Any], encrypt: bool = True) -> str:
        """
        将数据存储到 Walrus 网络
        
        Args:
            data: 要存储的数据
            encrypt: 是否加密数据
            
        Returns:
            存储哈希值
        """
        try:
            # 数据预处理
            processed_data = self._prepare_data(data, encrypt)
            
            # 创建存储请求
            storage_request = {
                "data": processed_data,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "app": settings.APP_NAME,
                    "version": settings.APP_VERSION,
                    "encrypted": encrypt
                }
            }
            
            # 发送到 Walrus 网络
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.storage_node}/store",
                    json=storage_request,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    storage_hash = result.get("hash")
                    logger.info(f"Data stored successfully with hash: {storage_hash}")
                    return storage_hash
                else:
                    raise Exception(f"Storage failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error storing data to Walrus: {e}")
            raise
            
    async def retrieve_data(self, storage_hash: str, decrypt: bool = True) -> Dict[str, Any]:
        """
        从 Walrus 检索数据
        
        Args:
            storage_hash: 存储哈希值
            decrypt: 是否解密数据
            
        Returns:
            检索到的数据
        """
        try:
            # 从 Walrus 网络检索
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.storage_node}/retrieve/{storage_hash}",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    data = result.get("data")
                    
                    # 数据后处理
                    return self._process_retrieved_data(data, decrypt)
                else:
                    raise Exception(f"Retrieval failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error retrieving data from Walrus: {e}")
            raise
            
    def _prepare_data(self, data: Dict[str, Any], encrypt: bool) -> str:
        """
        数据预处理
        """
        # 序列化数据
        json_data = json.dumps(data, ensure_ascii=False, sort_keys=True)
        
        if encrypt:
            # 加密数据
            encrypted_data = self.cipher.encrypt(json_data.encode())
            return base64.b64encode(encrypted_data).decode()
        else:
            return base64.b64encode(json_data.encode()).decode()
            
    def _process_retrieved_data(self, data: str, decrypt: bool) -> Dict[str, Any]:
        """
        检索数据后处理
        """
        if decrypt:
            # 解密数据
            encrypted_data = base64.b64decode(data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        else:
            # 直接解码
            decoded_data = base64.b64decode(data.encode()).decode()
            return json.loads(decoded_data)
            
    async def store_user_model(self, user_id: str, model_data: Dict[str, Any]) -> str:
        """
        存储用户模型到 Walrus
        
        Args:
            user_id: 用户ID
            model_data: 模型数据
            
        Returns:
            存储哈希值
        """
        # 添加用户标识和时间戳
        model_metadata = {
            "user_id": user_id,
            "model_type": "markov_chain",
            "created_at": datetime.utcnow().isoformat(),
            "model_data": model_data
        }
        
        return await self.store_data(model_metadata, encrypt=True)
        
    async def retrieve_user_model(self, storage_hash: str) -> Dict[str, Any]:
        """
        从 Walrus 检索用户模型
        
        Args:
            storage_hash: 存储哈希值
            
        Returns:
            用户模型数据
        """
        return await self.retrieve_data(storage_hash, decrypt=True)
        
    async def store_behavior_sequence(self, user_id: str, behavior_sequence: List[str]) -> str:
        """
        存储用户行为序列
        
        Args:
            user_id: 用户ID
            behavior_sequence: 行为序列
            
        Returns:
            存储哈希值
        """
        behavior_data = {
            "user_id": user_id,
            "sequence": behavior_sequence,
            "sequence_length": len(behavior_sequence),
            "stored_at": datetime.utcnow().isoformat()
        }
        
        return await self.store_data(behavior_data, encrypt=True)
        
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息

        Returns:
            存储统计信息
        """
        return {
            "total_models_stored": len(self.model_cache),
            "total_storage_size": sum(len(str(data)) for data in self.model_cache.values()),
            "active_storage_nodes": len(self.storage_nodes),
            "last_sync": datetime.utcnow().isoformat()
        }
            
    def generate_data_hash(self, data: Dict[str, Any]) -> str:
        """
        生成数据哈希，用于完整性验证
        """
        # 规范化数据并生成哈希
        normalized_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(normalized_data.encode()).hexdigest()

# 全局存储实例
walrus_storage = WalrusStorage()

async def init_walrus():
    """
    初始化 Walrus 连接
    """
    try:
        stats = await walrus_storage.get_storage_stats()
        logger.info(f"Walrus storage initialized. Stats: {stats}")
    except Exception as e:
        logger.error(f"Failed to initialize Walrus storage: {e}")
        raise