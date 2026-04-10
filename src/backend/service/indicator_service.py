"""
业务逻辑层 - 指标计算服务
计算 5 大维度指标
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


class IndicatorService:
    """指标计算服务"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def calculate_liquidity_indicators(self) -> Optional[Dict[str, Any]]:
        """计算流动性维度指标"""
        if self.df is None:
            return None
        
        df = self.df.copy()
        df['amount_to_market_cap'] = df['amount'] / 5e9
        df['avg_turnover_5d'] = df['turnover'].rolling(5).mean()
        df['bid_ask_spread'] = (df['high'] - df['low']) / df['close']
        df['liquidity_coverage'] = df['amount'].rolling(20).mean()
        
        return {
            'amount_to_market_cap': float(df['amount_to_market_cap'].iloc[-1]),
            'avg_turnover_5d': float(df['avg_turnover_5d'].iloc[-1]),
            'bid_ask_spread': float(df['bid_ask_spread'].iloc[-1]),
            'liquidity_coverage': float(df['liquidity_coverage'].iloc[-1])
        }
    
    def calculate_fund_structure_indicators(self) -> Optional[Dict[str, Any]]:
        """计算资金结构维度指标"""
        if self.df is None:
            return None
        
        df = self.df.copy()
        df['amount_change_pct'] = df['amount'].pct_change()
        df['financing_balance_change'] = df['amount'].rolling(5).mean().pct_change()
        
        return {
            'amount_change_pct': float(df['amount_change_pct'].iloc[-1]) if not pd.isna(df['amount_change_pct'].iloc[-1]) else 0,
            'financing_balance_change': float(df['financing_balance_change'].iloc[-1]) if not pd.isna(df['financing_balance_change'].iloc[-1]) else 0
        }
    
    def calculate_valuation_indicators(self) -> Optional[Dict[str, Any]]:
        """计算估值与业绩维度指标"""
        if self.df is None:
            return None
        
        df = self.df.copy()
        df['volatility'] = df['change_pct'].rolling(20).std() * np.sqrt(252)
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        return {
            'volatility': float(df['volatility'].iloc[-1]),
            'ma5': float(df['ma5'].iloc[-1]),
            'ma20': float(df['ma20'].iloc[-1]),
            'ma5_ma20_diff': float(df['ma5'].iloc[-1] - df['ma20'].iloc[-1])
        }
    
    def calculate_policy_indicators(self) -> Dict[str, Any]:
        """计算政策与制度维度指标"""
        return {
            'ipo_activity': 0.5,
            'regulation_intensity': 0.3,
            'financial_report_window': False
        }
    
    def calculate_macro_indicators(self) -> Dict[str, Any]:
        """计算宏观环境维度指标"""
        return {
            'excess_liquidity': 0.2,
            'pmi': 50.5,
            'risk_appetite': 0.6,
            'interest_rate_env': 0.4
        }
    
    def get_all_indicators(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            'liquidity': self.calculate_liquidity_indicators(),
            'fund_structure': self.calculate_fund_structure_indicators(),
            'valuation': self.calculate_valuation_indicators(),
            'policy': self.calculate_policy_indicators(),
            'macro': self.calculate_macro_indicators()
        }
