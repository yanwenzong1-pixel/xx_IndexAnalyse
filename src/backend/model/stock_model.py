"""
数据模型层 - 股票数据模型
定义标准化数据结构
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class StockData:
    """股票数据模型"""
    date: datetime
    open: float
    close: float
    high: float
    low: float
    volume: float
    amount: float
    amplitude: float
    change_pct: float
    change: float
    turnover: float
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StockData':
        """从字典创建实例"""
        return cls(
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            open=float(data['open']),
            close=float(data['close']),
            high=float(data['high']),
            low=float(data['low']),
            volume=float(data['volume']),
            amount=float(data['amount']),
            amplitude=float(data['amplitude']),
            change_pct=float(data['change_pct']),
            change=float(data['change']),
            turnover=float(data['turnover'])
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'amount': self.amount,
            'amplitude': self.amplitude,
            'change_pct': self.change_pct,
            'change': self.change,
            'turnover': self.turnover
        }


@dataclass
class IndicatorData:
    """指标数据模型"""
    name: str
    value: float
    unit: str
    description: str
    impact_coefficient: float = 0.0
    risk_level: str = 'low'
    risk_reason: str = ''
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'description': self.description,
            'impact_coefficient': self.impact_coefficient,
            'risk_level': self.risk_level,
            'risk_reason': self.risk_reason
        }


@dataclass
class RiskData:
    """风险数据模型"""
    risk_level: int
    risk_level_text: str
    downside_probability: float
    expected_decline: float
    alert: bool
    alert_message: str
    dimensions: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'risk_level': self.risk_level,
            'risk_level_text': self.risk_level_text,
            'downside_probability': self.downside_probability,
            'expected_decline': self.expected_decline,
            'alert': self.alert,
            'alert_message': self.alert_message,
            'dimensions': self.dimensions
        }
