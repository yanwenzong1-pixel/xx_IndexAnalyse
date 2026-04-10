import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.factor_data_service import get_factor_service
from utils.risk_calculation_service import get_risk_calculator
from utils.decline_calculation_service import calculate_expected_decline_detailed

class MicroCapAnalyzer:
    def __init__(self):
        self.base_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        self.secid = "90.BK1158"  # 微盘股指数
        self.data = None
        self.df = None
        self.risk_level = 0
        
    def fetch_data(self):
        """获取微盘股指数数据"""
        import time
        
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
        
        # 配置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://quote.eastmoney.com/',
            'Connection': 'keep-alive'
        }
        
        # 重试机制：最多尝试 5 次，递增等待时间
        max_retries = 5
        for attempt in range(max_retries):
            try:
                print(f"正在获取数据... (尝试 {attempt + 1}/{max_retries})")
                
                # 尝试直接连接
                response = requests.get(
                    self.base_url, 
                    params=params, 
                    headers=headers,
                    timeout=30,
                    proxies=None  # 不使用代理
                )
                
                if response.status_code == 200:
                    # 处理 JSONP 响应
                    content = response.text
                    
                    # 更健壮的 JSONP 解析
                    start_idx = content.find('(')
                    end_idx = content.rfind(')')
                    
                    if start_idx == -1 or end_idx == -1:
                        raise ValueError("无效的 JSONP 格式")
                    
                    json_str = content[start_idx + 1:end_idx]
                    json_str = json_str.strip()
                    
                    self.data = json.loads(json_str)
                    self._parse_data()
                    # 避免控制台在 GBK 编码下打印 Unicode 表情导致训练脚本中断
                    print(f"数据获取成功，共 {len(self.df)} 条记录")
                    return True
                else:
                    print(f"HTTP 错误：{response.status_code}")
                    
            except requests.exceptions.ProxyError as e:
                print(f"代理错误：{e}")
                print("尝试不使用代理直接连接...")
                continue
            except requests.exceptions.SSLError as e:
                print(f"SSL 错误：{e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败：{e}")
                print(f"响应内容长度：{len(response.text)}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
            except requests.exceptions.Timeout as e:
                print(f"请求超时：{e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
            except requests.exceptions.ConnectionError as e:
                print(f"连接错误：{e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
            except Exception as e:
                print(f"数据获取失败：{e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        # 避免控制台在 GBK 编码下打印 Unicode 表情导致训练脚本中断
        print("数据获取失败：超过最大重试次数")
        print("提示：将使用静态历史数据或缓存数据")
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
        """评估风险等级（1-10 级，支持连续小数）"""
        if self.df is None:
            return 0
        
        # 确保必要的指标已计算
        if 'ma20' not in self.df.columns:
            self.df['ma20'] = self.df['close'].rolling(20).mean()
        if 'ma5' not in self.df.columns:
            self.df['ma5'] = self.df['close'].rolling(5).mean()
        if 'volatility' not in self.df.columns:
            self.df['volatility'] = self.df['change_pct'].rolling(20).std() * np.sqrt(252)
        if 'ma20_20d' not in self.df.columns:
            self.df['ma20_20d'] = self.df['amount'].rolling(20).mean()
        
        # 基础风险分数（降低至 3.0，让风险分数更敏感）
        risk_score = 3.0
        
        # ========== 1. 流动性风险（权重 20%）==========
        liquidity_indicators = self.calculate_liquidity_indicators()
        if liquidity_indicators:
            turnover = liquidity_indicators['latest_avg_turnover_5d']
            # 换手率风险（降低阈值）
            if turnover > 12:
                risk_score += 2.0
            elif turnover > 8:
                risk_score += 1.0 + (turnover - 8) / 4.0
            elif turnover > 5:
                risk_score += (turnover - 5) / 3.0
            
            # 流动性枯竭风险
            amount_ratio = liquidity_indicators['latest_amount_to_market_cap']
            if amount_ratio < 0.0005:
                risk_score += 3.0
            elif amount_ratio < 0.001:
                risk_score += 2.0 + (0.001 - amount_ratio) / 0.0005
            elif amount_ratio < 0.002:
                risk_score += 1.0 + (0.002 - amount_ratio) / 0.001
        
        # ========== 2. 单日暴跌风险（新增，权重 20%）==========
        daily_change = self.df['change_pct'].iloc[-1]
        
        if daily_change < -7:
            risk_score += 2.0
        elif daily_change < -5:
            risk_score += 1.5
        elif daily_change < -3:
            risk_score += 1.0
        elif daily_change < -2:
            risk_score += 0.5
        
        # ========== 3. 价格趋势风险（双向计算，权重 25%）==========
        if len(self.df) > 20:
            recent_change = self.df['change_pct'].tail(5).sum()
            
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
            close_price = self.df['close'].iloc[-1]
            ma20_price = self.df['ma20'].iloc[-1]
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
        for i in range(min(5, len(self.df))):
            if self.df['change_pct'].iloc[-(i+1)] < 0:
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
        volatility = self.df['change_pct'].rolling(20).std().iloc[-1]
        if volatility > 8:
            risk_score += 2.0
        elif volatility > 5:
            risk_score += 1.0 + (volatility - 5) / 3.0
        elif volatility > 3:
            risk_score += (volatility - 3) / 2.0
        
        # ========== 6. 成交量异常风险（新增，权重 10%）==========
        avg_amount_20d = self.df['ma20_20d'].iloc[-1]
        current_amount = self.df['amount'].iloc[-1]
        
        if avg_amount_20d > 0:
            amount_ratio_20d = current_amount / avg_amount_20d
            
            # 成交量异常放大（>150%）
            if amount_ratio_20d > 1.5:
                risk_score += 1.0
            # 成交量异常萎缩（<50%）
            elif amount_ratio_20d < 0.5:
                risk_score += 1.5
        
        # 限制风险等级在 1-10 之间，保留 2 位小数
        self.risk_level = round(max(1.0, min(10.0, risk_score)), 2)
        return self.risk_level
    
    def predict_downside_risk(self):
        """预测下跌风险 - 使用新的多因子模型"""
        if self.df is None:
            return 0
        
        # 获取因子服务和风险计算器
        factor_service = get_factor_service()
        risk_calculator = get_risk_calculator()
        
        # 获取所有25个因子数据
        factors = factor_service.get_all_factors(self.df)
        
        # 计算下跌概率
        results = risk_calculator.predict_downside_probability(factors, self.df)
        
        # 返回T+1下跌概率
        return results['prob_t1']

    def predict_downside_probability_detailed(self):
        """详细预测下跌概率 - 返回T+1和T+5概率及中间结果"""
        if self.df is None:
            return {
                'prob_t1': 0,
                'prob_t5': 0,
                'base_risk': 0,
                'adjusted_risk': 0,
                'trend_adjustment': 1.0,
                'volatility_20d': 0,
                'momentum_1d': 0,
                'momentum_5d': 0
            }
        
        # 获取因子服务和风险计算器
        factor_service = get_factor_service()
        risk_calculator = get_risk_calculator()
        
        # 获取所有25个因子数据
        factors = factor_service.get_all_factors(self.df)
        
        # 计算下跌概率
        results = risk_calculator.predict_downside_probability(factors, self.df)
        
        return results
    
    def generate_daily_report(self):
        """生成每日报告"""
        if self.df is None:
            return ""
        
        latest_data = self.df.iloc[-1]
        risk_level = self.assess_risk_level()
        
        # 获取详细预测结果
        prediction_results = self.predict_downside_probability_detailed()
        prob_t1 = prediction_results['prob_t1']
        prob_t5 = prediction_results['prob_t5']
        
        # 计算预期跌幅
        decline_results = calculate_expected_decline_detailed(prediction_results)
        
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
- 5 日平均换手率：{self.df['turnover'].tail(5).mean():.2f}%
- 成交额/总市值：{latest_data['amount']/5e9*100:.2f}%
- 20 日波动率：{self.df['change_pct'].rolling(20).std().iloc[-1]*100:.2f}%

三、资金结构
- 成交额变化：{self.df['amount'].pct_change().iloc[-1]*100:.2f}%
- 趋势指标：MA5={self.df['close'].rolling(5).mean().iloc[-1]:.2f}, MA20={self.df['close'].rolling(20).mean().iloc[-1]:.2f}

四、风险评级
- 风险等级：{risk_level}/10
- 次日下跌概率：{prob_t1*100:.2f}%
- 5 日内下跌概率：{prob_t5*100:.2f}%
- 次日预期跌幅：{decline_results['t1']['expected_decline']:.2f}% (区间：{decline_results['t1']['lower_bound']:.2f}% ~ {decline_results['t1']['upper_bound']:.2f}%)
- 5 日内预期跌幅：{decline_results['t5']['expected_decline']:.2f}% (区间：{decline_results['t5']['lower_bound']:.2f}% ~ {decline_results['t5']['upper_bound']:.2f}%)
- 预警状态：{'风险警报' if prob_t1 > 0.7 else '正常'}

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
