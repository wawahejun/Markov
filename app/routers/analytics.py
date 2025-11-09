from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.walrus import walrus_storage
from app.services.markov_analyzer import MarkovChainAnalyzer

router = APIRouter()

@router.get("/storage/stats")
async def get_storage_stats():
    """
    获取 Walrus 存储统计信息
    """
    try:
        stats = await walrus_storage.get_storage_stats()
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage stats: {str(e)}")

@router.get("/storage/hash/{data}")
async def generate_data_hash(data: str):
    """
    生成数据哈希
    
    Args:
        data: 要生成哈希的数据
        
    Returns:
        数据哈希
    """
    try:
        # 创建测试数据
        test_data = {"data": data, "timestamp": datetime.now().isoformat()}
        data_hash = walrus_storage.generate_data_hash(test_data)
        
        return {
            "status": "success",
            "data_hash": data_hash,
            "input_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate hash: {str(e)}")

@router.get("/markov/stats/{user_id}")
async def get_markov_stats(user_id: str):
    """
    获取用户马尔科夫链统计信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        马尔科夫链统计信息
    """
    try:
        # 创建临时分析器获取统计信息
        analyzer = MarkovChainAnalyzer(order=2)
        stats = analyzer.get_user_behavior_stats(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "stats": stats,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Markov stats: {str(e)}")

@router.post("/markov/analyze")
async def analyze_behavior_sequence(
    user_id: str,
    behaviors: List[str],
    order: int = Query(2, ge=1, le=5)
):
    """
    分析行为序列
    
    Args:
        user_id: 用户ID
        behaviors: 行为序列
        order: 马尔科夫链阶数
        
    Returns:
        分析结果
    """
    try:
        # 创建分析器
        analyzer = MarkovChainAnalyzer(order=order)
        
        # 添加行为序列
        analyzer.add_user_behavior(user_id, behaviors)
        
        # 计算转移概率
        probabilities = analyzer.calculate_transition_probabilities(user_id)
        
        # 预测下一个行为
        next_behavior = analyzer.predict_next_behavior(user_id, behaviors)
        
        # 生成行为序列
        if behaviors:
            generated_sequence = analyzer.generate_behavior_sequence(
                user_id, behaviors[-1], length=5
            )
        else:
            generated_sequence = []
        
        return {
            "status": "success",
            "user_id": user_id,
            "transition_probabilities": probabilities,
            "predicted_next_behavior": next_behavior,
            "generated_sequence": generated_sequence,
            "sequence_length": len(behaviors),
            "order": order
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze sequence: {str(e)}")

@router.get("/system/health")
async def system_health():
    """
    系统健康检查
    """
    try:
        # 检查各个组件状态
        walrus_status = "unknown"
        try:
            stats = await walrus_storage.get_storage_stats()
            walrus_status = "healthy" if "error" not in stats else "unhealthy"
        except:
            walrus_status = "unhealthy"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "components": {
                "walrus_storage": walrus_status,
                "markov_analyzer": "healthy",
                "api": "healthy"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/system/metrics")
async def system_metrics(
    time_range: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$")
):
    """
    获取系统指标
    
    Args:
        time_range: 时间范围 (1h, 6h, 24h, 7d, 30d)
        
    Returns:
        系统指标
    """
    try:
        # 计算时间范围
        time_ranges = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        delta = time_ranges.get(time_range, timedelta(hours=24))
        start_time = datetime.now() - delta
        
        # 模拟指标数据
        metrics = {
            "time_range": time_range,
            "start_time": start_time,
            "end_time": datetime.now(),
            "total_behaviors": 1250,
            "total_users": 150,
            "total_recommendations": 3200,
            "average_recommendation_score": 0.75,
            "privacy_level_distribution": {
                "level_0": 10,
                "level_1": 45,
                "level_2": 85,
                "level_3": 10
            },
            "storage_usage": {
                "walrus_stored_models": 25,
                "total_storage_size_mb": 15.5
            }
        }
        
        return {
            "status": "success",
            "metrics": metrics,
            "generated_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.post("/privacy/test")
async def test_privacy_levels(
    data: str,
    privacy_levels: List[int] = Query([0, 1, 2, 3])
):
    """
    测试不同隐私级别的数据保护效果
    
    Args:
        data: 测试数据
        privacy_levels: 要测试的隐私级别列表
        
    Returns:
        不同隐私级别的处理结果
    """
    try:
        from app.services.recommender import recommender
        from app.models.schemas import UserBehavior, BehaviorType
        
        results = {}
        
        for level in privacy_levels:
            if level < 0 or level > 3:
                continue
                
            # 创建测试行为
            behavior = UserBehavior(
                user_id="test_user",
                behavior_type=BehaviorType.CLICK,
                item_id=data,
                category="test_category",
                timestamp=datetime.now(),
                metadata={"original_data": data, "test": True}
            )
            
            # 应用隐私保护
            protected_behavior = recommender._apply_privacy_protection(behavior, level)
            
            results[f"privacy_level_{level}"] = {
                "original_user_id": behavior.user_id,
                "processed_user_id": protected_behavior.user_id,
                "original_item_id": behavior.item_id,
                "processed_item_id": protected_behavior.item_id,
                "original_metadata": behavior.metadata,
                "processed_metadata": protected_behavior.metadata
            }
        
        return {
            "status": "success",
            "test_data": data,
            "privacy_test_results": results,
            "tested_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test privacy levels: {str(e)}")