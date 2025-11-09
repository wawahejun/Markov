from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BehaviorType(str, Enum):
    """用户行为类型"""
    CLICK = "click"
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    PURCHASE = "purchase"
    ADD_TO_CART = "add_to_cart"
    SEARCH = "search"
    FOLLOW = "follow"

class UserBehavior(BaseModel):
    """用户行为模型"""
    user_id: str = Field(..., description="用户ID")
    behavior_type: BehaviorType = Field(..., description="行为类型")
    item_id: str = Field(..., description="项目ID")
    category: Optional[str] = Field(None, description="项目分类")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProfile(BaseModel):
    """用户档案模型"""
    user_id: str = Field(..., description="用户ID")
    preferences: List[str] = Field(default_factory=list, description="用户偏好")
    behavior_history: List[UserBehavior] = Field(default_factory=list, description="行为历史")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    privacy_level: int = Field(default=1, ge=0, le=3, description="隐私等级 (0-3)")
    
class RecommendationItem(BaseModel):
    """推荐项目模型"""
    item_id: str = Field(..., description="项目ID")
    score: float = Field(..., description="推荐分数")
    reason: Optional[str] = Field(None, description="推荐理由")
    category: Optional[str] = Field(None, description="项目分类")
    metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")

class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    user_id: str = Field(..., description="用户ID")
    recommendations: List[RecommendationItem] = Field(..., description="推荐列表")
    algorithm: str = Field(..., description="使用的算法")
    timestamp: datetime = Field(default_factory=datetime.now, description="生成时间")
    privacy_preserved: bool = Field(True, description="是否保护隐私")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="置信度分数")

class BehaviorSequence(BaseModel):
    """行为序列模型"""
    user_id: str = Field(..., description="用户ID")
    behaviors: List[str] = Field(..., description="行为序列")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    
class ModelMetadata(BaseModel):
    """模型元数据模型"""
    model_id: str = Field(..., description="模型ID")
    user_id: Optional[str] = Field(None, description="关联的用户ID")
    model_type: str = Field("markov_chain", description="模型类型")
    version: str = Field("1.0", description="模型版本")
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="模型准确率")
    training_samples: int = Field(0, description="训练样本数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    walrus_hash: Optional[str] = Field(None, description="Walrus存储哈希")
    
class PrivacySettings(BaseModel):
    """隐私设置模型"""
    user_id: str = Field(..., description="用户ID")
    data_encryption: bool = Field(True, description="数据加密")
    anonymization_level: int = Field(2, ge=0, le=3, description="匿名化等级")
    retention_days: int = Field(90, ge=1, le=365, description="数据保留天数")
    share_anonymized_data: bool = Field(False, description="分享匿名化数据")
    
class AnalyticsData(BaseModel):
    """分析数据模型"""
    metric_name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    category: str = Field(..., description="指标分类")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")