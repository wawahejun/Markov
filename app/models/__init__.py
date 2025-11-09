# 模型模块初始化文件
from .schemas import (
    UserBehavior, BehaviorType, UserProfile,
    RecommendationItem, RecommendationResponse,
    ModelMetadata, BehaviorSequence, PrivacySettings, AnalyticsData
)

__all__ = [
    "UserBehavior", "BehaviorType", "UserProfile",
    "RecommendationItem", "RecommendationResponse", 
    "ModelMetadata", "BehaviorSequence", "PrivacySettings", "AnalyticsData"
]