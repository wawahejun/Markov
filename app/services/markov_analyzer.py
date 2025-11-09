import numpy as np
from collections import defaultdict, Counter
import json
from typing import Dict, List, Optional, Tuple
import hashlib

class MarkovChainAnalyzer:
    """
    马尔科夫链用户行为分析器
    """
    
    def __init__(self, order: int = 2):
        self.order = order  # 马尔科夫链阶数
        self.transition_matrix = defaultdict(lambda: defaultdict(float))
        self.state_counts = defaultdict(int)
        self.user_patterns = {}
        
    def add_user_behavior(self, user_id: str, behavior_sequence: List[str]) -> None:
        """
        添加用户行为序列
        
        Args:
            user_id: 用户ID
            behavior_sequence: 行为序列，如 ['click_product', 'add_to_cart', 'purchase']
        """
        if len(behavior_sequence) < self.order + 1:
            return
            
        # 为每个用户创建独立的模式
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = defaultdict(lambda: defaultdict(float))
            
        # 构建转移矩阵
        for i in range(len(behavior_sequence) - self.order):
            current_state = tuple(behavior_sequence[i:i + self.order])
            next_state = behavior_sequence[i + self.order]
            
            self.user_patterns[user_id][current_state][next_state] += 1
            self.transition_matrix[current_state][next_state] += 1
            self.state_counts[current_state] += 1
            
    def calculate_transition_probabilities(self, user_id: Optional[str] = None) -> Dict:
        """
        计算转移概率
        
        Args:
            user_id: 如果指定，计算该用户的个性化概率，否则计算全局概率
            
        Returns:
            转移概率矩阵
        """
        if user_id and user_id in self.user_patterns:
            matrix = self.user_patterns[user_id]
        else:
            matrix = self.transition_matrix
            
        probabilities = {}
        for current_state, transitions in matrix.items():
            total_count = sum(transitions.values())
            if total_count > 0:
                probabilities[current_state] = {
                    next_state: count / total_count 
                    for next_state, count in transitions.items()
                }
                
        return probabilities
        
    def predict_next_behavior(self, user_id: str, current_sequence: List[str]) -> Optional[str]:
        """
        预测用户的下一个行为
        
        Args:
            user_id: 用户ID
            current_sequence: 当前行为序列
            
        Returns:
            预测的行为，如果没有足够的历史数据则返回None
        """
        if len(current_sequence) < self.order:
            return None
            
        current_state = tuple(current_sequence[-self.order:])
        
        # 优先使用用户个性化模型
        if user_id in self.user_patterns and current_state in self.user_patterns[user_id]:
            probabilities = self.user_patterns[user_id][current_state]
        elif current_state in self.transition_matrix:
            probabilities = self.transition_matrix[current_state]
        else:
            return None
            
        # 选择概率最高的行为
        if probabilities:
            return max(probabilities.items(), key=lambda x: x[1])[0]
            
        return None
        
    def generate_behavior_sequence(self, user_id: str, start_behavior: str, length: int = 5) -> List[str]:
        """
        生成用户行为序列
        
        Args:
            user_id: 用户ID
            start_behavior: 起始行为
            length: 序列长度
            
        Returns:
            生成的行为序列
        """
        sequence = [start_behavior]
        current_sequence = [start_behavior]
        
        for _ in range(length - 1):
            next_behavior = self.predict_next_behavior(user_id, current_sequence)
            if next_behavior is None:
                break
                
            sequence.append(next_behavior)
            current_sequence.append(next_behavior)
            
            # 保持序列长度与马尔科夫链阶数一致
            if len(current_sequence) > self.order:
                current_sequence.pop(0)
                
        return sequence
        
    def get_user_behavior_stats(self, user_id: str) -> Dict:
        """
        获取用户行为统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户行为统计信息
        """
        if user_id not in self.user_patterns:
            return {}
            
        user_matrix = self.user_patterns[user_id]
        total_behaviors = sum(sum(transitions.values()) for transitions in user_matrix.values())
        unique_states = len(user_matrix)
        
        # 计算最常见的行为模式
        behavior_counts = Counter()
        for state, transitions in user_matrix.items():
            for behavior, count in transitions.items():
                behavior_counts[behavior] += count
                
        top_behaviors = behavior_counts.most_common(5)
        
        return {
            "total_behaviors": total_behaviors,
            "unique_states": unique_states,
            "top_behaviors": top_behaviors,
            "model_complexity": self._calculate_model_complexity(user_matrix)
        }
        
    def _calculate_model_complexity(self, matrix: Dict) -> float:
        """
        计算模型复杂度
        """
        if not matrix:
            return 0.0
            
        total_transitions = sum(len(transitions) for transitions in matrix.values())
        total_states = len(matrix)
        
        return total_transitions / total_states if total_states > 0 else 0.0
        
    def export_model(self, user_id: Optional[str] = None) -> Dict:
        """
        导出模型数据
        
        Args:
            user_id: 如果指定，导出该用户的模型
            
        Returns:
            模型数据
        """
        model_data = {
            "order": self.order,
            "timestamp": np.datetime64('now').astype(str),
            "model_hash": self._generate_model_hash()
        }
        
        if user_id:
            if user_id in self.user_patterns:
                model_data["user_id"] = user_id
                model_data["transition_matrix"] = dict(self.user_patterns[user_id])
                model_data["stats"] = self.get_user_behavior_stats(user_id)
        else:
            model_data["transition_matrix"] = dict(self.transition_matrix)
            model_data["state_counts"] = dict(self.state_counts)
            
        return model_data
        
    def _generate_model_hash(self) -> str:
        """
        生成模型哈希，用于版本控制
        """
        # 将元组键转换为字符串以便JSON序列化
        serializable_matrix = {}
        for state, transitions in self.transition_matrix.items():
            state_key = str(state) if isinstance(state, tuple) else state
            serializable_matrix[state_key] = dict(transitions)
        
        model_str = json.dumps(serializable_matrix, sort_keys=True)
        return hashlib.sha256(model_str.encode()).hexdigest()[:16]
        
    def import_model(self, model_data: Dict) -> None:
        """
        导入模型数据
        
        Args:
            model_data: 模型数据
        """
        self.order = model_data.get("order", 2)
        
        if "user_id" in model_data:
            user_id = model_data["user_id"]
            self.user_patterns[user_id] = defaultdict(lambda: defaultdict(float))
            for state, transitions in model_data["transition_matrix"].items():
                self.user_patterns[user_id][tuple(state) if isinstance(state, list) else state] = defaultdict(float, transitions)
        else:
            self.transition_matrix = defaultdict(lambda: defaultdict(float))
            for state, transitions in model_data["transition_matrix"].items():
                self.transition_matrix[tuple(state) if isinstance(state, list) else state] = defaultdict(float, transitions)