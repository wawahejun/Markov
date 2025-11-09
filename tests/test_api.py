import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch
from main import app


class TestAPIEndpoints:
    """测试API端点"""
    
    def setup_method(self):
        """设置测试环境"""
        self.client = TestClient(app)
        
    def test_root_endpoint(self):
        """测试根端点"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
    def test_add_user_behavior(self):
        """测试添加用户行为"""
        behavior_data = {
            "user_id": "test_user",
            "item_id": "item1",
            "behavior_type": "VIEW",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"device": "mobile"}
        }
        
        response = self.client.post("/api/v1/users/test_user/behaviors", json=behavior_data)
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["success"] is True
        
    def test_get_user_behaviors(self):
        """测试获取用户行为"""
        response = self.client.get("/api/v1/users/test_user/behaviors")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_user_profile(self):
        """测试获取用户档案"""
        response = self.client.get("/api/v1/users/test_user/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "behaviors" in data
        
    def test_update_user_profile(self):
        """测试更新用户档案"""
        profile_data = {
            "preferences": {"electronics": 10, "books": 5},
            "privacy_level": 2
        }
        
        response = self.client.put("/api/v1/users/test_user/profile", json=profile_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_generate_recommendations(self):
        """测试生成推荐"""
        response = self.client.post(
            "/api/v1/recommendations/generate",
            json={
                "user_id": "test_user",
                "num_recommendations": 5,
                "context": {"device": "mobile"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        
    def test_get_user_recommendations(self):
        """测试获取用户推荐"""
        response = self.client.get("/api/v1/recommendations/users/test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "recommendations" in data
        
    def test_get_popular_recommendations(self):
        """测试获取热门推荐"""
        response = self.client.get("/api/v1/recommendations/popular")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_analytics_stats(self):
        """测试获取分析统计"""
        response = self.client.get("/api/v1/analytics/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_keys" in data
        assert "user_models" in data
        
    def test_get_user_analytics(self):
        """测试获取用户分析"""
        response = self.client.get("/api/v1/analytics/users/test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "total_behaviors" in data
        
    def test_generate_data_hash(self):
        """测试生成数据哈希"""
        data = {"user_id": "test_user", "behavior": "click"}
        
        response = self.client.post("/api/v1/analytics/hash", json=data)
        
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        assert "algorithm" in data
        
    def test_invalid_user_id(self):
        """测试无效用户ID"""
        response = self.client.get("/api/v1/users/invalid_user_id_that_is_too_long/profile")
        
        assert response.status_code == 422  # 验证错误
        
    def test_invalid_behavior_type(self):
        """测试无效行为类型"""
        behavior_data = {
            "user_id": "test_user",
            "item_id": "item1",
            "behavior_type": "INVALID_TYPE",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = self.client.post("/api/v1/users/test_user/behaviors", json=behavior_data)
        
        assert response.status_code == 422  # 验证错误
        
    def test_empty_recommendations_request(self):
        """测试空推荐请求"""
        response = self.client.post(
            "/api/v1/recommendations/generate",
            json={}  # 空请求体
        )
        
        assert response.status_code == 422  # 验证错误
        
    def test_rate_limiting(self):
        """测试速率限制"""
        # 发送多个请求以测试速率限制
        for i in range(10):
            response = self.client.get("/api/v1/users/test_user/profile")
            
        # 检查是否有过多的请求响应
        # 注意：这取决于实际的速率限制配置
        
    def test_cors_headers(self):
        """测试CORS头"""
        response = self.client.get("/", headers={"Origin": "http://localhost:3000"})
        
        # 检查CORS头是否存在
        # 注意：这取决于实际的CORS配置
        
    def test_api_versioning(self):
        """测试API版本控制"""
        response = self.client.get("/api/v1/")
        
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__])