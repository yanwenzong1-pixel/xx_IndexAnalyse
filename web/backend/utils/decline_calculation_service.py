"""
预期跌幅计算模块
基于下跌概率计算预期跌幅及其置信区间
"""

import numpy as np


def calculate_expected_decline_t1(prob_t1, volatility_20d):
    """
    计算次日 (T+1) 预期跌幅
    
    Args:
        prob_t1: 次日下跌概率
        volatility_20d: 20日波动率
        
    Returns:
        dict: 包含预期跌幅和置信区间的字典
    """
    # 分段线性模型
    if prob_t1 < 0.3:
        expected_decline = 0.3
        confidence_interval = (0.1, 0.5)
    elif 0.3 <= prob_t1 < 0.5:
        expected_decline = 0.6
        confidence_interval = (0.3, 0.9)
    elif 0.5 <= prob_t1 < 0.7:
        expected_decline = 1.2
        confidence_interval = (0.7, 1.7)
    else:
        expected_decline = 2.0
        confidence_interval = (1.2, 2.8)
    
    # 根据波动率调整
    adjustment_factor = max(0.5, min(2.0, volatility_20d / 2.0))  # 基准波动率为2%
    # expected_decline/置信区间均为“正值跌幅百分比”
    expected_decline *= adjustment_factor
    confidence_interval = (
        confidence_interval[0] * adjustment_factor,
        confidence_interval[1] * adjustment_factor
    )
    
    return {
        'expected_decline': expected_decline,
        'confidence_interval': confidence_interval,
        'lower_bound': confidence_interval[0],
        'upper_bound': confidence_interval[1]
    }


def calculate_expected_decline_t5(prob_t5, prob_t1, volatility_20d):
    """
    计算5日内 (T+5) 预期跌幅
    
    Args:
        prob_t5: 5日内下跌概率
        prob_t1: 次日下跌概率
        volatility_20d: 20日波动率
        
    Returns:
        dict: 包含预期跌幅和置信区间的字典
    """
    # 时间平方根法则 + 概率放大效应
    expected_decline_t1 = calculate_expected_decline_t1(prob_t1, volatility_20d)['expected_decline']
    expected_decline = expected_decline_t1 * np.sqrt(5) * (1 + 0.3 * prob_t5)  # 概率放大系数0.3
    
    # 置信区间也相应扩大
    base_ci = calculate_expected_decline_t1(prob_t1, volatility_20d)['confidence_interval']
    lower_bound = base_ci[0] * np.sqrt(5) * (1 + 0.2 * prob_t5)
    upper_bound = base_ci[1] * np.sqrt(5) * (1 + 0.4 * prob_t5)  # 上界使用稍高的放大系数
    
    return {
        'expected_decline': expected_decline,
        'confidence_interval': (lower_bound, upper_bound),
        'lower_bound': lower_bound,
        'upper_bound': upper_bound
    }


def calculate_expected_decline_detailed(results):
    """
    基于详细预测结果计算预期跌幅
    
    Args:
        results: 详细预测结果字典，包含 prob_t1, prob_t5, volatility_20d 等
    
    Returns:
        dict: 包含T+1和T+5预期跌幅的字典
    """
    t1_decline = calculate_expected_decline_t1(
        results['prob_t1'], 
        results['volatility_20d']
    )
    
    t5_decline = calculate_expected_decline_t5(
        results['prob_t5'],
        results['prob_t1'],
        results['volatility_20d']
    )
    
    return {
        't1': t1_decline,
        't5': t5_decline
    }