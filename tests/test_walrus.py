import pytest
import json
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.core.walrus import WalrusStorage


class TestWalrusStorage:
    """测试Walrus存储系统"""
    
    def setup_method(self):
        """设置测试环境"""
        self.walrus = WalrusStorage()
    
    @pytest.fixture
    def event_loop(self):
        """创建事件循环用于异步测试"""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()
    
    def test_initialization(self):
        """测试初始化"""
        assert self.walrus.storage_node is not None
        assert self.walrus.rpc_url is not None
        assert self.walrus.contract_address is not None
        assert self.walrus.cipher is not None
        assert self.walrus.model_cache == {}
        
    @pytest.mark.asyncio
    async def test_store_data_success(self):
        """测试成功存储数据"""
        data = {"user_id": "test_user", "behavior": "click"}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"hash": "test_storage_hash"}
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await self.walrus.store_data(data)
            
            assert result == "test_storage_hash"
            
    @pytest.mark.asyncio
    async def test_store_data_failure(self):
        """测试存储数据失败"""
        data = {"user_id": "test_user", "behavior": "click"}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Storage error"
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception):
                await self.walrus.store_data(data)
                
    @pytest.mark.asyncio
    async def test_retrieve_data_success(self):
        """测试成功检索数据"""
        storage_hash = "test_storage_hash"
        expected_data = {"user_id": "test_user", "behavior": "click"}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "eyJ1c2VyX2lkIjogInRlc3RfdXNlciIsICJiZWhhdmlvciI6ICJjbGljayJ9"}
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await self.walrus.retrieve_data(storage_hash, decrypt=False)
            
            assert result == expected_data
            
    @pytest.mark.asyncio
    async def test_retrieve_data_not_found(self):
        """测试检索不存在的数据"""
        storage_hash = "non_existent_hash"
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not found"
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception):
                await self.walrus.retrieve_data(storage_hash)
                
    @pytest.mark.asyncio
    async def test_store_user_model(self):
        """测试存储用户模型"""
        user_id = "test_user"
        model_data = {"preferences": {"electronics": 10}, "privacy_level": 1}
        
        with patch.object(self.walrus, 'store_data') as mock_store:
            mock_store.return_value = "test_model_hash"
            
            result = await self.walrus.store_user_model(user_id, model_data)
            
            assert result == "test_model_hash"
            
    @pytest.mark.asyncio
    async def test_retrieve_user_model(self):
        """测试检索用户模型"""
        storage_hash = "test_model_hash"
        expected_model = {"preferences": {"electronics": 10}, "privacy_level": 1}
        
        with patch.object(self.walrus, 'retrieve_data') as mock_retrieve:
            mock_retrieve.return_value = expected_model
            
            result = await self.walrus.retrieve_user_model(storage_hash)
            
            assert result == expected_model
            
    @pytest.mark.asyncio
    async def test_store_behavior_sequence(self):
        """测试存储行为序列"""
        user_id = "test_user"
        sequence = ["VIEW", "CLICK", "PURCHASE"]
        
        with patch.object(self.walrus, 'store_data') as mock_store:
            mock_store.return_value = "test_sequence_hash"
            
            result = await self.walrus.store_behavior_sequence(user_id, sequence)
            
            assert result == "test_sequence_hash"
            
    @pytest.mark.asyncio
    async def test_get_storage_stats(self):
        """测试获取存储统计信息"""
        # 添加一些测试数据到模型缓存
        self.walrus.model_cache = {
            "user1": {"timestamp": datetime.utcnow()},
            "user2": {"timestamp": datetime.utcnow()}
        }
        
        stats = await self.walrus.get_storage_stats()
        
        assert stats["total_models_stored"] == 2
        
    def test_generate_data_hash(self):
        """测试生成数据哈希"""
        data = {"user_id": "test_user", "behavior": "click"}
        
        hash_result = self.walrus.generate_data_hash(data)
        
        assert len(hash_result) == 64  # SHA256哈希长度
        
    def test_generate_data_hash_consistency(self):
        """测试哈希一致性"""
        data = {"user_id": "test_user", "behavior": "click"}
        
        hash1 = self.walrus.generate_data_hash(data)
        hash2 = self.walrus.generate_data_hash(data)
        
        assert hash1 == hash2
        
    def test_generate_data_hash_uniqueness(self):
        """测试哈希唯一性"""
        data1 = {"user_id": "test_user", "behavior": "click"}
        data2 = {"user_id": "test_user", "behavior": "purchase"}
        
        hash1 = self.walrus.generate_data_hash(data1)
        hash2 = self.walrus.generate_data_hash(data2)
        
        assert hash1 != hash2
        
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """测试网络错误处理"""
        data = {"user_id": "test_user", "behavior": "click"}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client.post.side_effect = Exception("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception):
                await self.walrus.store_data(data)
                
    def test_invalid_data_handling(self):
        """测试无效数据处理"""
        # 使用不可序列化的数据
        invalid_data = {"timestamp": datetime.utcnow()}
        
        # 验证_prepare_data方法会抛出异常
        with pytest.raises(Exception):
            self.walrus._prepare_data(invalid_data, encrypt=True)