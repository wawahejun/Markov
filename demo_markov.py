#!/usr/bin/env python3
"""
马尔可夫链推荐系统演示脚本
展示如何使用马尔可夫链分析用户行为并生成推荐
"""

import asyncio
from datetime import datetime, timedelta
from app.services.markov_analyzer import MarkovChainAnalyzer
from app.models.schemas import UserBehavior, BehaviorType


def create_sample_user_behaviors():
    """创建示例用户行为数据"""
    user_id = "demo_user_001"
    behaviors = []
    
    # 模拟用户浏览电子产品的行为序列
    base_time = datetime.now()
    
    # 第一天：浏览手机
    behaviors.extend([
        UserBehavior(
            user_id=user_id,
            item_id="phone_001",
            behavior_type=BehaviorType.VIEW,
            timestamp=base_time
        ),
        UserBehavior(
            user_id=user_id,
            item_id="phone_001",
            behavior_type=BehaviorType.CLICK,
            timestamp=base_time + timedelta(minutes=2)
        ),
        UserBehavior(
            user_id=user_id,
            item_id="phone_002",
            behavior_type=BehaviorType.VIEW,
            timestamp=base_time + timedelta(minutes=5)
        ),
        UserBehavior(
            user_id=user_id,
            item_id="phone_001",
            behavior_type=BehaviorType.ADD_TO_CART,
            timestamp=base_time + timedelta(minutes=10)
        )
    ])
    
    # 第二天：浏览耳机
    next_day = base_time + timedelta(days=1)
    behaviors.extend([
        UserBehavior(
            user_id=user_id,
            item_id="earphone_001",
            behavior_type=BehaviorType.VIEW,
            timestamp=next_day
        ),
        UserBehavior(
            user_id=user_id,
            item_id="earphone_001",
            behavior_type=BehaviorType.CLICK,
            timestamp=next_day + timedelta(minutes=3)
        ),
        UserBehavior(
            user_id=user_id,
            item_id="earphone_002",
            behavior_type=BehaviorType.VIEW,
            timestamp=next_day + timedelta(minutes=8)
        ),
        UserBehavior(
            user_id=user_id,
            item_id="earphone_001",
            behavior_type=BehaviorType.PURCHASE,
            timestamp=next_day + timedelta(minutes=15)
        )
    ])
    
    # 第三天：浏览手机壳
    third_day = base_time + timedelta(days=2)
    behaviors.extend([
        UserBehavior(
            user_id=user_id,
            item_id="case_001",
            behavior_type=BehaviorType.VIEW,
            timestamp=third_day
        ),
        UserBehavior(
            user_id=user_id,
            item_id="case_002",
            behavior_type=BehaviorType.VIEW,
            timestamp=third_day + timedelta(minutes=4)
        ),
        UserBehavior(
            user_id=user_id,
            item_id="case_001",
            behavior_type=BehaviorType.CLICK,
            timestamp=third_day + timedelta(minutes=7)
        ),
        UserBehavior(
            user_id=user_id,
            item_id="case_001",
            behavior_type=BehaviorType.PURCHASE,
            timestamp=third_day + timedelta(minutes=12)
        )
    ])
    
    return user_id, behaviors


def demo_basic_markov_analysis():
    """演示基本的马尔可夫链分析"""
    print("🧠 马尔可夫链推荐系统演示")
    print("=" * 50)
    
    # 创建分析器
    analyzer = MarkovChainAnalyzer(order=2)
    
    # 获取示例数据
    user_id, behaviors = create_sample_user_behaviors()
    
    print(f"👤 用户ID: {user_id}")
    print(f"📊 行为数量: {len(behaviors)}")
    
    # 显示原始行为数据
    print("\n📋 用户行为序列:")
    for i, behavior in enumerate(behaviors, 1):
        print(f"  {i}. {behavior.behavior_type.value} - {behavior.item_id} "
              f"({behavior.timestamp.strftime('%Y-%m-%d %H:%M')})")
    
    # 转换为分析格式
    behavior_sequence = [f"{b.behavior_type.value}_{b.item_id}" for b in behaviors]
    
    # 训练模型
    print(f"\n🔍 训练马尔可夫链模型...")
    analyzer.add_user_behavior(user_id, behavior_sequence)
    
    # 计算转移概率
    probabilities = analyzer.calculate_transition_probabilities(user_id)
    print(f"✅ 模型训练完成！")
    print(f"📈 状态数量: {len(probabilities)}")
    
    # 显示转移概率
    print("\n🔄 行为转移概率:")
    for state, transitions in probabilities.items():
        print(f"  当前状态: {state}")
        for next_state, prob in transitions.items():
            print(f"    → {next_state}: {prob:.2%}")
    
    return analyzer, user_id, behavior_sequence


def demo_behavior_prediction(analyzer, user_id):
    """演示行为预测"""
    print("\n🔮 行为预测演示")
    print("=" * 30)
    
    # 测试不同的行为序列
    test_sequences = [
        ["VIEW_phone_001", "CLICK_phone_001"],
        ["VIEW_earphone_001", "CLICK_earphone_001"],
        ["VIEW_case_001", "CLICK_case_001"]
    ]
    
    for seq in test_sequences:
        prediction = analyzer.predict_next_behavior(user_id, seq)
        print(f"  序列: {seq}")
        print(f"  预测下一个行为: {prediction}")
        print()


def demo_sequence_generation(analyzer, user_id):
    """演示序列生成"""
    print("🎯 行为序列生成演示")
    print("=" * 30)
    
    # 从不同的起始行为生成序列
    start_behaviors = ["VIEW_phone_001", "VIEW_earphone_001", "VIEW_case_001"]
    
    for start in start_behaviors:
        generated_sequence = analyzer.generate_behavior_sequence(
            user_id, start, length=4
        )
        print(f"  起始行为: {start}")
        print(f"  生成序列: {generated_sequence}")
        print()


def demo_user_statistics(analyzer, user_id):
    """演示用户统计"""
    print("📊 用户行为统计")
    print("=" * 25)
    
    stats = analyzer.get_user_behavior_stats(user_id)
    
    print(f"  总行为数: {stats.get('total_behaviors', 0)}")
    print(f"  唯一状态数: {stats.get('unique_states', 0)}")
    print(f"  模型复杂度: {stats.get('model_complexity', 0):.2f}")
    
    if 'top_behaviors' in stats:
        print("  热门行为:")
        for behavior, count in stats['top_behaviors']:
            print(f"    {behavior}: {count}次")


def demo_model_export(analyzer, user_id):
    """演示模型导出"""
    print("\n💾 模型导出演示")
    print("=" * 25)
    
    model_data = analyzer.export_model(user_id)
    
    print(f"  模型阶数: {model_data['order']}")
    print(f"  时间戳: {model_data['timestamp']}")
    print(f"  模型哈希: {model_data['model_hash']}")
    print(f"  转移矩阵大小: {len(model_data.get('transition_matrix', {}))}")
    
    return model_data


async def main():
    """主演示函数"""
    try:
        # 基本分析演示
        analyzer, user_id, behavior_sequence = demo_basic_markov_analysis()
        
        # 行为预测演示
        demo_behavior_prediction(analyzer, user_id)
        
        # 序列生成演示
        demo_sequence_generation(analyzer, user_id)
        
        # 用户统计演示
        demo_user_statistics(analyzer, user_id)
        
        # 模型导出演示
        model_data = demo_model_export(analyzer, user_id)
        
        print("\n✨ 演示完成！")
        print("\n📌 总结:")
        print(f"  - 分析了 {len(behavior_sequence)} 个用户行为")
        print(f"  - 构建了 {len(model_data.get('transition_matrix', {}))} 个状态的转移矩阵")
        print(f"  - 成功训练了个性化推荐模型")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())