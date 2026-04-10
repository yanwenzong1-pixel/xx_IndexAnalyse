"""
业务逻辑层 - 报告生成服务
封装报告生成业务逻辑
"""
from typing import Optional, Dict, Any
import pandas as pd


class ReportService:
    """报告生成服务"""
    
    def __init__(self, df: pd.DataFrame, risk_data: Dict[str, Any], 
                 indicators: Dict[str, Any], decline_results: Dict[str, Any]):
        self.df = df
        self.risk_data = risk_data
        self.indicators = indicators
        self.decline_results = decline_results
    
    def generate_daily_report(self) -> str:
        """生成每日报告"""
        if self.df is None or len(self.df) == 0:
            return "数据不可用"
        
        latest = self.df.iloc[-1]
        
        report = f"""
微盘股指数每日监控报告
日期：{latest['date'].strftime('%Y-%m-%d')}

一、当日表现
- 收盘：{latest['close']:.2f}
- 涨跌幅：{latest['change_pct']:.2f}%
- 成交额：{latest['amount']/1e8:.2f}亿元
- 换手率：{latest['turnover']:.2f}%
- 振幅：{latest['amplitude']:.2f}%

二、核心指标
- 5 日平均换手率：{self.df['turnover'].tail(5).mean():.2f}%
- 成交额/总市值：{latest['amount']/5e9*100:.2f}%
- 20 日波动率：{self.df['change_pct'].rolling(20).std().iloc[-1]*100:.2f}%

三、资金结构
- 成交额变化：{self.df['amount'].pct_change().iloc[-1]*100:.2f}%
- 趋势指标：MA5={self.df['close'].rolling(5).mean().iloc[-1]:.2f}, MA20={self.df['close'].rolling(20).mean().iloc[-1]:.2f}

四、风险评级
- 风险等级：{self.risk_data['risk_level']}/{self.risk_data['risk_level_text']}
- 次日下跌概率：{self.risk_data['downside_probability']*100:.2f}%
- 5 日内下跌概率：待计算
- 次日预期跌幅：{self.decline_results['t1']['expected_decline']:.2f}%
- 预警状态：{'风险警报' if self.risk_data['alert'] else '正常'}

五、后续展望
- 短期趋势：{'上涨' if latest['close'] > self.df['close'].rolling(5).mean().iloc[-1] else '下跌'}
- 中期趋势：{'上涨' if latest['close'] > self.df['close'].rolling(20).mean().iloc[-1] else '下跌'}
        """
        
        return report.strip()
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成摘要信息"""
        if self.df is None or len(self.df) == 0:
            return {}
        
        latest = self.df.iloc[-1]
        
        return {
            'date': latest['date'].strftime('%Y-%m-%d'),
            'close': float(latest['close']),
            'change_pct': float(latest['change_pct']),
            'risk_level': self.risk_data['risk_level'],
            'downside_probability': self.risk_data['downside_probability'],
            'alert': self.risk_data['alert']
        }
