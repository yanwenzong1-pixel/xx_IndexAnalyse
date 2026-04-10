"""
历史风险计算服务 - 独立模块
计算历史每个交易日的风险打分（1-10 分）

核心原则：
1. 避免前视偏差 - 每个时点只用该时点及之前的数据
2. 复用现有逻辑 - 使用 analyzer.assess_risk_level()
3. 独立可测试 - 不依赖外部状态
"""

from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np


class HistoryRiskService:
    """历史风险服务 - 独立类，不依赖现有代码"""
    RISK_OUTPUT_SOURCE = "backend-live"
    RISK_OUTPUT_VERSION = "risk-v2-2dp"
    
    def __init__(self, analyzer):
        """
        初始化
        
        Args:
            analyzer: MicroCapAnalyzer 实例（用于获取基础数据）
        """
        self.analyzer = analyzer
    
    def calculate_single_day_risk(self, df_up_to_date) -> Dict:
        """
        计算单个交易日的风险打分
        
        核心逻辑：复用 analyzer.assess_risk_level()
        优势：不重复造轮子，保证逻辑一致
        
        Args:
            df_up_to_date: 截止到当前日期的 DataFrame（不包含未来数据）
            
        Returns:
            dict: 包含日期、风险分数、风险等级的字典
        """
        # 临时保存原始 DataFrame
        original_df = self.analyzer.df
        
        try:
            # 临时替换为历史数据
            self.analyzer.df = df_up_to_date
            
            # 复用现有风险评估逻辑
            risk_score = self.analyzer.assess_risk_level()
            
            # 获取日期
            current_date = df_up_to_date.iloc[-1]['date']
            if hasattr(current_date, 'strftime'):
                date_str = current_date.strftime('%Y-%m-%d')
            else:
                date_str = str(current_date)
            
            return {
                'date': date_str,
                'risk_score': self._round_risk_score(risk_score),
                'risk_level': self._get_risk_level_text(risk_score),
                'source': self.RISK_OUTPUT_SOURCE
            }
        finally:
            # 恢复原始 DataFrame（确保不影响后续计算）
            self.analyzer.df = original_df
    
    def calculate_history(self, days: int = 252) -> Dict:
        """
        计算历史 N 天的风险打分
        
        实现要点：
        1. 从当前日期向前回溯 days 天
        2. 对每个历史时点，只用该时点及之前的数据（避免前视偏差）
        3. 跳过数据量不足的日期（至少需要 20 个交易日才能计算完整指标）
        4. 返回按日期排序的结果数组
        
        Args:
            days: 回溯天数，默认 252 个交易日（约 1 年）
            
        Returns:
            dict: 包含成功标志、数据数组、元数据的字典
        """
        # 数据验证
        if self.analyzer.df is None:
            return {
                'success': False,
                'error': 'data_not_initialized',
                'message': '基础数据未初始化'
            }
        
        if len(self.analyzer.df) < days:
            return {
                'success': False,
                'error': 'insufficient_data',
                'message': f'历史数据不足，需要{days}天，实际{len(self.analyzer.df)}天'
            }
        
        print(f"[HistoryRisk] 开始计算历史风险，天数：{days}")
        
        results = []
        end_idx = len(self.analyzer.df) - 1
        
        # 最小数据量要求（确保 rolling 计算有效）
        min_required_days = 20
        
        # 保存原始 DataFrame
        original_df = self.analyzer.df
        
        # 从后向前遍历，确保每个时点只用历史数据
        for i in range(days):
            current_idx = end_idx - i
            
            # 跳过数据量不足的日期
            if current_idx + 1 < min_required_days:
                continue
            
            try:
                # 创建独立的副本（避免影响原始数据）
                df_up_to_current = original_df.iloc[:current_idx + 1].copy()
                
                # 临时替换 DataFrame
                self.analyzer.df = df_up_to_current
                
                # 计算单日风险
                risk_score = self.analyzer.assess_risk_level()
                
                # 获取日期
                current_date = df_up_to_current.iloc[-1]['date']
                date_str = current_date.strftime('%Y-%m-%d') if hasattr(current_date, 'strftime') else str(current_date)
                
                results.append({
                    'date': date_str,
                    'risk_score': self._round_risk_score(risk_score),  # 风险分统一两位小数
                    'risk_level': self._get_risk_level_text(risk_score),
                    'source': self.RISK_OUTPUT_SOURCE
                })
                
                # 每计算 50 天输出一次进度
                if (i + 1) % 50 == 0:
                    print(f"[HistoryRisk] 进度：{i + 1}/{days}，已计算 {len(results)} 条")
                    
            except Exception as e:
                # 如果计算失败，跳过该日期（可能是数据质量问题）
                current_date = original_df.iloc[current_idx]['date']
                date_str = current_date.strftime('%Y-%m-%d') if hasattr(current_date, 'strftime') else str(current_date)
                print(f"⚠️ 跳过日期 {date_str}：{e}")
                continue
        
        # 恢复原始 DataFrame
        self.analyzer.df = original_df
        
        # 反转结果（最近日期在前）
        results.reverse()
        
        print(f"[HistoryRisk] 计算完成，共 {len(results)} 条记录")
        
        # 如果没有成功计算任何数据，返回错误
        if not results:
            return {
                'success': False,
                'error': 'calculation_failed',
                'message': '未能计算任何历史风险数据'
            }
        
        # 计算统计信息
        risk_scores = [r['risk_score'] for r in results]
        
        return {
            'success': True,
            'data': results,
            'metadata': {
                'total_days': len(results),
                'avg_risk': self._round_risk_score(np.mean(risk_scores)),
                'max_risk': self._round_risk_score(np.max(risk_scores)),
                'min_risk': self._round_risk_score(np.min(risk_scores)),
                'current_risk': self._round_risk_score(risk_scores[-1]) if risk_scores else 0.0,
                'risk_trend': self._calculate_trend(risk_scores),
                'source': self.RISK_OUTPUT_SOURCE,
                'version': self.RISK_OUTPUT_VERSION
            }
        }

    def _round_risk_score(self, value: float) -> float:
        """统一风险分精度：保留两位小数并返回 float。"""
        return round(float(value), 2)
    
    def _get_risk_level_text(self, score: float) -> str:
        """
        风险等级文本映射
        
        Args:
            score: 风险分数（1-10）
            
        Returns:
            str: 风险等级文本
        """
        if score <= 3:
            return 'low'
        elif score <= 5:
            return 'medium'
        elif score <= 7:
            return 'high'
        else:
            return 'very_high'
    
    def _calculate_trend(self, risk_scores: List[float]) -> str:
        """
        计算风险趋势
        
        Args:
            risk_scores: 风险分数数组（按时间正序）
            
        Returns:
            str: rising（上升）/ stable（稳定）/ falling（下降）
        """
        if len(risk_scores) < 5:
            return 'stable'
        
        # 比较最近 5 天和之前 5 天的平均风险
        recent_avg = np.mean(risk_scores[-5:])
        earlier_avg = np.mean(risk_scores[-10:-5])
        
        diff = recent_avg - earlier_avg
        
        if diff > 0.5:
            return 'rising'
        elif diff < -0.5:
            return 'falling'
        else:
            return 'stable'


# 工厂函数（便于后续集成）
def get_history_risk_service(analyzer):
    """
    获取历史风险服务实例
    
    Args:
        analyzer: MicroCapAnalyzer 实例
        
    Returns:
        HistoryRiskService 实例
    """
    return HistoryRiskService(analyzer)
