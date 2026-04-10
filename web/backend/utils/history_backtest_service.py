"""
历史数据回溯服务模块
实现历史 N 日的下跌概率回溯计算
"""

import time
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import numpy as np


class HistoryBacktestService:
    """历史回溯服务"""
    
    def __init__(self, analyzer):
        """
        初始化回溯服务
        
        Args:
            analyzer: MicroCapAnalyzer 实例
        """
        self.analyzer = analyzer
        self.factor_service = None
        self.risk_calculator = None
        
        # 因子计算需要的历史窗口（252 个交易日）
        self.factor_window = 252
    
    def _ensure_services_initialized(self):
        """确保服务已初始化"""
        if self.factor_service is None:
            from utils.factor_data_service import get_factor_service
            from utils.risk_calculation_service import get_risk_calculator
            self.factor_service = get_factor_service()
            self.risk_calculator = get_risk_calculator()
    
    def fetch_extended_market_data(self, days: int) -> Optional[pd.DataFrame]:
        """
        获取扩展的历史市场数据（包含因子计算所需的额外历史数据）
        
        Args:
            days: 需要回溯的天数
            
        Returns:
            DataFrame with market data (days + factor_window)
        """
        # 需要获取的天数 = 回溯天数 + 因子计算窗口
        total_days_needed = days + self.factor_window
        
        # 修改 analyzer 的 fetch_data 方法以获取更多数据
        # 注意：当前 fetch_data 已经获取了全部历史数据，所以直接使用即可
        if self.analyzer.df is None:
            if not self.analyzer.fetch_data():
                return None
        
        # 检查数据是否足够
        if len(self.analyzer.df) < total_days_needed:
            # 数据不足，使用全部可用数据
            return self.analyzer.df.copy()
        
        # 返回足够的历史数据
        return self.analyzer.df.tail(total_days_needed).copy()
    
    def calculate_single_day_prediction(self, df_up_to_date: pd.DataFrame) -> Optional[Dict]:
        """
        计算单日的下跌概率预测
        
        Args:
            df_up_to_date: 截止到当日的历史数据 DataFrame
            
        Returns:
            预测结果字典，包含 prob_t1, prob_t5 等
        """
        try:
            self._ensure_services_initialized()
            
            # 1. 计算 25 因子数据
            factors = self.factor_service.get_all_factors(df_up_to_date)
            
            if not factors:
                return None
            
            # 2. 计算下跌概率
            result = self.risk_calculator.predict_downside_probability(
                factors, 
                df_up_to_date
            )
            
            # 3. 添加日期信息
            result['date'] = df_up_to_date['date'].iloc[-1].strftime('%Y-%m-%d')
            
            return result
            
        except Exception as e:
            print(f"单日计算失败：{e}")
            return None
    
    def calculate_history(self, days: int = 300, include_evaluation: bool = False) -> Dict:
        """
        计算历史 N 日的下跌概率
        
        Args:
            days: 回溯天数，默认 300
            include_evaluation: 是否在元数据中加入回测对齐评估（预测概率 vs 未来真实跌幅/累计涨跌幅）
            
        Returns:
            {
                'success': bool,
                'data': List[Dict],  # 每日预测结果
                'metadata': Dict,    # 元数据
                'error': Optional[str]
            }
        """
        start_time = time.time()
        
        try:
            # 1. 获取扩展历史数据
            extended_df = self.fetch_extended_market_data(days)
            
            if extended_df is None or len(extended_df) == 0:
                return {
                    'success': False,
                    'data': [],
                    'metadata': {},
                    'error': '市场数据获取失败'
                }
            
            # 2. 确定实际可回溯的天数
            actual_days = min(days, len(extended_df) - self.factor_window)
            
            if actual_days <= 0:
                return {
                    'success': False,
                    'data': [],
                    'metadata': {},
                    'error': f'历史数据不足，需要至少 {self.factor_window} 日，当前只有 {len(extended_df)} 日'
                }
            
            # 3. 循环计算每日预测
            results = []

            # 可选：用于概率校准/对齐的评估数据（不影响预测本身）
            eval_t1_probs = []
            eval_t1_labels = []  # 1=未来 T+1 下跌，0=未来不下跌
            eval_t5_probs = []
            eval_t5_labels = []  # 1=未来 5 日内累计下跌，0=未来不下跌
            
            # 从后往前循环（最近的日期在前）
            # 起始索引：确保有 factor_window 天的历史数据用于因子计算
            start_idx = self.factor_window - 1
            end_idx = len(extended_df) - 1
            
            for i in range(actual_days):
                # 当前日期索引（从后往前）
                current_idx = end_idx - i
                
                # 确保有足够历史数据
                if current_idx < start_idx:
                    break
                
                # 截取到当前日期的历史数据（避免未来函数）
                df_up_to_current = extended_df.iloc[:current_idx + 1].copy()
                
                # 计算单日预测
                daily_result = self.calculate_single_day_prediction(df_up_to_current)
                
                if daily_result:
                    results.append(daily_result)

                    if include_evaluation:
                        # 真实对齐：只使用 extended_df 中“未来窗口”做评估，
                        # 特征仍然只来自 df_up_to_current（避免前视偏差污染）。
                        if current_idx + 1 <= end_idx:
                            t1_change_pct = float(extended_df['change_pct'].iloc[current_idx + 1])
                            eval_t1_probs.append(float(daily_result.get('prob_t1', 0.0)))
                            eval_t1_labels.append(1.0 if t1_change_pct < 0 else 0.0)

                        if current_idx + 5 <= end_idx:
                            # 未来 5 天累计涨跌幅 < 0 视作“5日内下跌”
                            t5_cum_change_pct = float(
                                extended_df['change_pct'].iloc[current_idx + 1: current_idx + 6].sum()
                            )
                            eval_t5_probs.append(float(daily_result.get('prob_t5', 0.0)))
                            eval_t5_labels.append(1.0 if t5_cum_change_pct < 0 else 0.0)
            
            # 4. 反转结果（最近的日期在前）
            results.reverse()
            
            # 5. 计算元数据
            calculation_time = time.time() - start_time

            # 确保风险计算器已初始化，从而能拿到当前 prob_model_params.json 版本与温度信息
            self._ensure_services_initialized()
            
            metadata = {
                'total_days': len(results),
                'requested_days': days,
                'calculation_time_ms': round(calculation_time * 1000, 2),
                'cache_hit': False,
                'cache_key': f'predict_history_{days}_{datetime.now().strftime("%Y%m%d")}',
                'data_start_date': results[0]['date'] if results else None,
                'data_end_date': results[-1]['date'] if results else None
            }

            prob_params = getattr(self.risk_calculator, "prob_model_params", {}) or {}
            metadata.update(
                {
                    "prob_model_params_version": prob_params.get("version"),
                    "temperature_t1": prob_params.get("temperature_t1"),
                    "temperature_t5": prob_params.get("temperature_t5"),
                }
            )

            if include_evaluation:
                # 只有在样本足够时才计算指标
                evaluation = {}
                eps = 1e-12

                def classify_calibration_status(bias: float, ece: float) -> str:
                    # 偏差定义：pred_mean - event_rate
                    if abs(bias) <= 0.05 and ece <= 0.08:
                        return "normal"
                    if bias < -0.05:
                        return "underestimate"
                    if bias > 0.05:
                        return "overestimate"
                    return "normal"

                def classify_alert_level(bias: float, ece: float) -> str:
                    if ece > 0.15 or abs(bias) > 0.12:
                        return "red"
                    if ece > 0.10:
                        return "yellow"
                    return "none"

                def compute_metrics(p_list, y_list):
                    p = np.array(p_list, dtype=float)
                    y = np.array(y_list, dtype=float)
                    res = {}

                    # Brier score
                    res['brier'] = float(np.mean((p - y) ** 2))
                    res['event_rate'] = float(np.mean(y))
                    res['pred_mean'] = float(np.mean(p))
                    res['bias'] = float(res['pred_mean'] - res['event_rate'])
                    res['prob_range'] = [float(np.min(p)), float(np.max(p))]
                    res['hit_rate@0.5'] = float(np.mean((p >= 0.5) == (y >= 0.5)))

                    # Logloss（交叉熵）
                    res['logloss'] = float(-np.mean(y * np.log(p + eps) + (1.0 - y) * np.log(1.0 - p + eps)))

                    # 可靠性分箱（reliability / ECE）
                    n_bins = 10
                    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
                    bins = []
                    ece = 0.0
                    total = max(1, len(p))
                    for i in range(n_bins):
                        left = bin_edges[i]
                        right = bin_edges[i + 1]
                        if i == n_bins - 1:
                            mask = (p >= left) & (p <= right)
                        else:
                            mask = (p >= left) & (p < right)

                        cnt = int(np.sum(mask))
                        if cnt <= 0:
                            continue

                        p_mean = float(np.mean(p[mask]))
                        y_mean = float(np.mean(y[mask]))
                        bins.append({
                            'bin_start': float(left),
                            'bin_end': float(right),
                            'pred_mean': p_mean,
                            'obs_rate': y_mean,
                            'count': cnt
                        })
                        ece += (cnt / total) * abs(y_mean - p_mean)

                    res['reliability_bins'] = bins
                    res['ece'] = float(ece)
                    res['calibration_status'] = classify_calibration_status(
                        res['bias'], res['ece']
                    )
                    res['calibration_alert_level'] = classify_alert_level(
                        res['bias'], res['ece']
                    )

                    return res

                if eval_t1_probs and eval_t1_labels and len(eval_t1_probs) == len(eval_t1_labels):
                    m = compute_metrics(eval_t1_probs, eval_t1_labels)
                    evaluation['t1_brier'] = m['brier']
                    evaluation['t1_event_rate'] = m['event_rate']
                    evaluation['t1_prob_range'] = m['prob_range']
                    evaluation['t1_hit_rate@0.5'] = m['hit_rate@0.5']
                    evaluation['t1_logloss'] = m['logloss']
                    evaluation['t1_reliability_bins'] = m['reliability_bins']
                    evaluation['t1_ece'] = m['ece']
                    evaluation['t1_pred_mean'] = m['pred_mean']
                    evaluation['t1_bias'] = m['bias']
                    evaluation['calibration_status_t1'] = m['calibration_status']
                    evaluation['calibration_alert_level_t1'] = m['calibration_alert_level']
                else:
                    evaluation['t1_note'] = 'insufficient_samples'

                if eval_t5_probs and eval_t5_labels and len(eval_t5_probs) == len(eval_t5_labels):
                    m = compute_metrics(eval_t5_probs, eval_t5_labels)
                    evaluation['t5_brier'] = m['brier']
                    evaluation['t5_event_rate'] = m['event_rate']
                    evaluation['t5_prob_range'] = m['prob_range']
                    evaluation['t5_hit_rate@0.5'] = m['hit_rate@0.5']
                    evaluation['t5_logloss'] = m['logloss']
                    evaluation['t5_reliability_bins'] = m['reliability_bins']
                    evaluation['t5_ece'] = m['ece']
                    evaluation['t5_pred_mean'] = m['pred_mean']
                    evaluation['t5_bias'] = m['bias']
                    evaluation['calibration_status_t5'] = m['calibration_status']
                    evaluation['calibration_alert_level_t5'] = m['calibration_alert_level']
                else:
                    evaluation['t5_note'] = 'insufficient_samples'

                metadata['evaluation'] = evaluation
            
            return {
                'success': True,
                'data': results,
                'metadata': metadata,
                'error': None
            }
            
        except Exception as e:
            calculation_time = time.time() - start_time
            return {
                'success': False,
                'data': [],
                'metadata': {
                    'calculation_time_ms': round(calculation_time * 1000, 2),
                    'error_type': type(e).__name__
                },
                'error': f'计算失败：{str(e)}'
            }
    
    def get_history_summary(self, days: int = 300) -> Dict:
        """
        获取历史预测的统计摘要
        
        Args:
            days: 回溯天数
            
        Returns:
            统计摘要字典
        """
        result = self.calculate_history(days)
        
        if not result['success'] or len(result['data']) == 0:
            return {
                'success': False,
                'error': result['error']
            }
        
        # 提取 prob_t1 和 prob_t5
        prob_t1_values = [d['prob_t1'] for d in result['data']]
        prob_t5_values = [d['prob_t5'] for d in result['data']]
        
        # 计算统计指标
        summary = {
            'success': True,
            't1_stats': {
                'min': round(min(prob_t1_values) * 100, 2),
                'max': round(max(prob_t1_values) * 100, 2),
                'mean': round(np.mean(prob_t1_values) * 100, 2),
                'median': round(np.median(prob_t1_values) * 100, 2),
                'std': round(np.std(prob_t1_values) * 100, 2),
                'current': round(prob_t1_values[-1] * 100, 2) if prob_t1_values else None
            },
            't5_stats': {
                'min': round(min(prob_t5_values) * 100, 2),
                'max': round(max(prob_t5_values) * 100, 2),
                'mean': round(np.mean(prob_t5_values) * 100, 2),
                'median': round(np.median(prob_t5_values) * 100, 2),
                'std': round(np.std(prob_t5_values) * 100, 2),
                'current': round(prob_t5_values[-1] * 100, 2) if prob_t5_values else None
            },
            'metadata': result['metadata']
        }
        
        return summary


# 单例模式
_history_service_instance = None

def get_history_service(analyzer=None):
    """
    获取历史回溯服务单例
    
    Args:
        analyzer: MicroCapAnalyzer 实例
        
    Returns:
        HistoryBacktestService 实例
    """
    global _history_service_instance
    if _history_service_instance is None:
        if analyzer is None:
            from .analyzer import MicroCapAnalyzer
            analyzer = MicroCapAnalyzer()
            analyzer.fetch_data()
        _history_service_instance = HistoryBacktestService(analyzer)
    return _history_service_instance
