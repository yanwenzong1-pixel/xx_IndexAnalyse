"""
因子数据服务模块
负责获取、计算和缓存 25 个核心因子数据
使用本地缓存避免影响页面加载速度
"""

import json
import os
import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
import requests


class FactorDataService:
    """因子数据服务类"""
    
    def __init__(self, cache_dir="data/cache"):
        """
        初始化因子数据服务
        
        Args:
            cache_dir: 缓存数据目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 因子元数据
        self.factors_config = {
            # 资金结构维度 (F1-F5)
            'F1': {'name': '成交额占比', 'unit': '%', 'risk_direction': 'positive'},
            'F2': {'name': '龙虎榜游资净买卖', 'unit': '亿元', 'risk_direction': 'negative'},
            'F3': {'name': '股东质押率', 'unit': '%', 'risk_direction': 'positive'},
            'F4': {'name': '北向/机构持仓占比', 'unit': '%', 'risk_direction': 'negative'},
            'F5': {'name': '融资余额变化', 'unit': '%', 'risk_direction': 'bidirectional'},
            
            # 流动性维度 (L1-L3)
            'L1': {'name': '5 日均成交额', 'unit': '亿元', 'risk_direction': 'negative'},
            'L2': {'name': '20 日均成交额', 'unit': '亿元', 'risk_direction': 'negative'},
            'L3': {'name': '5 日均换手率', 'unit': '%', 'risk_direction': 'bidirectional'},
            
            # 估值与业绩维度 (V1-V6)
            'V1': {'name': 'PE 中位数', 'unit': '分位数', 'risk_direction': 'positive'},
            'V2': {'name': 'PB 中位数', 'unit': '倍', 'risk_direction': 'positive'},
            'V3': {'name': 'PS 中位数', 'unit': '倍', 'risk_direction': 'positive'},
            'V4': {'name': '归母净利润同比增速', 'unit': '%', 'risk_direction': 'negative'},
            'V5': {'name': '营收规模增速', 'unit': '%', 'risk_direction': 'negative'},
            'V6': {'name': '市值规模增速', 'unit': '%', 'risk_direction': 'bidirectional'},
            
            # 政策与制度维度 (P1-P5)
            'P1': {'name': '量化监管政策', 'unit': 'virtual', 'risk_direction': 'positive'},
            'P2': {'name': 'IPO/减持/退市规则变化', 'unit': 'virtual', 'risk_direction': 'positive'},
            'P3': {'name': '财报披露窗口期', 'unit': 'virtual', 'risk_direction': 'positive'},
            'P4': {'name': '市场风格引导政策', 'unit': 'virtual', 'risk_direction': 'bidirectional'},
            'P5': {'name': '宏观政策拐点监控', 'unit': 'virtual', 'risk_direction': 'bidirectional'},
            
            # 宏观环境维度 (M1-M6)
            'M1': {'name': '剩余流动性 (M2-社融)', 'unit': '%', 'risk_direction': 'negative'},
            'M2': {'name': '制造业 PMI', 'unit': '指数', 'risk_direction': 'negative'},
            'M3': {'name': 'PPI', 'unit': '%', 'risk_direction': 'positive'},
            'M4': {'name': 'CPI', 'unit': '%', 'risk_direction': 'bidirectional'},
            'M5': {'name': '市场风险偏好', 'unit': '指数', 'risk_direction': 'negative'},
            'M6': {'name': '利率环境', 'unit': '指数', 'risk_direction': 'negative'},
        }
        
        # 缓存过期时间 (小时)
        self.cache_expiry = {
            'market_data': 1,      # 市场数据 1 小时过期
            'macro_data': 24,      # 宏观数据 24 小时过期
            'policy_data': 24,     # 政策数据 24 小时过期
            'fund_data': 1,        # 资金数据 1 小时过期
        }
    
    def get_all_factors(self, df=None):
        """
        获取所有 25 个因子数据
        
        Args:
            df: 基础市场数据 DataFrame
            
        Returns:
            dict: 包含所有因子数据的字典
        """
        factors = {}
        
        # 从基础数据计算市场相关因子
        if df is not None:
            market_factors = self._calculate_market_factors(df)
            factors.update(market_factors)
        
        # 获取需要外部数据源的因子
        external_factors = self._get_external_factors()
        factors.update(external_factors)
        
        # 保存到缓存
        self._save_to_cache('all_factors', factors)
        
        return factors
    
    def _calculate_market_factors(self, df):
        """
        从基础市场数据计算因子
        
        Args:
            df: 基础市场数据 DataFrame
            
        Returns:
            dict: 市场相关因子
        """
        factors = {}
        
        # F1: 成交额占比 (成交额/总市值，假设总市值 50 亿)
        df['amount_to_market_cap'] = df['amount'] / 5e9 * 100
        factors['F1'] = df['amount_to_market_cap'].iloc[-1]
        
        # F2: 龙虎榜游资净买卖 (简化计算，用成交额变化率代替)
        df['amount_change_ratio'] = df['amount'].pct_change()
        factors['F2'] = df['amount_change_ratio'].iloc[-1] * 100 if not pd.isna(df['amount_change_ratio'].iloc[-1]) else 0
        
        # F3: 股东质押率 (简化为固定值，后续接入真实数据)
        factors['F3'] = 25.0  # 假设平均质押率 25%
        
        # F4: 北向/机构持仓占比 (简化为固定值)
        factors['F4'] = 15.0  # 假设平均持仓占比 15%
        
        # F5: 融资余额变化 (用 5 日均成交额变化率近似)
        df['amount_ma5'] = df['amount'].rolling(5).mean()
        df['amount_ma5_change'] = df['amount_ma5'].pct_change()
        factors['F5'] = df['amount_ma5_change'].iloc[-1] * 100 if not pd.isna(df['amount_ma5_change'].iloc[-1]) else 0
        
        # L1: 5 日均成交额
        factors['L1'] = df['amount'].rolling(5).mean().iloc[-1] / 1e8
        
        # L2: 20 日均成交额
        factors['L2'] = df['amount'].rolling(20).mean().iloc[-1] / 1e8
        
        # L3: 5 日均换手率
        factors['L3'] = df['turnover'].rolling(5).mean().iloc[-1]
        
        # V1-V3: 估值指标 (简化计算，后续接入真实数据)
        # 使用价格波动率近似估值分位数
        volatility_20d = df['change_pct'].rolling(20).std().iloc[-1]
        factors['V1'] = min(100, max(0, 50 + volatility_20d * 10))  # PE 中位数分位数
        factors['V2'] = 2.5 + volatility_20d * 0.5  # PB 中位数
        factors['V3'] = 3.0 + volatility_20d * 0.3  # PS 中位数
        
        # V4-V6: 业绩指标 (简化计算)
        # 用近期涨跌幅近似业绩增速
        recent_return_5d = df['change_pct'].tail(5).sum()
        recent_return_20d = df['change_pct'].tail(20).sum()
        factors['V4'] = recent_return_5d * 2  # 净利润增速
        factors['V5'] = recent_return_5d * 1.5  # 营收增速
        factors['V6'] = recent_return_20d  # 市值增速
        
        return factors
    
    def _get_external_factors(self):
        """
        获取需要外部数据源的因子
        
        Returns:
            dict: 外部因子数据
        """
        external_factors = {}
        
        # 政策与制度维度 (P1-P5) - 从政策数据缓存读取
        policy_data = self._load_from_cache('policy_factors')
        if policy_data is None:
            policy_data = self._fetch_policy_factors()
            self._save_to_cache('policy_factors', policy_data)
        external_factors.update(policy_data)
        
        # 宏观环境维度 (M1-M6) - 从宏观数据缓存读取
        macro_data = self._load_from_cache('macro_factors')
        if macro_data is None:
            macro_data = self._fetch_macro_factors()
            self._save_to_cache('macro_factors', macro_data)
        external_factors.update(macro_data)
        
        return external_factors
    
    def _fetch_policy_factors(self):
        """
        获取政策与制度维度因子
        
        Returns:
            dict: 政策因子数据
        """
        # 简化实现，返回默认值
        # 后续可以接入政策新闻 API 或人工录入
        return {
            'P1': 1,  # 量化监管政策：0=宽松，1=中性，2=收紧
            'P2': 1,  # IPO/减持/退市规则变化：0=宽松，1=中性，2=收紧
            'P3': 0,  # 财报披露窗口期：0=非窗口期，1=窗口期
            'P4': 1,  # 市场风格引导政策：0=利好，1=中性，2=利空
            'P5': 0,  # 宏观政策拐点监控：0=无拐点，1=有拐点
        }
    
    def _fetch_macro_factors(self):
        """
        获取宏观环境维度因子
        
        Returns:
            dict: 宏观因子数据
        """
        # 简化实现，返回默认值
        # 后续可以接入国家统计局 API 或 Wind API
        return {
            'M1': 2.5,  # 剩余流动性 (M2-社融剪刀差) %
            'M2': 50.5,  # 制造业 PMI
            'M3': 1.2,  # PPI %
            'M4': 0.8,  # CPI %
            'M5': 55,   # 市场风险偏好指数
            'M6': 60,   # 利率环境指数
        }
    
    def _load_from_cache(self, cache_key):
        """
        从缓存加载数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            dict or None: 缓存的数据，如果过期或不存在则返回 None
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            expiry_hours = self.cache_expiry.get(cache_key.split('_')[0], 24)
            
            if datetime.now() - cached_time > timedelta(hours=expiry_hours):
                return None  # 缓存过期
            
            return cache_data['data']
        
        except Exception as e:
            print(f"读取缓存失败：{e}")
            return None
    
    def _save_to_cache(self, cache_key, data):
        """
        保存数据到缓存
        
        Args:
            cache_key: 缓存键
            data: 要保存的数据
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败：{e}")
    
    def _calculate_factor_series_from_df(self, df: pd.DataFrame, factor_id: str) -> Optional[pd.Series]:
        """
        基于输入 `df` 计算某个因子在每个交易日的时间序列（用于滚动标准化参照）。

        注意：外部/虚拟因子在当前项目中为常数（或简化常数），因此返回常数序列。
        """
        if df is None or len(df) == 0:
            return None

        idx = df.index

        # ========== 市场相关因子（由 df 派生）==========
        if factor_id == 'F1':  # 成交额占比
            return (df['amount'] / 5e9 * 100).astype(float)
        if factor_id == 'F2':  # 龙虎榜游资净买卖（简化：成交额变化率）
            return (df['amount'].pct_change() * 100).astype(float)
        if factor_id == 'F3':  # 股东质押率（常数化）
            return pd.Series([25.0] * len(df), index=idx, dtype=float)
        if factor_id == 'F4':  # 北向/机构持仓占比（常数化）
            return pd.Series([15.0] * len(df), index=idx, dtype=float)
        if factor_id == 'F5':  # 融资余额变化（简化：5日均成交额变化率）
            amount_ma5 = df['amount'].rolling(5).mean()
            return (amount_ma5.pct_change() * 100).astype(float)

        # 流动性维度
        if factor_id == 'L1':  # 5 日均成交额
            return (df['amount'].rolling(5).mean() / 1e8).astype(float)
        if factor_id == 'L2':  # 20 日均成交额
            return (df['amount'].rolling(20).mean() / 1e8).astype(float)
        if factor_id == 'L3':  # 5 日均换手率
            return df['turnover'].rolling(5).mean().astype(float)

        # 估值与业绩维度（简化：用 change_pct 的滚动波动率/累积收益替代）
        volatility_20d = df['change_pct'].rolling(20).std()
        if factor_id == 'V1':  # PE 中位数分位数（约束到 0-100）
            v1 = 50 + volatility_20d * 10
            return v1.clip(lower=0, upper=100).astype(float)
        if factor_id == 'V2':  # PB 中位数
            return (2.5 + volatility_20d * 0.5).astype(float)
        if factor_id == 'V3':  # PS 中位数
            return (3.0 + volatility_20d * 0.3).astype(float)

        # 业绩增速（简化：5/20日累计涨跌幅）
        rolling_return_5d = df['change_pct'].rolling(5).sum()
        rolling_return_20d = df['change_pct'].rolling(20).sum()
        if factor_id == 'V4':
            return (rolling_return_5d * 2).astype(float)
        if factor_id == 'V5':
            return (rolling_return_5d * 1.5).astype(float)
        if factor_id == 'V6':
            return rolling_return_20d.astype(float)

        # ========== 虚拟/外部因子（当前实现为常数）==========
        policy_factors = None
        macro_factors = None

        if factor_id in {'P1', 'P2', 'P3', 'P4', 'P5'}:
            policy_factors = self._fetch_policy_factors()
            return pd.Series([float(policy_factors[factor_id])] * len(df), index=idx, dtype=float)

        if factor_id in {'M1', 'M2', 'M3', 'M4', 'M5', 'M6'}:
            macro_factors = self._fetch_macro_factors()
            return pd.Series([float(macro_factors[factor_id])] * len(df), index=idx, dtype=float)

        return None

    def get_factor_history(self, factor_id, days=252, df=None):
        """
        获取因子的历史数据 (用于标准化计算)
        
        Args:
            factor_id: 因子 ID (如 'F1', 'L1' 等)
            days: 历史天数，默认 252 个交易日
            df: 可选输入的市场 DataFrame；若提供则使用 `df` 生成确定性的滚动历史参照，
                避免回测中标准化参照的随机漂移。
            
        Returns:
            list: 历史因子数据列表
        """
        # 优先使用 df 生成确定性滚动历史（用于回测/rolling 一致性）
        if df is not None:
            series = self._calculate_factor_series_from_df(df, factor_id)
            if series is not None:
                values = series.dropna().astype(float).tolist()
                return values[-days:] if len(values) > days else values

        cache_file = self.cache_dir / f"{factor_id}_history.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                return history_data[-days:]  # 返回最近 N 天数据
            except:
                pass
        
        # 如果缓存不存在，生成模拟历史数据
        # 实际应用中应该从数据库或 API 获取
        return self._generate_factor_history(factor_id, days)
    
    def _generate_factor_history(self, factor_id, days):
        """
        生成因子历史数据 (模拟)
        
        Args:
            factor_id: 因子 ID
            days: 历史天数
            
        Returns:
            list: 历史因子数据列表
        """
        np.random.seed(hash(factor_id) % 2**32)
        
        # 根据因子类型生成不同特征的数据
        config = self.factors_config.get(factor_id, {})
        risk_direction = config.get('risk_direction', 'positive')
        
        if risk_direction == 'positive':
            # 正向风险因子：均值较高
            mean = 50
            std = 15
        elif risk_direction == 'negative':
            # 负向风险因子：均值较低
            mean = 30
            std = 10
        else:  # bidirectional
            # 双向风险因子：均值在中间
            mean = 50
            std = 20
        
        history = np.random.normal(mean, std, days).tolist()
        
        # 保存到缓存
        cache_file = self.cache_dir / f"{factor_id}_history.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(history, f)
        except:
            pass
        
        return history
    
    def refresh_all_factors(self, df=None):
        """
        强制刷新所有因子数据
        
        Args:
            df: 基础市场数据 DataFrame
            
        Returns:
            dict: 刷新后的因子数据
        """
        # 清除所有缓存
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        
        # 重新获取所有因子
        return self.get_all_factors(df)


# 单例模式
_factor_service_instance = None

def get_factor_service():
    """获取因子服务单例"""
    global _factor_service_instance
    if _factor_service_instance is None:
        _factor_service_instance = FactorDataService()
    return _factor_service_instance
