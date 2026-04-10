"""
数据模型层 - API 响应模型
定义统一的 API 响应格式
"""
from dataclasses import dataclass
from typing import Any, Optional, Dict


@dataclass
class APIResponse:
    """API 响应基础模型"""
    success: bool
    message: str = ''
    data: Any = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            'success': self.success,
            'message': self.message
        }
        if self.data is not None:
            result['data'] = self.data
        return result


@dataclass
class ErrorResponse:
    """错误响应模型"""
    success: bool = False
    message: str = '操作失败'
    error_code: str = 'UNKNOWN_ERROR'
    details: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            'success': self.success,
            'message': self.message,
            'error_code': self.error_code
        }
        if self.details:
            result['details'] = self.details
        return result


@dataclass
class StockDataResponse:
    """股票数据响应"""
    success: bool
    message: str
    latest: Optional[Dict] = None
    history: Optional[list] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'success': self.success,
            'message': self.message,
            'data': {
                'latest': self.latest,
                'history': self.history
            } if self.latest and self.history else None
        }


@dataclass
class IndicatorResponse:
    """指标数据响应"""
    success: bool
    message: str
    liquidity: Optional[Dict] = None
    fund_structure: Optional[Dict] = None
    valuation: Optional[Dict] = None
    policy: Optional[Dict] = None
    macro: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'success': self.success,
            'message': self.message,
            'data': {
                'liquidity': self.liquidity,
                'fund_structure': self.fund_structure,
                'valuation': self.valuation,
                'policy': self.policy,
                'macro': self.macro
            } if any([self.liquidity, self.fund_structure, self.valuation, self.policy, self.macro]) else None
        }


@dataclass
class RiskResponse:
    """风险评估响应"""
    success: bool
    message: str
    risk_level: Optional[int] = None
    risk_level_text: Optional[str] = None
    downside_probability: Optional[float] = None
    expected_decline: Optional[float] = None
    alert: Optional[bool] = None
    alert_message: Optional[str] = None
    dimensions: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'success': self.success,
            'message': self.message,
            'data': {
                'risk_level': self.risk_level,
                'risk_level_text': self.risk_level_text,
                'downside_probability': self.downside_probability,
                'expected_decline': self.expected_decline,
                'alert': self.alert,
                'alert_message': self.alert_message,
                'dimensions': self.dimensions
            } if self.risk_level is not None else None
        }
