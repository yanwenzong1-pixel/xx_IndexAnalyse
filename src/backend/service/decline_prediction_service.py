"""
业务逻辑层 - 下跌概率预测服务
封装下跌概率预测业务逻辑
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


class DeclinePredictionService:
    """下跌概率预测服务"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def predict_downside_probability(self) -> Dict[str, float]:
        """
        预测下跌概率
        
        Returns:
            包含 T+1 和 T+5 下跌概率的字典
        """
        if self.df is None or len(self.df) == 0:
            return {
                'prob_t1': 0.0,
                'prob_t5': 0.0
            }
        
        df = self.df.copy()
        
        # 基础风险分数
        base_risk = 0.5
        
        # 考虑近期涨跌幅
        recent_1d = df['change_pct'].iloc[-1]
        recent_5d = df['change_pct'].tail(5).sum()
        
        if recent_1d > 5:
            base_risk += 0.1
        elif recent_1d > 3:
            base_risk += 0.05
        elif recent_1d < -3:
            base_risk -= 0.1
        
        if recent_5d > 10:
            base_risk += 0.15
        elif recent_5d > 5:
            base_risk += 0.08
        
        # 考虑波动率
        volatility = df['change_pct'].rolling(20).std().iloc[-1]
        if volatility > 5:
            base_risk += 0.1
        
        # 考虑趋势
        if len(df) > 20:
            ma5 = df['close'].rolling(5).mean().iloc[-1]
            ma20 = df['close'].rolling(20).mean().iloc[-1]
            
            if ma5 < ma20:
                base_risk += 0.1
        
        # 限制在 0-1 之间
        prob_t1 = max(0.0, min(1.0, base_risk))
        prob_t5 = max(0.0, min(1.0, base_risk * 1.1))
        
        return {
            'prob_t1': round(prob_t1, 4),
            'prob_t5': round(prob_t5, 4)
        }
    
    def calculate_expected_decline(self, prob_t1: float, prob_t5: float) -> Dict[str, Any]:
        """
        计算预期跌幅
        
        Args:
            prob_t1: T+1 下跌概率
            prob_t5: T+5 下跌概率
            
        Returns:
            包含预期跌幅的字典
        """
        # 基础跌幅
        base_decline = 0.02
        
        # 根据概率调整
        t1_decline = base_decline + prob_t1 * 0.05
        t5_decline = base_decline * 2 + prob_t5 * 0.08
        
        # 添加波动区间
        t1_lower = max(0, t1_decline - 0.01)
        t1_upper = t1_decline + 0.02
        t5_lower = max(0, t5_decline - 0.02)
        t5_upper = t5_decline + 0.03
        
        return {
            't1': {
                'expected_decline': round(t1_decline * 100, 2),
                'lower_bound': round(t1_lower * 100, 2),
                'upper_bound': round(t1_upper * 100, 2)
            },
            't5': {
                'expected_decline': round(t5_decline * 100, 2),
                'lower_bound': round(t5_lower * 100, 2),
                'upper_bound': round(t5_upper * 100, 2)
            }
        }
