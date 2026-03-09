import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MicroCapAnalyzer:
    def __init__(self):
        self.base_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        self.secid = "90.BK1158"  # 微盘股指数
        self.data = None
        self.df = None
        self.risk_level = 0
        
    def fetch_data(self):
        """获取微盘股指数数据"""
        params = {
            "cb": "jQuery35108745723541970376_1772087141861",
            "secid": self.secid,
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "end": "20500101",
            "lmt": "1000000",
            "_": "1772703835"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                # 处理JSONP响应
                content = response.text
                json_str = content.split('(', 1)[1].rstrip(')')
                self.data = json.loads(json_str)
                self._parse_data()
                return True
        except Exception as e:
            print(f"数据获取失败: {e}")
        return False
    
    def _parse_data(self):
        """解析数据为DataFrame"""
        if 'data' in self.data and 'klines' in self.data['data']:
            klines = self.data['data']['klines']
            data_list = []
            for kline in klines:
                parts = kline.split(',')
                data_list.append({
                    'date': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[2]),
                    'high': float(parts[3]),
                    'low': float(parts[4]),
                    'volume': float(parts[5]),
                    'amount': float(parts[6]),
                    'amplitude': float(parts[7]),
                    'change_pct': float(parts[8]),
                    'change': float(parts[9]),
                    'turnover': float(parts[10])
                })
            self.df = pd.DataFrame(data_list)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values('date')
            self.df.reset_index(drop=True, inplace=True)
    
    def calculate_liquidity_indicators(self):
        """计算流动性维度指标"""
        if self.df is None:
            return None
        
        # 计算日均成交额/总市值（假设总市值为50亿以下，这里用成交额代替相对值）
        self.df['amount_to_market_cap'] = self.df['amount'] / 5e9  # 假设平均总市值50亿
        
        # 计算5日移动平均换手率
        self.df['avg_turnover_5d'] = self.df['turnover'].rolling(5).mean()
        
        # 计算买卖盘价差（用当日最高价和最低价的比值近似）
        self.df['bid_ask_spread'] = (self.df['high'] - self.df['low']) / self.df['close']
        
        # 计算流动性覆盖率（用成交额的移动平均）
        self.df['liquidity_coverage'] = self.df['amount'].rolling(20).mean()
        
        return {
            'latest_amount_to_market_cap': self.df['amount_to_market_cap'].iloc[-1],
            'latest_avg_turnover_5d': self.df['avg_turnover_5d'].iloc[-1],
            'latest_bid_ask_spread': self.df['bid_ask_spread'].iloc[-1],
            'latest_liquidity_coverage': self.df['liquidity_coverage'].iloc[-1]
        }
    
    def calculate_fund_structure_indicators(self):
        """计算资金结构维度指标"""
        if self.df is None:
            return None
        
        # 计算量化成交额占比（用成交额的变化率近似）
        self.df['amount_change_pct'] = self.df['amount'].pct_change()
        
        # 计算融资余额变化（用成交额的移动平均变化近似）
        self.df['financing_balance_change'] = self.df['amount'].rolling(5).mean().pct_change()
        
        return {
            'latest_amount_change_pct': self.df['amount_change_pct'].iloc[-1],
            'latest_financing_balance_change': self.df['financing_balance_change'].iloc[-1]
        }
    
    def calculate_valuation_indicators(self):
        """计算估值与业绩维度指标"""
        if self.df is None:
            return None
        
        # 计算波动率
        self.df['volatility'] = self.df['change_pct'].rolling(20).std() * np.sqrt(252)
        
        # 计算趋势指标
        self.df['ma5'] = self.df['close'].rolling(5).mean()
        self.df['ma20'] = self.df['close'].rolling(20).mean()
        
        return {
            'latest_volatility': self.df['volatility'].iloc[-1],
            'latest_ma5': self.df['ma5'].iloc[-1],
            'latest_ma20': self.df['ma20'].iloc[-1],
            'ma5_ma20_diff': self.df['ma5'].iloc[-1] - self.df['ma20'].iloc[-1]
        }
    
    def calculate_policy_indicators(self):
        """计算政策与制度维度指标"""
        # 这里需要外部数据，暂时返回占位符
        return {
            'ipo_activity': 0.5,  # 0-1之间的指标
            'regulation_intensity': 0.3,  # 0-1之间的指标
            'financial_report_window': False
        }
    
    def calculate_macro_indicators(self):
        """计算宏观环境维度指标"""
        # 这里需要外部数据，暂时返回占位符
        return {
            'excess_liquidity': 0.2,  # M2-社融剪刀差
            'pmi': 50.5,  # 制造业PMI
            'risk_appetite': 0.6,  # 市场风险偏好
            'interest_rate_env': 0.4  # 利率环境
        }
    
    def assess_risk_level(self):
        """评估风险等级（1-10级）"""
        if self.df is None:
            return 0
        
        # 基础风险分数
        risk_score = 5
        
        # 流动性风险
        liquidity_indicators = self.calculate_liquidity_indicators()
        if liquidity_indicators:
            # 换手率过高
            if liquidity_indicators['latest_avg_turnover_5d'] > 8:
                risk_score += 2
            # 流动性枯竭
            elif liquidity_indicators['latest_amount_to_market_cap'] < 0.001:
                risk_score += 3
        
        # 价格趋势风险
        if len(self.df) > 20:
            # 短期大幅上涨
            recent_change = self.df['change_pct'].tail(5).sum()
            if recent_change > 20:
                risk_score += 2
            # 跌破重要均线
            if self.df['close'].iloc[-1] < self.df['ma20'].iloc[-1]:
                risk_score += 1
        
        # 波动率风险
        volatility = self.df['change_pct'].rolling(20).std().iloc[-1]
        if volatility > 5:
            risk_score += 2
        
        # 限制风险等级在1-10之间
        self.risk_level = max(1, min(10, risk_score))
        return self.risk_level
    
    def predict_downside_risk(self):
        """预测下跌风险"""
        if self.df is None:
            return 0
        
        # 基于历史数据的简单预测
        recent_volatility = self.df['change_pct'].rolling(20).std().iloc[-1]
        recent_trend = self.df['change_pct'].tail(5).mean()
        
        # 计算下跌概率
        downside_probability = 0
        if recent_trend < 0 and recent_volatility > 3:
            downside_probability = min(1, (abs(recent_trend) / 2 + recent_volatility / 10))
        
        return downside_probability
    
    def generate_daily_report(self):
        """生成每日报告"""
        if self.df is None:
            return ""
        
        latest_data = self.df.iloc[-1]
        risk_level = self.assess_risk_level()
        downside_probability = self.predict_downside_risk()
        
        report = f"""
微盘股指数每日监控报告
日期：{latest_data['date'].strftime('%Y-%m-%d')}

一、当日表现
- 收盘：{latest_data['close']:.2f}
- 涨跌幅：{latest_data['change_pct']:.2f}%
- 成交额：{latest_data['amount']/1e8:.2f}亿元
- 换手率：{latest_data['turnover']:.2f}%
- 振幅：{latest_data['amplitude']:.2f}%

二、核心指标
- 5日平均换手率：{self.df['turnover'].tail(5).mean():.2f}%
- 成交额/总市值：{latest_data['amount']/5e9*100:.2f}%
- 20日波动率：{self.df['change_pct'].rolling(20).std().iloc[-1]*100:.2f}%

三、资金结构
- 成交额变化：{self.df['amount'].pct_change().iloc[-1]*100:.2f}%
- 趋势指标：MA5={self.df['close'].rolling(5).mean().iloc[-1]:.2f}, MA20={self.df['close'].rolling(20).mean().iloc[-1]:.2f}

四、风险评级
- 风险等级：{risk_level}/10
- 下跌概率：{downside_probability*100:.2f}%
- 预警状态：{'风险警报' if downside_probability > 0.7 else '正常'}

五、后续展望
- 短期趋势：{'上涨' if self.df['close'].iloc[-1] > self.df['ma5'].iloc[-1] else '下跌'}
- 中期趋势：{'上涨' if self.df['close'].iloc[-1] > self.df['ma20'].iloc[-1] else '下跌'}
        """
        
        return report
    
    def check_alert_conditions(self):
        """检查预警条件"""
        downside_probability = self.predict_downside_risk()
        if downside_probability > 0.7:
            return True, f"微盘股指数下跌风险警报！下跌概率：{downside_probability*100:.2f}%"
        
        # 检查买点信号
        if len(self.df) > 20:
            ma5 = self.df['close'].rolling(5).mean().iloc[-1]
            ma20 = self.df['close'].rolling(20).mean().iloc[-1]
            if ma5 > ma20 and self.df['change_pct'].iloc[-1] > 0:
                return True, "微盘股指数出现买点信号！"
        
        return False, ""
