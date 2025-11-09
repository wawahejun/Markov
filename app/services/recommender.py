from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from cryptography.fernet import Fernet
import base64
import hashlib
import logging
from datetime import datetime, timedelta

from app.services.markov_analyzer import MarkovChainAnalyzer
from app.core.walrus import walrus_storage
from app.models.schemas import (
    UserBehavior, RecommendationItem, RecommendationResponse, 
    BehaviorType, UserProfile
)

logger = logging.getLogger(__name__)

class PrivacyPreservingRecommender:
    """
    隐私保护推荐系统
    """
    
    def __init__(self):
        self.markov_analyzer = MarkovChainAnalyzer(order=2)
        self.user_profiles = {}
        self.encryption_key = self._generate_encryption_key()
        self.cipher = Fernet(base64.urlsafe_b64encode(self.encryption_key))
        
    def _generate_encryption_key(self) -> bytes:
        """
        生成加密密钥
        """
        key = hashlib.sha256(b"markov-walrus-recommender").digest()
        return key[:32].ljust(32, b'0')
        
    def add_user_behavior(self, user_id: str, behavior: UserBehavior, 
                         privacy_level: int = 2) -> None:
        """
        添加用户行为，支持不同隐私级别
        
        Args:
            user_id: 用户ID
            behavior: 用户行为
            privacy_level: 隐私级别 (0-3)
                0: 无隐私保护
                1: 基础匿名化
                2: 差分隐私
                3: 完全加密
        """
        try:
            # 根据隐私级别处理数据
            processed_behavior = self._apply_privacy_protection(behavior, privacy_level)
            
            # 添加到马尔科夫链分析器
            behavior_sequence = self._behavior_to_sequence(processed_behavior)
            self.markov_analyzer.add_user_behavior(user_id, behavior_sequence)
            
            # 更新用户档案
            self._update_user_profile(user_id, processed_behavior, privacy_level)
            
            logger.info(f"Added behavior for user {user_id} with privacy level {privacy_level}")
            
        except Exception as e:
            logger.error(f"Error adding user behavior: {e}")
            raise
            
    def _apply_privacy_protection(self, behavior: UserBehavior, 
                                 privacy_level: int) -> UserBehavior:
        """
        应用隐私保护
        """
        if privacy_level == 0:
            # 无隐私保护，返回原始数据
            return behavior
            
        elif privacy_level == 1:
            # 基础匿名化：移除直接标识符
            return UserBehavior(
                user_id=self._anonymize_user_id(behavior.user_id),
                behavior_type=behavior.behavior_type,
                item_id=behavior.item_id,
                category=behavior.category,
                timestamp=behavior.timestamp,
                metadata=self._remove_identifiers(behavior.metadata)
            )
            
        elif privacy_level == 2:
            # 差分隐私：添加噪声
            noisy_behavior = self._add_differential_privacy_noise(behavior)
            return noisy_behavior
            
        elif privacy_level == 3:
            # 完全加密：加密敏感数据
            return self._encrypt_behavior_data(behavior)
            
        else:
            return behavior
            
    def _anonymize_user_id(self, user_id: str) -> str:
        """
        匿名化用户ID
        """
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
    def _remove_identifiers(self, metadata: Optional[Dict]) -> Optional[Dict]:
        """
        移除标识符
        """
        if not metadata:
            return metadata
            
        # 移除可能包含个人信息的字段
        sensitive_fields = ['email', 'phone', 'address', 'name', 'ip']
        filtered_metadata = {k: v for k, v in metadata.items() 
                           if k.lower() not in sensitive_fields}
        return filtered_metadata
        
    def _add_differential_privacy_noise(self, behavior: UserBehavior) -> UserBehavior:
        """
        添加差分隐私噪声
        """
        # 这里可以实现更复杂的差分隐私算法
        # 简单示例：对时间戳添加随机噪声
        import random
        
        noise_minutes = random.randint(-30, 30)
        noisy_timestamp = behavior.timestamp + timedelta(minutes=noise_minutes)
        
        return UserBehavior(
            user_id=self._anonymize_user_id(behavior.user_id),
            behavior_type=behavior.behavior_type,
            item_id=behavior.item_id,
            category=behavior.category,
            timestamp=noisy_timestamp,
            metadata=behavior.metadata
        )
        
    def _encrypt_behavior_data(self, behavior: UserBehavior) -> UserBehavior:
        """
        加密行为数据
        """
        # 加密敏感字段
        encrypted_metadata = {}
        if behavior.metadata:
            for key, value in behavior.metadata.items():
                if isinstance(value, str) and len(value) > 0:
                    encrypted_value = self.cipher.encrypt(value.encode()).decode()
                    encrypted_metadata[key] = encrypted_value
                else:
                    encrypted_metadata[key] = value
                    
        return UserBehavior(
            user_id=self._anonymize_user_id(behavior.user_id),
            behavior_type=behavior.behavior_type,
            item_id=self.cipher.encrypt(behavior.item_id.encode()).decode(),
            category=self.cipher.encrypt(behavior.category.encode()).decode() if behavior.category else None,
            timestamp=behavior.timestamp,
            metadata=encrypted_metadata
        )
        
    def _behavior_to_sequence(self, behavior: UserBehavior) -> List[str]:
        """
        将行为转换为序列格式
        """
        return [f"{behavior.behavior_type.value}_{behavior.item_id}"]
        
    def _update_user_profile(self, user_id: str, behavior: UserBehavior, 
                           privacy_level: int) -> None:
        """
        更新用户档案
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'behaviors': [],
                'preferences': {},
                'privacy_level': privacy_level,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
        profile = self.user_profiles[user_id]
        profile['behaviors'].append(behavior)
        profile['updated_at'] = datetime.utcnow()
        
        # 更新偏好（基于行为类型和分类）
        if behavior.category:
            if behavior.category not in profile['preferences']:
                profile['preferences'][behavior.category] = 0
            profile['preferences'][behavior.category] += 1
            
    async def generate_recommendations(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 10,
        privacy_level: int = 1
    ) -> List[Dict[str, Any]]:
        """
        生成隐私保护的推荐
        
        Args:
            user_id: 用户ID
            num_recommendations: 推荐数量
            context: 上下文信息
            
        Returns:
            推荐响应
        """
        try:
            # 获取用户最近的行為序列
            recent_behaviors = self._get_recent_behaviors(user_id)
            
            if not recent_behaviors:
                # 如果没有历史行为，返回热门推荐
                return await self._generate_popular_recommendations(user_id, num_recommendations)
                
            # 使用马尔科夫链预测下一个行为
            behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in recent_behaviors]
            
            recommendations = []
            
            # 生成多个推荐
            for _ in range(num_recommendations):
                next_behavior = self.markov_analyzer.predict_next_behavior(user_id, behavior_sequence)
                if next_behavior:
                    # 解析预测的行为
                    behavior_type, item_id = self._parse_predicted_behavior(next_behavior)
                    
                    # 计算推荐分数
                    score = self._calculate_recommendation_score(
                        user_id, behavior_type, item_id, recent_behaviors
                    )
                    
                    recommendation = RecommendationItem(
                        item_id=item_id,
                        score=score,
                        reason=f"基于您的{behavior_type}行为模式",
                        category=self._get_item_category(item_id),
                        metadata={"predicted_behavior": behavior_type}
                    )
                    
                    recommendations.append(recommendation)
                    
                    # 更新序列以生成下一个推荐
                    behavior_sequence.append(next_behavior)
                    if len(behavior_sequence) > self.markov_analyzer.order + 1:
                        behavior_sequence.pop(0)
                        
            # 按分数排序
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return RecommendationResponse(
                user_id=user_id,
                recommendations=recommendations[:num_recommendations],
                algorithm="privacy_preserving_markov_chain",
                privacy_preserved=True,
                confidence_score=self._calculate_confidence_score(user_id, recommendations)
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
            
    def _get_recent_behaviors(self, user_id: str, limit: int = 10) -> List[UserBehavior]:
        """
        获取用户最近的行为
        """
        if user_id not in self.user_profiles:
            return []
            
        profile = self.user_profiles[user_id]
        behaviors = profile['behaviors']
        
        # 按时间排序并返回最近的
        behaviors.sort(key=lambda x: x.timestamp, reverse=True)
        return behaviors[:limit]
        
    def _parse_predicted_behavior(self, predicted_behavior: str) -> Tuple[str, str]:
        """
        解析预测的行为
        """
        parts = predicted_behavior.split('_', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "unknown", predicted_behavior
        
    def _calculate_recommendation_score(self, user_id: str, behavior_type: str, 
                                      item_id: str, recent_behaviors: List[UserBehavior]) -> float:
        """
        计算推荐分数
        """
        base_score = 0.5
        
        # 基于行为类型的权重
        behavior_weights = {
            BehaviorType.PURCHASE: 1.0,
            BehaviorType.ADD_TO_CART: 0.8,
            BehaviorType.LIKE: 0.6,
            BehaviorType.CLICK: 0.4,
            BehaviorType.VIEW: 0.3
        }
        
        weight = behavior_weights.get(BehaviorType(behavior_type), 0.5)
        
        # 基于时间衰减
        if recent_behaviors:
            time_factor = self._calculate_time_factor(recent_behaviors[0].timestamp)
        else:
            time_factor = 1.0
            
        # 基于用户偏好的调整
        preference_factor = self._calculate_preference_factor(user_id, item_id)
        
        return base_score * weight * time_factor * preference_factor
        
    def _calculate_time_factor(self, timestamp: datetime, half_life_days: int = 7) -> float:
        """
        计算时间衰减因子
        """
        days_diff = (datetime.utcnow() - timestamp).days
        return np.exp(-days_diff / half_life_days)
        
    def _calculate_preference_factor(self, user_id: str, item_id: str) -> float:
        """
        计算用户偏好因子
        """
        if user_id not in self.user_profiles:
            return 1.0
            
        profile = self.user_profiles[user_id]
        preferences = profile['preferences']
        
        # 这里可以实现更复杂的偏好计算
        # 简单示例：基于分类的偏好
        total_behaviors = sum(preferences.values())
        if total_behaviors == 0:
            return 1.0
            
        # 假设我们可以获取项目的分类
        item_category = self._get_item_category(item_id)
        if item_category in preferences:
            return 1.0 + (preferences[item_category] / total_behaviors)
            
        return 1.0
        
    def _get_item_category(self, item_id: str) -> str:
        """
        获取项目分类（模拟）
        """
        # 这里可以实现真实的项目分类获取
        # 现在使用简单的哈希分类
        categories = ['electronics', 'clothing', 'books', 'food', 'sports']
        category_index = hash(item_id) % len(categories)
        return categories[category_index]
        
    async def _generate_popular_recommendations(self, user_id: str, 
                                               num_recommendations: int) -> RecommendationResponse:
        """
        生成热门推荐（当没有用户历史时）
        """
        # 模拟热门项目
        popular_items = [
            {"item_id": "item_001", "category": "electronics", "score": 0.8},
            {"item_id": "item_002", "category": "clothing", "score": 0.7},
            {"item_id": "item_003", "category": "books", "score": 0.6},
            {"item_id": "item_004", "category": "food", "score": 0.5},
            {"item_id": "item_005", "category": "sports", "score": 0.4}
        ]
        
        recommendations = []
        for item in popular_items[:num_recommendations]:
            recommendation = RecommendationItem(
                item_id=item["item_id"],
                score=item["score"],
                reason="热门推荐",
                category=item["category"]
            )
            recommendations.append(recommendation)
            
        return RecommendationResponse(
            user_id=user_id,
            recommendations=recommendations,
            algorithm="popular_items",
            privacy_preserved=True,
            confidence_score=0.3  # 低置信度，因为是通用推荐
        )
        
    def _calculate_confidence_score(self, user_id: str, 
                                   recommendations: List[RecommendationItem]) -> float:
        """
        计算置信度分数
        """
        if not recommendations:
            return 0.0
            
        # 基于推荐数量和用户历史行为计算置信度
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            behavior_count = len(profile['behaviors'])
            
            # 更多历史行为 = 更高置信度
            history_factor = min(behavior_count / 50, 1.0)  # 50个行为达到最大置信度
            
            # 基于推荐分数的置信度
            avg_score = sum(r.score for r in recommendations) / len(recommendations)
            
            return (history_factor + avg_score) / 2
        else:
            return 0.3  # 新用户的默认置信度
            
    async def store_model_to_walrus(self, user_id: str) -> str:
        """
        将用户模型存储到 Walrus
        """
        if user_id not in self.user_profiles:
            raise ValueError(f"User {user_id} not found")
            
        # 导出马尔科夫链模型
        model_data = self.markov_analyzer.export_model(user_id)
        
        # 存储到 Walrus
        storage_hash = await walrus_storage.store_user_model(user_id, model_data)
        
        logger.info(f"Stored model for user {user_id} to Walrus with hash: {storage_hash}")
        return storage_hash
        
    async def load_model_from_walrus(self, storage_hash: str) -> Dict[str, Any]:
        """
        从 Walrus 加载模型
        """
        return await walrus_storage.retrieve_user_model(storage_hash)

# 全局推荐器实例
recommender = PrivacyPreservingRecommender()