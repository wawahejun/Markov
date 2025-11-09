# 推荐系统API路由
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.recommender import recommender
from app.models.schemas import UserBehavior, RecommendationItem, UserProfile

router = APIRouter()

@router.post("/generate")
async def generate_recommendations(
    user_id: str,
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    privacy_level: int = Query(1, ge=0, le=3)
):
    """
    生成个性化推荐
    
    Args:
        user_id: 用户ID
        category: 推荐分类筛选
        limit: 推荐数量
        privacy_level: 隐私级别
        
    Returns:
        推荐结果列表
    """
    try:
        # 生成推荐
        recommendations = recommender.generate_recommendations(
            user_id=user_id,
            category=category,
            limit=limit,
            privacy_level=privacy_level
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations,
            "total": len(recommendations),
            "privacy_level": privacy_level,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.post("/generate/sequence")
async def generate_recommendations_from_sequence(
    user_id: str,
    behaviors: List[str],
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    privacy_level: int = Query(1, ge=0, le=3)
):
    """
    基于行为序列生成推荐
    
    Args:
        user_id: 用户ID
        behaviors: 行为序列
        category: 推荐分类筛选
        limit: 推荐数量
        privacy_level: 隐私级别
        
    Returns:
        推荐结果列表
    """
    try:
        # 添加行为序列到用户模型
        recommender.markov_analyzer.add_user_behavior(user_id, behaviors)
        
        # 生成推荐
        recommendations = recommender.generate_recommendations(
            user_id=user_id,
            category=category,
            limit=limit,
            privacy_level=privacy_level
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "input_behaviors": behaviors,
            "recommendations": recommendations,
            "total": len(recommendations),
            "privacy_level": privacy_level,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations from sequence: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_recommendations(
    user_id: str,
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    获取用户推荐
    
    Args:
        user_id: 用户ID
        category: 推荐分类筛选
        limit: 推荐数量
        
    Returns:
        推荐结果列表
    """
    try:
        # 获取用户推荐
        recommendations = recommender.get_user_recommendations(user_id, category, limit)
        
        return {
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations,
            "total": len(recommendations),
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user recommendations: {str(e)}")

@router.post("/store-model/{user_id}")
async def store_user_model(user_id: str):
    """
    存储用户模型到 Walrus
    
    Args:
        user_id: 用户ID
        
    Returns:
        存储结果
    """
    try:
        # 存储用户模型
        result = recommender.store_user_model(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "storage_id": result.get("storage_id"),
            "hash": result.get("hash"),
            "stored_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store user model: {str(e)}")

@router.get("/load-model/{user_id}")
async def load_user_model(user_id: str):
    """
    从 Walrus 加载用户模型
    
    Args:
        user_id: 用户ID
        
    Returns:
        加载结果
    """
    try:
        # 加载用户模型
        result = recommender.load_user_model(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "model_loaded": result.get("model_loaded", False),
            "metadata": result.get("metadata", {}),
            "loaded_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load user model: {str(e)}")

@router.get("/model-metadata/{user_id}")
async def get_user_model_metadata(user_id: str):
    """
    获取用户模型元数据
    
    Args:
        user_id: 用户ID
        
    Returns:
        模型元数据
    """
    try:
        # 获取用户模型元数据
        metadata = recommender.get_user_model_metadata(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "metadata": metadata,
            "retrieved_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user model metadata: {str(e)}")

@router.get("/trending")
async def get_trending_recommendations(
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    time_window: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$")
):
    """
    获取热门推荐
    
    Args:
        category: 推荐分类筛选
        limit: 推荐数量
        time_window: 时间窗口
        
    Returns:
        热门推荐结果
    """
    try:
        # 获取热门推荐
        trending = recommender.get_trending_recommendations(category, limit, time_window)
        
        return {
            "status": "success",
            "trending": trending,
            "total": len(trending),
            "time_window": time_window,
            "category": category,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending recommendations: {str(e)}")

@router.get("/categories")
async def get_available_categories():
    """
    获取可用推荐分类
    
    Returns:
        可用分类列表
    """
    try:
        # 获取可用分类
        categories = recommender.get_available_categories()
        
        return {
            "status": "success",
            "categories": categories,
            "total": len(categories),
            "retrieved_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/category/{category}")
async def get_category_recommendations(
    category: str,
    limit: int = Query(10, ge=1, le=50),
    user_id: Optional[str] = Query(None)
):
    """
    获取特定分类推荐
    
    Args:
        category: 分类名称
        limit: 推荐数量
        user_id: 用户ID（可选，用于个性化）
        
    Returns:
        分类推荐结果
    """
    try:
        # 获取分类推荐
        recommendations = recommender.get_category_recommendations(category, limit, user_id)
        
        return {
            "status": "success",
            "category": category,
            "recommendations": recommendations,
            "total": len(recommendations),
            "user_id": user_id,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category recommendations: {str(e)}")

@router.post("/feedback")
async def add_recommendation_feedback(
    user_id: str,
    recommendation_id: str,
    feedback: str = Query(..., regex="^(like|dislike|ignore)$")
):
    """
    添加推荐反馈
    
    Args:
        user_id: 用户ID
        recommendation_id: 推荐ID
        feedback: 反馈类型 (like/dislike/ignore)
        
    Returns:
        反馈结果
    """
    try:
        # 添加推荐反馈
        result = recommender.add_recommendation_feedback(user_id, recommendation_id, feedback)
        
        return {
            "status": "success",
            "user_id": user_id,
            "recommendation_id": recommendation_id,
            "feedback": feedback,
            "feedback_added_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add feedback: {str(e)}")

@router.get("/feedback/{user_id}")
async def get_user_feedback_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=500)
):
    """
    获取用户反馈历史
    
    Args:
        user_id: 用户ID
        limit: 返回数量限制
        
    Returns:
        反馈历史
    """
    try:
        # 获取用户反馈历史
        feedback_history = recommender.get_user_feedback_history(user_id, limit)
        
        return {
            "status": "success",
            "user_id": user_id,
            "feedback_history": feedback_history,
            "total": len(feedback_history),
            "retrieved_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback history: {str(e)}")