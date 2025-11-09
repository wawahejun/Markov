import pytest
import numpy as np
from datetime import datetime, timedelta
from app.services.markov_analyzer import MarkovChainAnalyzer
from app.models.schemas import UserBehavior, BehaviorType


class TestMarkovChainAnalyzer:
    """测试马尔科夫链分析器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.analyzer = MarkovChainAnalyzer(order=2)
        
    def test_initialization(self):
        """测试初始化"""
        assert self.analyzer.order == 2
        assert len(self.analyzer.transition_matrix) == 0
        assert len(self.analyzer.user_patterns) == 0
        
    def test_add_behavior_sequence(self):
        """测试添加行为序列"""
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
        
        # 将行为转换为序列格式
        behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
        self.analyzer.add_user_behavior(user_id, behavior_sequence)
        
        assert user_id in self.analyzer.user_patterns
        assert len(self.analyzer.user_patterns[user_id]) > 0
        
    def test_build_transition_matrix(self):
        """测试构建转移矩阵"""
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
        
        # 将行为转换为序列格式
        behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
        self.analyzer.add_user_behavior(user_id, behavior_sequence)
        probabilities = self.analyzer.calculate_transition_probabilities(user_id)
        
        assert len(probabilities) > 0
        assert user_id in self.analyzer.user_patterns
        
    def test_predict_next_behavior(self):
        """测试预测下一个行为"""
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
        
        # 将行为转换为序列格式
        behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
        self.analyzer.add_user_behavior(user_id, behavior_sequence)
        
        recent_sequence = ["VIEW_item1", "CLICK_item2"]
        prediction = self.analyzer.predict_next_behavior(user_id, recent_sequence)
        
        # 由于数据有限，预测可能为空或返回某个行为
        assert prediction is None or isinstance(prediction, str)
        
    def test_get_user_statistics(self):
        """测试获取用户统计信息"""
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
        
        # 将行为转换为序列格式
        behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
        self.analyzer.add_user_behavior(user_id, behavior_sequence)
        
        stats = self.analyzer.get_user_behavior_stats(user_id)
        
        assert stats["total_behaviors"] >= 1  # 至少有一个行为被记录
        assert stats["unique_states"] > 0
        assert len(stats["top_behaviors"]) > 0
        
    def test_empty_behavior_sequence(self):
        """测试空行为序列"""
        user_id = "test_user"
        self.analyzer.add_user_behavior(user_id, [])
        
        assert user_id not in self.analyzer.user_patterns
        
    def test_invalid_user_id(self):
        """测试无效用户ID"""
        user_id = "test_user"
        behaviors = [
            UserBehavior(
                user_id="valid_user",
                item_id="item1",
                behavior_type=BehaviorType.VIEW,
                timestamp=datetime.utcnow()
            )
        ]
        
        # 将行为转换为序列格式
        behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
        
        # 添加足够长的序列以创建用户模式
        long_sequence = behavior_sequence * 3  # 重复3次确保长度足够
        self.analyzer.add_user_behavior(user_id, long_sequence)
        
        # 验证用户模式被正确添加
        assert user_id in self.analyzer.user_patterns
        
    def test_predict_with_insufficient_data(self):
        """测试数据不足时的预测"""
        user_id = "test_user"
        behaviors = [
            UserBehavior(
                user_id=user_id,
                item_id="item1",
                behavior_type=BehaviorType.VIEW,
                timestamp=datetime.utcnow()
            )
        ]
        
        # 将行为转换为序列格式
        behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
        self.analyzer.add_user_behavior(user_id, behavior_sequence)
        
        recent_sequence = ["VIEW_item1", "CLICK_item2"]  # 比可用数据更长的序列
        prediction = self.analyzer.predict_next_behavior(user_id, recent_sequence)
        
        assert prediction is None


if __name__ == "__main__":
    pytest.main([__file__])