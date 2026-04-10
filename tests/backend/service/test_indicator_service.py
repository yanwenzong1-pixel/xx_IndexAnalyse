"""
后端 Service 测试 - 指标计算测试
"""
import pytest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.service.indicator_service import IndicatorService


class TestIndicatorService:
    """指标服务测试类"""

    @pytest.fixture
    def sample_df(self):
        """测试数据夹具"""
        data = {
            'date': pd.date_range('2024-01-01', periods=30),
            'close': [100 + i * 0.5 for i in range(30)],
            'high': [102 + i * 0.5 for i in range(30)],
            'low': [98 + i * 0.5 for i in range(30)],
            'amount': [1e9] * 30,
            'turnover': [5.0] * 30,
            'change_pct': [0.5] * 30,
        }
        return pd.DataFrame(data)

    def test_liquidity_indicators(self, sample_df):
        """测试流动性指标计算"""
        service = IndicatorService(sample_df)
        indicators = service.calculate_liquidity_indicators()
        
        assert indicators is not None
        assert 'amount_to_market_cap' in indicators
        assert 'avg_turnover_5d' in indicators
        assert isinstance(indicators['amount_to_market_cap'], float)

    def test_fund_structure_indicators(self, sample_df):
        """测试资金结构指标计算"""
        service = IndicatorService(sample_df)
        indicators = service.calculate_fund_structure_indicators()
        
        assert indicators is not None
        assert 'amount_change_pct' in indicators

    def test_valuation_indicators(self, sample_df):
        """测试估值指标计算"""
        service = IndicatorService(sample_df)
        indicators = service.calculate_valuation_indicators()
        
        assert indicators is not None
        assert 'volatility' in indicators
        assert 'ma5' in indicators
        assert 'ma20' in indicators

    def test_get_all_indicators(self, sample_df):
        """测试获取所有指标"""
        service = IndicatorService(sample_df)
        all_indicators = service.get_all_indicators()
        
        assert 'liquidity' in all_indicators
        assert 'fund_structure' in all_indicators
        assert 'valuation' in all_indicators
        assert 'policy' in all_indicators
        assert 'macro' in all_indicators
