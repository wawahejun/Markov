#!/usr/bin/env python3
"""
基于现有系统架构的高级马尔可夫链推荐系统演示
集成 app/services/markov_analyzer.py 的多阶建模和混合预测功能
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.markov_analyzer import MarkovChainAnalyzer


class EnhancedMarkovChainAnalyzer(MarkovChainAnalyzer):
    """增强版马尔可夫链分析器，支持多阶建模和混合预测"""
    
    def __init__(self, max_order: int = 3):
        super().__init__(order=1)  # 先初始化基础类
        self.max_order = max_order
        self.analyzers = {}  # 存储不同阶数的分析器
        self.user_demographics = {}
        self.item_categories = {}
        self.category_preferences = {}
        
        # 为每个阶数创建独立的分析器
        for order in range(1, max_order + 1):
            self.analyzers[order] = MarkovChainAnalyzer(order=order)
    
    def add_user_demographics(self, user_id: str, demographics: Dict):
        """添加用户人口统计学信息"""
        self.user_demographics[user_id] = demographics
        
    def add_item_categories(self, item_categories: Dict[str, str]):
        """添加物品分类信息"""
        self.item_categories.update(item_categories)
        
    def set_category_preferences(self, user_id: str, preferences: Dict[str, float]):
        """设置用户类别偏好"""
        self.category_preferences[user_id] = preferences
        
    def create_enhanced_user_behaviors(self, num_users: int = 5, 
                                     behaviors_per_user: int = 25) -> Dict[str, List[Dict]]:
        """创建增强的用户行为数据"""
        
        # 定义物品分类
        categories = {
            'phone_001': 'electronics', 'phone_002': 'electronics',
            'laptop_001': 'electronics', 'laptop_002': 'electronics',
            'earphone_001': 'accessories', 'earphone_002': 'accessories',
            'case_001': 'accessories', 'case_002': 'accessories',
            'shirt_001': 'clothing', 'shirt_002': 'clothing',
            'shoes_001': 'clothing', 'shoes_002': 'clothing',
            'book_001': 'books', 'book_002': 'books'
        }
        self.add_item_categories(categories)
        
        all_behaviors = {}
        behavior_types = ['VIEW', 'CLICK', 'ADD_TO_CART', 'PURCHASE', 'RATE', 'SHARE']
        
        for user_id in range(num_users):
            user_id_str = f"user_{user_id:03d}"
            
            # 随机生成用户人口统计学信息
            demographics = {
                'age_group': np.random.choice(['18-25', '25-35', '35-45', '45+']),
                'income_level': np.random.choice(['low', 'medium', 'high']),
                'location': np.random.choice(['urban', 'suburban', 'rural'])
            }
            self.add_user_demographics(user_id_str, demographics)
            
            # 根据收入水平设置类别偏好
            if demographics['income_level'] == 'high':
                preferences = {
                    'electronics': 1.5, 'accessories': 1.2, 'clothing': 0.8, 'books': 0.6
                }
            elif demographics['income_level'] == 'medium':
                preferences = {
                    'electronics': 1.2, 'accessories': 1.0, 'clothing': 1.0, 'books': 0.8
                }
            else:
                preferences = {
                    'electronics': 0.8, 'accessories': 0.9, 'clothing': 1.3, 'books': 1.0
                }
            self.set_category_preferences(user_id_str, preferences)
            
            behaviors = []
            base_time = datetime.now() - timedelta(days=30)
            
            # 生成基于用户特征的行为模式
            for i in range(behaviors_per_user):
                # 根据用户特征调整行为概率
                if demographics['income_level'] == 'high':
                    item_prob = [0.3, 0.25, 0.2, 0.15, 0.1]
                else:
                    item_prob = [0.15, 0.15, 0.2, 0.2, 0.3]
                
                items = list(categories.keys())[:5]
                item_id = np.random.choice(items, p=item_prob)
                
                # 行为类型概率（模拟真实用户行为流程）
                if i == 0:
                    behavior_type = 'VIEW'
                elif i < 5:
                    behavior_type = np.random.choice(['VIEW', 'CLICK'], p=[0.7, 0.3])
                elif i < 15:
                    behavior_type = np.random.choice(['VIEW', 'CLICK', 'ADD_TO_CART'], p=[0.4, 0.3, 0.3])
                else:
                    behavior_type = np.random.choice(behavior_types, p=[0.2, 0.2, 0.2, 0.2, 0.1, 0.1])
                
                behavior_time = base_time + timedelta(
                    days=np.random.randint(0, 30),
                    hours=np.random.randint(0, 24),
                    minutes=np.random.randint(0, 60)
                )
                
                behaviors.append({
                    'user_id': user_id_str,
                    'item_id': item_id,
                    'behavior_type': behavior_type,
                    'category': categories[item_id],
                    'timestamp': behavior_time,
                    'session_id': f"session_{i//5}"
                })
            
            # 按时间排序
            behaviors.sort(key=lambda x: x['timestamp'])
            all_behaviors[user_id_str] = behaviors
            
        return all_behaviors
    
    def build_multi_order_models(self, behaviors: Dict[str, List[Dict]]):
        """构建多阶马尔可夫模型"""
        
        for order in range(1, self.max_order + 1):
            print(f"构建 {order} 阶马尔可夫模型...")
            
            for user_id, user_behaviors in behaviors.items():
                # 提取行为序列
                behavior_sequence = [
                    f"{b['behavior_type']}_{b['item_id']}_{b['category']}"
                    for b in user_behaviors
                ]
                
                # 为每个阶数的分析器添加数据
                if len(behavior_sequence) > order:
                    self.analyzers[order].add_user_behavior(user_id, behavior_sequence)
            
            # 计算转移概率
            print(f"  {order} 阶模型状态数: {len(self.analyzers[order].transition_matrix)}")
    
    def hybrid_prediction(self, user_id: str, recent_behaviors: List[str], 
                         alpha_global: float = 0.3) -> Dict[str, float]:
        """混合预测（全局+个性化）"""
        
        predictions = defaultdict(float)
        
        for order in range(1, self.max_order + 1):
            if len(recent_behaviors) < order:
                continue
            
            # 获取当前分析器
            analyzer = self.analyzers[order]
            
            # 全局模型预测
            global_probs = analyzer.calculate_transition_probabilities()
            current_state = tuple(recent_behaviors[-order:])
            
            if current_state in global_probs:
                weight = 1.0 / order  # 阶数越高权重越小
                for next_state, prob in global_probs[current_state].items():
                    predictions[next_state] += alpha_global * prob * weight
            
            # 个性化模型预测
            user_probs = analyzer.calculate_transition_probabilities(user_id)
            if current_state in user_probs:
                weight = 1.0 / order
                for next_state, prob in user_probs[current_state].items():
                    predictions[next_state] += (1 - alpha_global) * prob * weight
        
        # 归一化概率
        total_prob = sum(predictions.values())
        if total_prob > 0:
            predictions = {state: prob / total_prob for state, prob in predictions.items()}
        
        return dict(sorted(predictions.items(), key=lambda x: x[1], reverse=True))
    
    def category_aware_prediction(self, user_id: str, recent_behaviors: List[str]) -> Dict[str, float]:
        """类别感知预测"""
        
        base_predictions = self.hybrid_prediction(user_id, recent_behaviors)
        
        # 获取用户类别偏好
        preferences = self.category_preferences.get(user_id, {})
        
        # 根据类别偏好调整预测
        adjusted_predictions = {}
        for behavior, prob in base_predictions.items():
            # 提取类别信息
            parts = behavior.split('_')
            if len(parts) >= 3:
                category = parts[2]
                weight = preferences.get(category, 1.0)
                adjusted_predictions[behavior] = prob * weight
        
        # 重新归一化
        total_prob = sum(adjusted_predictions.values())
        if total_prob > 0:
            adjusted_predictions = {state: prob / total_prob 
                                   for state, prob in adjusted_predictions.items()}
        
        return adjusted_predictions
    
    def get_model_statistics(self) -> Dict:
        """获取模型统计信息"""
        
        stats = {
            'model_info': {
                'max_order': self.max_order,
                'total_users': len(self.user_demographics),
                'total_items': len(self.item_categories),
                'categories': list(set(self.item_categories.values()))
            },
            'order_statistics': {},
            'user_statistics': {}
        }
        
        # 各阶模型统计
        for order, analyzer in self.analyzers.items():
            total_states = len(analyzer.transition_matrix)
            total_transitions = sum(len(transitions) for transitions in analyzer.transition_matrix.values())
            
            stats['order_statistics'][f'order_{order}'] = {
                'total_states': total_states,
                'total_transitions': total_transitions,
                'avg_out_degree': total_transitions / total_states if total_states > 0 else 0
            }
        
        # 用户统计
        for user_id in self.user_demographics:
            user_stats = {}
            for order, analyzer in self.analyzers.items():
                if user_id in analyzer.user_patterns:
                    user_matrix = analyzer.user_patterns[user_id]
                    user_stats[f'order_{order}'] = {
                        'unique_states': len(user_matrix),
                        'total_behaviors': sum(sum(transitions.values()) for transitions in user_matrix.values())
                    }
            stats['user_statistics'][user_id] = user_stats
        
        return stats
    
    def export_enhanced_model(self, user_id: Optional[str] = None) -> Dict:
        """导出增强模型数据"""
        
        model_data = {
            'max_order': self.max_order,
            'timestamp': datetime.now().isoformat(),
            'user_demographics': self.user_demographics if not user_id else None,
            'item_categories': self.item_categories,
            'category_preferences': self.category_preferences.get(user_id, {}) if user_id else self.category_preferences
        }
        
        if user_id:
            # 导出特定用户的模型
            user_models = {}
            for order, analyzer in self.analyzers.items():
                if user_id in analyzer.user_patterns:
                    user_models[f'order_{order}'] = analyzer.export_model(user_id)
            model_data['user_models'] = user_models
        else:
            # 导出全局模型
            global_models = {}
            for order, analyzer in self.analyzers.items():
                global_models[f'order_{order}'] = analyzer.export_model()
            model_data['global_models'] = global_models
        
        return model_data


def run_enhanced_demo():
    """运行增强演示"""
    
    print("🚀 基于现有架构的增强马尔可夫链推荐系统")
    print("=" * 60)
    
    # 创建增强分析器
    analyzer = EnhancedMarkovChainAnalyzer(max_order=3)
    
    # 生成增强用户行为数据
    print("📊 生成增强用户行为数据...")
    behaviors = analyzer.create_enhanced_user_behaviors(num_users=5, behaviors_per_user=25)
    
    print(f"✅ 生成了 {len(behaviors)} 个用户的行为数据")
    total_behaviors = sum(len(user_behaviors) for user_behaviors in behaviors.values())
    print(f"📈 总行为数: {total_behaviors}")
    
    # 构建多阶模型
    print("\n🔧 构建多阶马尔可夫模型...")
    analyzer.build_multi_order_models(behaviors)
    
    # 获取模型统计
    stats = analyzer.get_model_statistics()
    print("\n📋 模型统计信息:")
    print(f"  最大阶数: {stats['model_info']['max_order']}")
    print(f"  用户数量: {stats['model_info']['total_users']}")
    print(f"  物品数量: {stats['model_info']['total_items']}")
    print(f"  分类数量: {len(stats['model_info']['categories'])}")
    
    # 显示各阶模型详情
    print("\n🔄 各阶模型详情:")
    for order, order_stats in stats['order_statistics'].items():
        print(f"  {order}:")
        print(f"    状态数: {order_stats['total_states']}")
        print(f"    转移数: {order_stats['total_transitions']}")
        print(f"    平均出度: {order_stats['avg_out_degree']:.2f}")
    
    # 演示混合预测
    print("\n🔮 混合预测演示")
    print("=" * 40)
    
    test_user = "user_000"
    test_sequence = ["VIEW_phone_001_electronics", "CLICK_phone_001_electronics"]
    
    # 不同混合参数的预测
    for alpha in [0.1, 0.3, 0.5, 0.7, 0.9]:
        predictions = analyzer.hybrid_prediction(test_user, test_sequence, alpha_global=alpha)
        top_3 = list(predictions.items())[:3]
        
        print(f"\n  混合参数 α={alpha}:")
        for behavior, prob in top_3:
            print(f"    → {behavior}: {prob:.4f}")
    
    # 演示类别感知预测
    print("\n🎯 类别感知预测演示")
    print("=" * 40)
    
    category_predictions = analyzer.category_aware_prediction(test_user, test_sequence)
    
    print("  基于类别偏好的预测结果:")
    for behavior, prob in list(category_predictions.items())[:5]:
        print(f"    → {behavior}: {prob:.4f}")
    
    # 显示用户人口统计学信息
    print(f"\n👤 测试用户 {test_user} 信息:")
    demo_info = analyzer.user_demographics.get(test_user, {})
    for key, value in demo_info.items():
        print(f"  {key}: {value}")
    
    print(f"\n🎨 类别偏好:")
    prefs = analyzer.category_preferences.get(test_user, {})
    for category, weight in prefs.items():
        print(f"  {category}: {weight}")
    
    return analyzer, behaviors, stats


if __name__ == "__main__":
    analyzer, behaviors, stats = run_enhanced_demo()
    
    print("\n✨ 增强演示完成！")
    print("📊 系统特色:")
    print(f"  - 基于现有架构的模块化设计")
    print(f"  - 支持多阶马尔可夫链建模")
    print(f"  - 集成用户人口统计学信息")
    print(f"  - 实现混合预测算法")
    print(f"  - 支持类别感知推荐")
    print(f"  - 与生产系统完全兼容")