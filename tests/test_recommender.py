import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.recommender import PrivacyPreservingRecommender
from app.models.schemas import UserBehavior, BehaviorType, UserProfile


class TestPrivacyPreservingRecommender:
    """测试隐私保护推荐系统"""
    
    def setup_method(self):
        """设置测试环境"""
        self.recommender = PrivacyPreservingRecommender(
            walrus_storage=Mock(),
            markov_analyzer=Mock()
        )
        
    def test_initialization(self):
        """测试初始化"""
        assert self.recommender.walrus_storage is not None
        assert self.recommender.markov_analyzer is not None
        assert self.recommender.user_profiles == {}
        
    def test_add_user_behavior(self):
        """测试添加用户行为"""
        user_id = "test_user"
        behavior = UserBehavior(
            user_id=user_id,
            item_id="item1",
            behavior_type=BehaviorType.VIEW,
            timestamp=datetime.utcnow()
        )
        
        result = self.recommender.add_user_behavior(user_id, behavior)
        
        assert result is True
        assert user_id in self.recommender.user_profiles
        
    def test_get_user_profile(self):
        """测试获取用户档案"""
        user_id = "test_user"
        behavior = UserBehavior(
            user_id=user_id,
            item_id="item1",
            behavior_type=BehaviorType.VIEW,
            timestamp=datetime.utcnow()
        )
        
        self.recommender.add_user_behavior(user_id, behavior)
        profile = self.recommender.get_user_profile(user_id)
        
        assert profile is not None
        assert profile.user_id == user_id
        assert len(profile.behaviors) == 1
        
    def test_update_user_profile(self):
        """测试更新用户档案"""
        user_id = "test_user"
        profile_data = {
            "preferences": {"electronics": 10, "books": 5},
            "privacy_level": 2
        }
        
        result = self.recommender.update_user_profile(user_id, profile_data)
        
        assert result is True
        assert user_id in self.recommender.user_profiles
        
    def test_generate_recommendations_no_history(self):
        """测试无历史记录时的推荐生成"""
        user_id = "test_user"
        
        # 模拟没有历史行为的情况
        self.recommender._get_recent_behaviors = Mock(return_value=[])
        
        with patch.object(self.recommender, '_generate_popular_recommendations') as mock_popular:
            mock_popular.return_value = {
                "user_id": user_id,
                "recommendations": [],
                "algorithm": "popular_items",
                "privacy_preserved": True,
                "confidence_score": 0.3
            }
            
            result = self.recommender.generate_recommendations(user_id, num_recommendations=5)
            
            assert result is not None
            assert result["user_id"] == user_id
            mock_popular.assert_called_once()
            
    def test_generate_recommendations_with_history(self):
        """测试有历史记录时的推荐生成"""
        user_id = "test_user"
        
        # 模拟有历史行为的情况
        mock_behaviors = [
            UserBehavior(
                user_id=user_id,
                item_id="item1",
                behavior_type=BehaviorType.VIEW,
                timestamp=datetime.utcnow()
            ),
            UserBehavior(
                user_id=user_id,
                item_id="item2",
                behavior_type=BehaviorType.CLICK,
                timestamp=datetime.utcnow() + timedelta(minutes=1)
            )
        ]
        
        self.recommender._get_recent_behaviors = Mock(return_value=mock_behaviors)
        self.recommender.markov_analyzer.predict_next_behavior = Mock(return_value="PURCHASE_item3")
        
        result = self.recommender.generate_recommendations(user_id, num_recommendations=2)
        
        assert result is not None
        assert result["user_id"] == user_id
        assert result["algorithm"] == "privacy_preserving_markov_chain"
        assert result["privacy_preserved"] is True
        
    def test_get_recent_behaviors(self):
        """测试获取最近行为"""
        user_id = "test_user"
        behaviors = [
            UserBehavior(
                user_id=user_id,
                item_id="item1",
                behavior_type=BehaviorType.VIEW,
                timestamp=datetime.utcnow()
            ),
            UserBehavior(
                user_id=user_id,
                item_id="item2",
                behavior_type=BehaviorType.CLICK,
                timestamp=datetime.utcnow() + timedelta(minutes=1)
            ),
            UserBehavior(
                user_id=user_id,
                item_id="item3",
                behavior_type=BehaviorType.PURCHASE,
                timestamp=datetime.utcnow() + timedelta(minutes=2)
            )
        ]
        
        # 添加行为到用户档案
        for behavior in behaviors:
            self.recommender.add_user_behavior(user_id, behavior)
            
        recent_behaviors = self.recommender._get_recent_behaviors(user_id, limit=2)
        
        assert len(recent_behaviors) == 2
        assert recent_behaviors[0].item_id == "item3"  # 最新的
        assert recent_behaviors[1].item_id == "item2"  # 第二新的
        
    def test_calculate_recommendation_score(self):
        """测试推荐分数计算"""
        user_id = "test_user"
        recent_behaviors = [
            UserBehavior(
                user_id=user_id,
                item_id="item1",
                behavior_type=BehaviorType.VIEW,
                timestamp=datetime.utcnow()
            )
        ]
        
        score = self.recommender._calculate_recommendation_score(
            user_id, "PURCHASE", "item2", recent_behaviors
        )
        
        assert 0 <= score <= 1.0
        
    def test_calculate_time_factor(self):
        """测试时间因子计算"""
        recent_timestamp = datetime.utcnow()
        old_timestamp = datetime.utcnow() - timedelta(days=14)
        
        recent_factor = self.recommender._calculate_time_factor(recent_timestamp)
        old_factor = self.recommender._calculate_time_factor(old_timestamp)
        
        assert recent_factor > old_factor  # 最近的时间因子应该更大
        
    def test_calculate_preference_factor(self):
        """测试偏好因子计算"""
        user_id = "test_user"
        
        # 设置用户偏好
        self.recommender.user_profiles[user_id] = {
            "behaviors": [],
            "preferences": {"electronics": 10, "books": 5},
            "privacy_level": 1
        }
        
        # 测试偏好的分类
        factor_preferred = self.recommender._calculate_preference_factor(
            user_id, "electronics_item"
        )
        
        # 测试不偏好的分类
        factor_not_preferred = self.recommender._calculate_preference_factor(
            user_id, "sports_item"
        )
        
        assert factor_preferred > factor_not_preferred
        
    def test_store_user_model(self):
        """测试存储用户模型"""
        user_id = "test_user"
        model_data = {"preferences": {"electronics": 10}, "privacy_level": 1}
        
        self.recommender.walrus_storage.store_user_model = Mock(return_value=True)
        
        result = self.recommender.store_user_model(user_id, model_data)
        
        assert result is True
        self.recommender.walrus_storage.store_user_model.assert_called_once_with(
            user_id, model_data
        )
        
    def test_retrieve_user_model(self):
        """测试检索用户模型"""
        user_id = "test_user"
        expected_model = {"preferences": {"electronics": 10}, "privacy_level": 1}
        
        self.recommender.walrus_storage.retrieve_user_model = Mock(
            return_value=expected_model
        )
        
        result = self.recommender.retrieve_user_model(user_id)
        
        assert result == expected_model
        self.recommender.walrus_storage.retrieve_user_model.assert_called_once_with(user_id)


if __name__ == "__main__":
    pytest.main([__file__])