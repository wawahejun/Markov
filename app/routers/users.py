# 用户管理API路由
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.recommender import recommender
from app.models.schemas import UserBehavior, UserProfile, BehaviorType

router = APIRouter()

@router.post("/behaviors")
async def add_user_behavior(behavior: UserBehavior):
    """
    添加用户行为数据
    """
    try:
        # 添加行为到推荐系统
        recommender.add_user_behavior(behavior)
        
        return {
            "status": "success",
            "user_id": behavior.user_id,
            "behavior_type": behavior.behavior_type,
            "timestamp": behavior.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add behavior: {str(e)}")

@router.post("/behaviors/batch")
async def add_user_behaviors_batch(behaviors: List[UserBehavior]):
    """
    批量添加用户行为数据
    """
    try:
        success_count = 0
        for behavior in behaviors:
            try:
                recommender.add_user_behavior(behavior)
                success_count += 1
            except Exception as e:
                print(f"Failed to add behavior for user {behavior.user_id}: {e}")
        
        return {
            "status": "success",
            "total_behaviors": len(behaviors),
            "success_count": success_count,
            "failure_count": len(behaviors) - success_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add behaviors: {str(e)}")

@router.get("/behaviors/{user_id}")
async def get_user_behaviors(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    获取用户行为历史
    """
    try:
        # 获取用户行为数据
        behaviors = recommender.get_user_behaviors(user_id, limit, offset)
        
        return {
            "status": "success",
            "user_id": user_id,
            "behaviors": behaviors,
            "total": len(behaviors),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user behaviors: {str(e)}")

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    获取用户档案
    """
    try:
        profile = recommender.get_user_profile(user_id)
        
        if not profile:
            # 创建默认用户档案
            profile = UserProfile(
                user_id=user_id,
                preferences=[],
                behavior_summary={},
                privacy_level=1,
                created_at=datetime.now()
            )
        
        return {
            "status": "success",
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@router.put("/profile/{user_id}")
async def update_user_profile(user_id: str, profile: UserProfile):
    """
    更新用户档案
    """
    try:
        # 更新用户档案
        updated_profile = recommender.update_user_profile(user_id, profile)
        
        return {
            "status": "success",
            "profile": updated_profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

@router.get("/analysis/{user_id}")
async def get_user_analysis(user_id: str):
    """
    获取用户分析数据
    """
    try:
        # 获取用户分析数据
        analysis = recommender.get_user_analysis(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "analysis": analysis,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analysis: {str(e)}")

@router.delete("/behaviors/{user_id}")
async def clear_user_behaviors(user_id: str):
    """
    清除用户行为数据
    """
    try:
        # 清除用户行为数据
        recommender.clear_user_behaviors(user_id)
        
        return {
            "status": "success",
            "message": f"User behaviors cleared for {user_id}",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear user behaviors: {str(e)}")

@router.get("/behaviors/{user_id}/categories")
async def get_user_behavior_categories(user_id: str):
    """
    获取用户行为分类统计
    """
    try:
        # 获取用户行为数据
        behaviors = recommender.get_user_behaviors(user_id, limit=1000)
        
        # 统计分类
        category_stats = {}
        for behavior in behaviors:
            category = behavior.category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        return {
            "status": "success",
            "user_id": user_id,
            "categories": category_stats,
            "total_behaviors": len(behaviors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get behavior categories: {str(e)}")

@router.get("/behaviors/{user_id}/timeline")
async def get_user_behavior_timeline(
    user_id: str,
    days: int = Query(7, ge=1, le=30)
):
    """
    获取用户行为时间线
    """
    try:
        # 获取用户行为数据
        behaviors = recommender.get_user_behaviors(user_id, limit=1000)
        
        # 按日期分组
        timeline = {}
        for behavior in behaviors:
            date = behavior.timestamp.date()
            if date not in timeline:
                timeline[date] = []
            timeline[date].append({
                "type": behavior.behavior_type,
                "item_id": behavior.item_id,
                "category": behavior.category,
                "timestamp": behavior.timestamp
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "timeline": timeline,
            "total_days": len(timeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get behavior timeline: {str(e)}")