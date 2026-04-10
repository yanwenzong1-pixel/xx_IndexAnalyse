"""
业务逻辑层 - 风险评估服务
封装风险评估业务逻辑
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple


class RiskService:
    """风险评估服务"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def assess_risk_level(self) -> float:
        """
        评估风险等级（1-10 级）
        
        Returns:
            风险等级（1-10）
        """
        if self.df is None or len(self.df) == 0:
            return 0
        
        df = self.df.copy()
        
        # 计算必要的指标
        if 'ma20' not in df.columns:
            df['ma20'] = df['close'].rolling(20).mean()
        if 'ma5' not in df.columns:
            df['ma5'] = df['close'].rolling(5).mean()
        if 'volatility' not in df.columns:
            df['volatility'] = df['change_pct'].rolling(20).std() * np.sqrt(252)
        if 'ma20_20d' not in df.columns:
            df['ma20_20d'] = df['amount'].rolling(20).mean()
        
        # 基础风险分数（降低至 3.0，让风险分数更敏感）
        risk_score = 3.0
        
        # ========== 1. 流动性风险（权重 20%）==========
        avg_turnover_5d = df['turnover'].tail(5).mean()
        amount_ratio = df['amount'].iloc[-1] / 5e9
        
        # 换手率风险（降低阈值）
        if avg_turnover_5d > 12:
            risk_score += 2.0
        elif avg_turnover_5d > 8:
            risk_score += 1.0 + (avg_turnover_5d - 8) / 4.0
        elif avg_turnover_5d > 5:
            risk_score += (avg_turnover_5d - 5) / 3.0
        
        # 流动性枯竭风险
        if amount_ratio < 0.0005:
            risk_score += 3.0
        elif amount_ratio < 0.001:
            risk_score += 2.0 + (0.001 - amount_ratio) / 0.0005
        elif amount_ratio < 0.002:
            risk_score += 1.0 + (0.002 - amount_ratio) / 0.001
        
        # ========== 2. 单日暴跌风险（新增，权重 20%）==========
        daily_change = df['change_pct'].iloc[-1]
        
        if daily_change < -7:
            risk_score += 2.0
        elif daily_change < -5:
            risk_score += 1.5
        elif daily_change < -3:
            risk_score += 1.0
        elif daily_change < -2:
            risk_score += 0.5
        
        # ========== 3. 价格趋势风险（双向计算，权重 25%）==========
        if len(df) > 20:
            recent_change = df['change_pct'].tail(5).sum()
            
            # 上涨风险
            if recent_change > 15:
                risk_score += min(2.0, 1.0 + (recent_change - 15) / 10.0)
            elif recent_change > 8:
                risk_score += (recent_change - 8) / 7.0
            
            # 下跌风险（新增）
            if recent_change < -15:
                risk_score += min(2.0, abs(recent_change) / 10.0)
            elif recent_change < -8:
                risk_score += abs(recent_change) / 10.0
            elif recent_change < -5:
                risk_score += abs(recent_change) / 15.0
            
            # 均线跌破风险（降低阈值）
            close_price = df['close'].iloc[-1]
            ma20_price = df['ma20'].iloc[-1]
            if close_price < ma20_price:
                drop_ratio = (ma20_price - close_price) / ma20_price
                if drop_ratio > 0.05:
                    risk_score += 2.0
                elif drop_ratio > 0.02:
                    risk_score += 1.0 + (drop_ratio - 0.02) / 0.03
                else:
                    risk_score += drop_ratio / 0.02
        
        # ========== 4. 连续下跌风险（新增，权重 10%）==========
        consecutive_down = 0
        for i in range(min(5, len(df))):
            if df['change_pct'].iloc[-(i+1)] < 0:
                consecutive_down += 1
            else:
                break
        
        if consecutive_down >= 5:
            risk_score += 2.0
        elif consecutive_down >= 3:
            risk_score += 1.0
        elif consecutive_down >= 2:
            risk_score += 0.5
        
        # ========== 5. 波动率风险（权重 15%，降低阈值）==========
        volatility = df['change_pct'].rolling(20).std().iloc[-1]
        if volatility > 8:
            risk_score += 2.0
        elif volatility > 5:
            risk_score += 1.0 + (volatility - 5) / 3.0
        elif volatility > 3:
            risk_score += (volatility - 3) / 2.0
        
        # ========== 6. 成交量异常风险（新增，权重 10%）==========
        avg_amount_20d = df['ma20_20d'].iloc[-1]
        current_amount = df['amount'].iloc[-1]
        
        if avg_amount_20d > 0:
            amount_ratio_20d = current_amount / avg_amount_20d
            
            # 成交量异常放大（>150%）
            if amount_ratio_20d > 1.5:
                risk_score += 1.0
            # 成交量异常萎缩（<50%）
            elif amount_ratio_20d < 0.5:
                risk_score += 1.5
        
        # 限制在 1-10 之间
        return round(max(1.0, min(10.0, risk_score)), 2)
    
    def get_risk_level_text(self, risk_level: float) -> str:
        """获取风险等级文本"""
        if risk_level <= 3:
            return "低风险"
        elif risk_level <= 5:
            return "中等风险"
        elif risk_level <= 7:
            return "较高风险"
        else:
            return "高风险"
    
    def check_alert(self, downside_probability: float) -> Tuple[bool, str]:
        """
        检查预警条件
        
        Args:
            downside_probability: 下跌概率
            
        Returns:
            (是否预警, 预警消息)
        """
        if downside_probability > 0.7:
            return True, f"微盘股指数下跌风险警报！下跌概率：{downside_probability*100:.2f}%"
        
        if len(self.df) > 20:
            ma5 = self.df['close'].rolling(5).mean().iloc[-1]
            ma20 = self.df['close'].rolling(20).mean().iloc[-1]
            if ma5 > ma20 and self.df['change_pct'].iloc[-1] > 0:
                return True, "微盘股指数出现买点信号！"
        
        return False, ""
    
    def get_risk_data(self, downside_probability: float, expected_decline: float) -> Dict[str, Any]:
        """获取完整风险数据"""
        risk_level = self.assess_risk_level()
        alert, alert_message = self.check_alert(downside_probability)
        
        return {
            'risk_level': risk_level,
            'risk_level_text': self.get_risk_level_text(risk_level),
            'downside_probability': downside_probability,
            'expected_decline': expected_decline,
            'alert': alert,
            'alert_message': alert_message
        }
