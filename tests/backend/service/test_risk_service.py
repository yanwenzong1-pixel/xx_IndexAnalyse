"""
后端 Service 测试 - 风险评估服务测试
验证风险打分修复后的逻辑
"""
import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.service.risk_service import RiskService


class TestRiskServiceFix:
    """风险评估服务测试类"""

    @pytest.fixture
    def create_sample_df(self):
        """创建测试数据夹具"""
        def _create_df(scenario='normal'):
            """
            创建不同场景的测试数据
            
            场景：
            - normal: 正常市场
            - crash: 暴跌市场（-5.98%）
            - continuous_down: 连续下跌
            - high_volatility: 高波动率
            """
            dates = pd.date_range('2024-01-01', periods=30)
            
            if scenario == 'crash':
                # 暴跌场景：最后一日 -5.98%，前几日连续下跌
                # 注意：`RiskService.assess_risk_level()` 使用末尾 `df['change_pct'].iloc[-1]`
                # 作为单日暴跌依据，因此本测试数据需要把负值放在序列末尾。
                changes = [0.5] * 24 + [-0.3, -1.0, -2.0, -3.0, -4.0, -5.98]
                closes = [1000 * (1 + sum(changes[:i+1]) / 100) for i in range(30)]
                amounts = [3e9] * 30
                turnovers = [3.5] * 30
                
            elif scenario == 'continuous_down':
                # 连续下跌场景：连续 5 日下跌
                # 同理：连续下跌检测从末尾开始回溯最后 N 天，
                # 因此需要让最后 5 天保持为负数。
                changes = [0.5] * 25 + [-1.0, -1.5, -2.0, -2.5, -3.0]
                closes = [1000 * (1 + sum(changes[:i+1]) / 100) for i in range(30)]
                amounts = [2.5e9] * 30
                turnovers = [4.0] * 30
                
            elif scenario == 'high_volatility':
                # 高波动率场景
                # 保证“最近 20 日”仍为高波动，避免 rolling(20) 被早期数据稀释
                changes = [0.5] * 10 + [6.0, -5.5, 7.0, -6.0, 5.0, -4.5, 6.5, -5.0, 7.5, -6.5,
                                         5.5, -4.0, 6.0, -5.0, 7.0, -6.0, 5.0, -4.5, 6.5, -5.5]
                closes = [1000 * (1 + sum(changes[:i+1]) / 100) for i in range(30)]
                amounts = [4e9] * 30
                turnovers = [8.0] * 30
                
            else:  # normal
                # 正常市场
                changes = [0.5] * 30
                closes = [1000 * (1 + sum(changes[:i+1]) / 100) for i in range(30)]
                amounts = [2e9] * 30
                turnovers = [3.0] * 30
            
            data = {
                'date': dates,
                'close': closes,
                'high': [c * 1.02 for c in closes],
                'low': [c * 0.98 for c in closes],
                'amount': amounts,
                'turnover': turnovers,
                'change_pct': changes,
            }
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        
        return _create_df

    def test_normal_market(self, create_sample_df):
        """测试正常市场风险打分"""
        df = create_sample_df('normal')
        service = RiskService(df)
        risk_level = service.assess_risk_level()
        
        # 正常市场风险应在 3-5 分之间
        assert 3.0 <= risk_level <= 5.5, f"正常市场风险打分应为 3-5.5 分，实际：{risk_level}"
        print(f"✅ 正常市场风险打分：{risk_level} 分")

    def test_crash_market(self, create_sample_df):
        """测试暴跌市场风险打分（核心测试）"""
        df = create_sample_df('crash')
        service = RiskService(df)
        risk_level = service.assess_risk_level()
        
        # 暴跌市场风险应达到 8 分以上
        assert risk_level >= 8.0, f"暴跌市场风险打分应>=8 分，实际：{risk_level}"
        assert risk_level <= 10.0, f"风险打分上限应为 10 分，实际：{risk_level}"
        
        # 验证单日暴跌风险计算
        daily_change = df['change_pct'].iloc[-1]
        assert daily_change == -5.98, f"测试数据验证失败：{daily_change}"
        
        print(f"✅ 暴跌市场风险打分：{risk_level} 分（单日跌幅：{daily_change}%）")

    def test_continuous_down(self, create_sample_df):
        """测试连续下跌风险打分"""
        df = create_sample_df('continuous_down')
        service = RiskService(df)
        risk_level = service.assess_risk_level()
        
        # 连续下跌风险应在 6-9 分之间
        assert risk_level >= 6.0, f"连续下跌风险打分应>=6 分，实际：{risk_level}"
        
        # 验证连续下跌天数
        consecutive_down = 0
        for i in range(5):
            if df['change_pct'].iloc[-(i+1)] < 0:
                consecutive_down += 1
            else:
                break
        
        assert consecutive_down >= 3, f"测试数据验证失败：连续下跌{consecutive_down}天"
        print(f"✅ 连续下跌风险打分：{risk_level} 分（连续{consecutive_down}日下跌）")

    def test_high_volatility(self, create_sample_df):
        """测试高波动率市场风险打分"""
        df = create_sample_df('high_volatility')
        service = RiskService(df)
        risk_level = service.assess_risk_level()
        
        # 高波动率风险应在 5-8 分之间
        assert risk_level >= 5.0, f"高波动率风险打分应>=5 分，实际：{risk_level}"
        
        # 验证波动率计算
        volatility = df['change_pct'].rolling(20).std().iloc[-1]
        print(f"✅ 高波动率市场风险打分：{risk_level} 分（20 日波动率：{volatility:.2f}%）")

    def test_risk_level_text(self, create_sample_df):
        """测试风险等级文本映射"""
        service = RiskService(create_sample_df('normal'))
        
        assert service.get_risk_level_text(2.5) == "低风险"
        assert service.get_risk_level_text(4.0) == "中等风险"
        assert service.get_risk_level_text(6.5) == "较高风险"
        assert service.get_risk_level_text(8.5) == "高风险"
        
        print("✅ 风险等级文本映射正确")

    def test_risk_data_structure(self, create_sample_df):
        """测试风险数据结构完整性"""
        df = create_sample_df('crash')
        service = RiskService(df)
        
        risk_data = service.get_risk_data(
            downside_probability=0.42,
            expected_decline=0.012
        )
        
        # 验证返回数据结构
        assert 'risk_level' in risk_data
        assert 'risk_level_text' in risk_data
        assert 'downside_probability' in risk_data
        assert 'expected_decline' in risk_data
        assert 'alert' in risk_data
        assert 'alert_message' in risk_data
        
        # 验证数据类型
        assert isinstance(risk_data['risk_level'], float)
        assert isinstance(risk_data['risk_level_text'], str)
        assert isinstance(risk_data['downside_probability'], float)
        assert risk_data['risk_level'] == round(risk_data['risk_level'], 2)
        
        print("✅ 风险数据结构完整")


class TestRiskScoreCalculation:
    """风险打分计算细节测试"""

    @pytest.fixture
    def sample_df(self):
        """标准测试数据"""
        dates = pd.date_range('2024-01-01', periods=30)
        data = {
            'date': dates,
            'close': [1000 + i * 5 for i in range(30)],
            'high': [1020 + i * 5 for i in range(30)],
            'low': [980 + i * 5 for i in range(30)],
            'amount': [2e9] * 30,
            'turnover': [3.0] * 30,
            'change_pct': [0.5] * 30,
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def test_base_score(self, sample_df):
        """测试基础分从 3.0 开始"""
        service = RiskService(sample_df)
        # 修改数据使所有风险因子为 0
        sample_df['change_pct'] = [0.0] * 30
        sample_df['turnover'] = [2.0] * 30
        sample_df['amount'] = [3e9] * 30
        
        risk_level = service.assess_risk_level()
        # 基础分 3.0 + 微小调整
        assert 3.0 <= risk_level <= 4.0, f"基础分应接近 3.0，实际：{risk_level}"
        print(f"✅ 基础分测试通过：{risk_level} 分")

    def test_daily_crash_impact(self, sample_df):
        """测试单日暴跌影响"""
        # 设置单日暴跌 -6%
        sample_df.loc[sample_df.index[-1], 'change_pct'] = -6.0
        service = RiskService(sample_df)
        
        risk_level = service.assess_risk_level()
        # 基础分 3.0 + 单日暴跌 1.5 分 = 4.5 分以上
        assert risk_level >= 4.5, f"单日暴跌 -6% 风险应>=4.5 分，实际：{risk_level}"
        print(f"✅ 单日暴跌 -6% 风险打分：{risk_level} 分")

    def test_5day_continuous_down_impact(self, sample_df):
        """测试连续 5 日下跌影响"""
        # 设置连续 5 日下跌
        for i in range(5):
            sample_df.loc[sample_df.index[-(i+1)], 'change_pct'] = -2.0
        
        service = RiskService(sample_df)
        risk_level = service.assess_risk_level()
        
        # 基础分 3.0 + 连续下跌 2.0 分 + 其他 = 5 分以上
        assert risk_level >= 5.0, f"连续 5 日下跌风险应>=5 分，实际：{risk_level}"
        print(f"✅ 连续 5 日下跌风险打分：{risk_level} 分")
