"""
因子标准化和风险计算模块
实现 25 个因子的标准化处理和风险分计算
"""

import os
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata
from utils.factor_data_service import get_factor_service


class FactorStandardizer:
    """因子标准化器"""
    
    def __init__(self):
        self.factor_service = get_factor_service()
    
    def normalize(self, factor_value, factor_id, window_days=252, df_context=None):
        """
        使用分位数滚动标准化对因子进行标准化
        
        Args:
            factor_value: 当前因子值
            factor_id: 因子 ID (如 'F1', 'L1' 等)
            window_days: 滚动窗口天数，默认 252 个交易日
            
        Returns:
            float: 标准化后的值 (0-1 区间)
        """
        # 获取历史数据
        history = self.factor_service.get_factor_history(factor_id, window_days, df=df_context)
        
        if not history:
            # 如果历史数据不足，返回默认值
            return 0.5
        
        # 添加当前值到历史数据
        extended_history = history + [factor_value]
        
        # 计算分位数排名
        ranks = rankdata(extended_history, method='average')
        normalized_value = ranks[-1] / len(extended_history)  # 当前值的分位数排名
        
        return min(1.0, max(0.0, normalized_value))  # 确保在 [0,1] 区间
    
    def normalize_bidirectional(self, factor_value, factor_id, optimal_value=None, window_days=252, df_context=None):
        """
        对双向风险因子进行标准化处理 (距离最优值的标准化)
        
        Args:
            factor_value: 当前因子值
            factor_id: 因子 ID
            optimal_value: 最优值 (如果不提供，则根据历史数据计算)
            window_days: 滚动窗口天数
            
        Returns:
            float: 标准化后的值 (0-1 区间，越接近最优值越小（风险越低）)
        """
        # 获取历史数据
        history = self.factor_service.get_factor_history(factor_id, window_days, df=df_context)
        
        if not history:
            return 0.5
        
        # 如果未指定最优值，使用历史中位数作为最优值
        if optimal_value is None:
            optimal_value = np.median(history)
        
        # 计算与最优值的距离
        distance = abs(factor_value - optimal_value)
        
        # 计算历史数据的最大最小距离
        distances_from_optimal = [abs(x - optimal_value) for x in history]
        max_distance = max(distances_from_optimal) if distances_from_optimal else 1
        
        if max_distance == 0:
            return 0.0
        
        # 标准化距离
        normalized_distance = min(1.0, distance / max_distance)
        
        # 返回“距离归一化结果”：距离越小风险越低
        return normalized_distance
    
    def normalize_virtual(self, factor_value, factor_id):
        """
        对虚拟变量进行标准化处理
        
        Args:
            factor_value: 虚拟变量值 (0, 1, 2)
            factor_id: 因子 ID
            
        Returns:
            float: 标准化后的值 (0-1 区间)
        """
        # 假设虚拟变量是 0-2 的整数，标准化到 0-1
        if isinstance(factor_value, (int, float)):
            return min(1.0, max(0.0, factor_value / 2.0))
        return 0.5


class RiskCalculator:
    """风险计算器"""
    
    def __init__(self):
        self.standardizer = FactorStandardizer()
        
        # prob_model_params.json 的路径/mtime，用于运行时自动热重载
        self._prob_model_params_path = (
            Path(__file__).resolve().parents[1] / "data" / "prob_model_params.json"
        )
        self._prob_model_params_mtime = None
        
        # 各维度权重
        self.dimension_weights = {
            'fund': 0.25,      # 资金结构
            'liquidity': 0.20, # 流动性
            'valuation': 0.20, # 估值与业绩
            'policy': 0.20,    # 政策与制度
            'macro': 0.15      # 宏观环境
        }
        
        # 各因子权重 (在各自维度内的权重)
        self.factor_weights = {
            # 资金结构维度 (F1-F5)
            'F1': 0.25,  # 成交额占比
            'F2': 0.25,  # 龙虎榜游资净买卖
            'F3': 0.20,  # 股东质押率
            'F4': 0.20,  # 北向/机构持仓占比
            'F5': 0.10,  # 融资余额变化
            
            # 流动性维度 (L1-L3)
            'L1': 0.4,   # 5 日均成交额
            'L2': 0.4,   # 20 日均成交额
            'L3': 0.2,   # 5 日均换手率
            
            # 估值与业绩维度 (V1-V6)
            'V1': 0.2,   # PE 中位数
            'V2': 0.15,  # PB 中位数
            'V3': 0.15,  # PS 中位数
            'V4': 0.2,   # 归母净利润同比增速
            'V5': 0.15,  # 营收规模增速
            'V6': 0.15,  # 市值规模增速
            
            # 政策与制度维度 (P1-P5)
            'P1': 0.2,   # 量化监管政策
            'P2': 0.2,   # IPO/减持/退市规则变化
            'P3': 0.2,   # 财报披露窗口期
            'P4': 0.2,   # 市场风格引导政策
            'P5': 0.2,   # 宏观政策拐点监控
            
            # 宏观环境维度 (M1-M6)
            'M1': 0.17,  # 剩余流动性
            'M2': 0.17,  # 制造业 PMI
            'M3': 0.16,  # PPI
            'M4': 0.16,  # CPI
            'M5': 0.17,  # 市场风险偏好
            'M6': 0.17   # 利率环境
        }

        # 下跌概率模型参数（可训练/可校准）
        self.prob_model_params = self._load_probability_model_params()
        self._maybe_reload_probability_model_params(force=True)

    def _load_probability_model_params(self):
        """
        从 `web/backend/data/prob_model_params.json` 加载可训练的参数与温度缩放系数。
        失败时回退到代码内默认值。
        """
        default_params = {
            "version": 1,
            "temperature_t1": 1.0,
            "temperature_t5": 1.0,
            "t1_weights": {
                "alpha_0": -1.5,
                "alpha_1": 2.0,
                "alpha_2": 0.5,
                "alpha_3": 0.03,
                "alpha_4": -0.02
            },
            "t5_weights": {
                "beta_0": -1.2,
                "beta_1": 1.8,
                "beta_2": 0.4,
                "beta_3": 0.04,
                "beta_4": -0.03,
                "beta_5": 0.05,
                "beta_6": -0.02
            }
        }

        try:
            if self._prob_model_params_path.exists():
                with open(self._prob_model_params_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # 兜底：合并默认值，避免缺字段
                merged = default_params.copy()
                merged.update(loaded)
                if "t1_weights" in loaded:
                    merged["t1_weights"] = {**default_params["t1_weights"], **loaded["t1_weights"]}
                if "t5_weights" in loaded:
                    merged["t5_weights"] = {**default_params["t5_weights"], **loaded["t5_weights"]}
                return merged
        except Exception:
            pass

        return default_params

    def _maybe_reload_probability_model_params(self, force: bool = False) -> None:
        """
        如果 prob_model_params.json 在运行期间发生变更，则热重载。
        主要用于解决“修改参数文件但界面/趋势不更新”的问题。
        """
        try:
            if not self._prob_model_params_path.exists():
                return

            mtime = os.path.getmtime(str(self._prob_model_params_path))
            if force or self._prob_model_params_mtime is None or mtime > self._prob_model_params_mtime:
                self.prob_model_params = self._load_probability_model_params()
                self._prob_model_params_mtime = mtime
        except Exception:
            # 热重载失败不应影响预测主流程
            return
    
    def calculate_dimension_risks(self, factors, df_context=None):
        """
        计算各维度风险分
        
        Args:
            factors: 所有因子数据字典
            
        Returns:
            dict: 各维度风险分
        """
        dimension_risks = {}
        
        # 资金结构维度风险分 (S_fund)
        fund_factors = ['F1', 'F2', 'F3', 'F4', 'F5']
        fund_risks = []
        for fid in fund_factors:
            if fid in factors:
                # F2 和 F4 是负向风险 (值越大风险越小)，需要反向处理
                if fid in ['F2', 'F4']:  # 负向风险因子
                    norm_value = self.standardizer.normalize(
                        -factors[fid], fid, df_context=df_context
                    )
                else:  # 正向风险因子
                    norm_value = self.standardizer.normalize(
                        factors[fid], fid, df_context=df_context
                    )
                
                weight = self.factor_weights.get(fid, 0.2)
                fund_risks.append(norm_value * weight)
        
        dimension_risks['fund'] = sum(fund_risks)
        
        # 流动性维度风险分 (S_liquidity)
        liquidity_factors = ['L1', 'L2', 'L3']
        liquidity_risks = []
        for fid in liquidity_factors:
            if fid in factors:
                if fid in ['L1', 'L2']:  # 负向风险因子
                    norm_value = self.standardizer.normalize(
                        -factors[fid], fid, df_context=df_context
                    )
                else:  # L3 是双向风险因子
                    norm_value = self.standardizer.normalize_bidirectional(
                        factors[fid],
                        fid,
                        optimal_value=5.0,  # 最优换手率 5%
                        df_context=df_context,
                    )
                
                weight = self.factor_weights.get(fid, 0.33)
                liquidity_risks.append(norm_value * weight)
        
        dimension_risks['liquidity'] = sum(liquidity_risks)
        
        # 估值与业绩维度风险分 (S_valuation)
        valuation_factors = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        valuation_risks = []
        for fid in valuation_factors:
            if fid in factors:
                if fid in ['V4', 'V5']:  # 负向风险因子
                    norm_value = self.standardizer.normalize(
                        -factors[fid], fid, df_context=df_context
                    )
                else:  # V1, V2, V3, V6 是正向或双向风险因子
                    if fid == 'V6':  # V6 是双向风险因子
                        norm_value = self.standardizer.normalize_bidirectional(
                            factors[fid],
                            fid,
                            optimal_value=10.0,  # 最优市值增速 10%
                            df_context=df_context,
                        )
                    else:  # V1, V2, V3 是正向风险因子
                        norm_value = self.standardizer.normalize(
                            factors[fid], fid, df_context=df_context
                        )
                
                weight = self.factor_weights.get(fid, 0.17)
                valuation_risks.append(norm_value * weight)
        
        dimension_risks['valuation'] = sum(valuation_risks)
        
        # 政策与制度维度风险分 (S_policy)
        policy_factors = ['P1', 'P2', 'P3', 'P4', 'P5']
        policy_risks = []
        for fid in policy_factors:
            if fid in factors:
                # P4, P5 是双向风险因子，其他是正向风险因子
                if fid in ['P4', 'P5']:
                    # 对于双向风险，计算与中性值(1)的距离
                    norm_value = abs(factors[fid] - 1)  # 结果为 0, 1, 或 2-1=1
                    norm_value = min(1.0, norm_value)  # 标准化到 0-1
                else:
                    norm_value = self.standardizer.normalize_virtual(factors[fid], fid)
                
                weight = self.factor_weights.get(fid, 0.2)
                policy_risks.append(norm_value * weight)
        
        dimension_risks['policy'] = sum(policy_risks)
        
        # 宏观环境维度风险分 (S_macro)
        macro_factors = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
        macro_risks = []
        for fid in macro_factors:
            if fid in factors:
                # 按配置决定风险方向，避免 M1/M3/M2... 与 factors_config 不一致
                factor_meta = self.standardizer.factor_service.factors_config.get(fid, {})
                risk_direction = factor_meta.get('risk_direction', 'positive')
                
                if risk_direction == 'negative':
                    norm_value = self.standardizer.normalize(
                        -factors[fid], fid, df_context=df_context
                    )
                elif risk_direction == 'bidirectional':
                    # 双向风险的“最优值”目前仅为 M4 维度显式配置
                    optimal_map = {'M4': 2.0}
                    norm_value = self.standardizer.normalize_bidirectional(
                        factors[fid],
                        fid,
                        optimal_value=optimal_map.get(fid),
                        df_context=df_context,
                    )
                else:  # positive
                    norm_value = self.standardizer.normalize(
                        factors[fid], fid, df_context=df_context
                    )
                
                weight = self.factor_weights.get(fid, 0.17)
                macro_risks.append(norm_value * weight)
        
        dimension_risks['macro'] = sum(macro_risks)
        
        return dimension_risks
    
    def calculate_trend_adjustment(self, df):
        """
        计算趋势调整因子
        
        Args:
            df: 基础市场数据 DataFrame
            
        Returns:
            float: 趋势调整系数 (0-1 区间)
        """
        if df is None or len(df) < 20:
            return 1.0  # 默认不调整
        
        # 计算各组成部分
        # MA5/MA20 比值
        ma5 = df['close'].rolling(5).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma_ratio = ma5 / ma20 if ma20 != 0 else 1.0
        
        # 指数相对中期均线的偏离度
        price_deviation = (df['close'].iloc[-1] - ma20) / ma20
        
        # 20 日动量指标
        momentum_20d = df['change_pct'].tail(20).sum()
        
        # 综合趋势因子
        trend_factor = 0.4 * ma_ratio + 0.3 * price_deviation + 0.3 * (momentum_20d / 100)
        
        # 使用 Sigmoid 函数将趋势因子映射到 (0,1) 区间
        k = 2  # 敏感系数
        adjustment = 1 / (1 + np.exp(-k * trend_factor))
        
        return adjustment
    
    def calculate_comprehensive_risk(self, factors, df=None):
        """
        计算综合风险分
        
        Args:
            factors: 所有因子数据字典
            df: 基础市场数据 DataFrame
            
        Returns:
            tuple: (基础风险分, 调整后风险分, 趋势调整系数)
        """
        # 计算各维度风险分
        dimension_risks = self.calculate_dimension_risks(factors, df_context=df)
        
        # 计算基础风险分
        base_risk = 0
        for dim, weight in self.dimension_weights.items():
            base_risk += dimension_risks.get(dim, 0) * weight
        
        # 计算趋势调整系数
        trend_adjustment = self.calculate_trend_adjustment(df)
        
        # 计算调整后风险分
        # trend_adjustment 越大表示趋势越强（更偏向上涨），因此应当降低“下跌风险”。
        adjusted_risk = base_risk * (1.0 - trend_adjustment)
        
        return base_risk, adjusted_risk, trend_adjustment
    
    def predict_downside_probability(self, factors, df=None):
        """
        预测下跌概率
        
        Args:
            factors: 所有因子数据字典
            df: 基础市场数据 DataFrame
            
        Returns:
            dict: 包含 T+1 和 T+5 预测概率的字典
        """
        # 运行时自动刷新参数，避免单例缓存造成“参数改了但结果不变”
        self._maybe_reload_probability_model_params()

        # 计算综合风险分
        base_risk, adjusted_risk, trend_adj = self.calculate_comprehensive_risk(factors, df)
        
        # 计算波动率
        if df is not None and len(df) > 20:
            volatility_20d = df['change_pct'].rolling(20).std().iloc[-1]
        else:
            volatility_20d = 2.0  # 默认波动率
        
        # 计算动量
        if df is not None and len(df) > 5:
            momentum_1d = df['change_pct'].iloc[-1]  # 前1日涨跌幅
            momentum_5d = df['change_pct'].tail(5).sum()  # 前5日累计涨跌幅
        else:
            momentum_1d = 0.0
            momentum_5d = 0.0
        
        # T+1 下跌概率 (Logit 模型)
        # ln(P/(1-P)) = α₀ + α₁·R_adjusted + α₂·R_adjusted² + α₃·Volatility_20d + α₄·Momentum_1d
        t1w = self.prob_model_params.get('t1_weights', {})
        alpha_0 = float(t1w.get('alpha_0', -1.5))  # 截距项
        alpha_1 = float(t1w.get('alpha_1', 2.0))   # 风险分线性项系数
        alpha_2 = float(t1w.get('alpha_2', 0.5))   # 风险分二次项系数
        alpha_3 = float(t1w.get('alpha_3', 0.03))  # 波动率系数
        alpha_4 = float(t1w.get('alpha_4', -0.02)) # 动量系数
        temperature_t1 = float(self.prob_model_params.get('temperature_t1', 1.0) or 1.0)
        if temperature_t1 <= 0:
            temperature_t1 = 1.0
        
        linear_combination_t1 = (
            alpha_0 + 
            alpha_1 * adjusted_risk + 
            alpha_2 * (adjusted_risk ** 2) + 
            alpha_3 * volatility_20d + 
            alpha_4 * momentum_1d
        )

        # 温度缩放（概率校准）
        linear_combination_t1 = linear_combination_t1 / temperature_t1
        
        # 反解概率
        prob_t1 = 1 / (1 + np.exp(-linear_combination_t1))
        
        # T+5 下跌概率 (扩展 Logit 模型)
        # ln(P/(1-P)) = β₀ + β₁·R_adjusted + β₂·R_adjusted² + β₃·Volatility_20d + β₄·Momentum_5d + β₅·MacroUncertainty + β₆·(R_adjusted · Momentum_5d)
        t5w = self.prob_model_params.get('t5_weights', {})
        beta_0 = float(t5w.get('beta_0', -1.2))
        beta_1 = float(t5w.get('beta_1', 1.8))
        beta_2 = float(t5w.get('beta_2', 0.4))
        beta_3 = float(t5w.get('beta_3', 0.04))
        beta_4 = float(t5w.get('beta_4', -0.03))
        beta_5 = float(t5w.get('beta_5', 0.05))
        beta_6 = float(t5w.get('beta_6', -0.02))
        temperature_t5 = float(self.prob_model_params.get('temperature_t5', 1.0) or 1.0)
        if temperature_t5 <= 0:
            temperature_t5 = 1.0
        
        # 简化的宏观不确定性指数 (基于 PMI, PPI, CPI 波动)
        macro_uncertainty = 0.1  # 默认值，后续可从宏观数据计算
        if 'M2' in factors and 'M3' in factors and 'M4' in factors:
            macro_uncertainty = (abs(factors['M2'] - 50) / 50 + 
                                abs(factors['M3']) / 10 + 
                                abs(factors['M4'] - 2) / 2) / 3
        
        linear_combination_t5 = (
            beta_0 + 
            beta_1 * adjusted_risk + 
            beta_2 * (adjusted_risk ** 2) + 
            beta_3 * volatility_20d + 
            beta_4 * momentum_5d + 
            beta_5 * macro_uncertainty + 
            beta_6 * (adjusted_risk * momentum_5d)
        )

        # 温度缩放（概率校准）
        linear_combination_t5 = linear_combination_t5 / temperature_t5
        
        # 反解概率
        prob_t5 = 1 / (1 + np.exp(-linear_combination_t5))
        
        # 数值保护：避免极端概率导致 logloss/校准计算出现 log(0)
        eps = 1e-6
        prob_t1 = float(np.clip(prob_t1, eps, 1.0 - eps))
        prob_t5 = float(np.clip(prob_t5, eps, 1.0 - eps))
        
        return {
            'prob_t1': prob_t1,
            'prob_t5': prob_t5,
            'base_risk': base_risk,
            'adjusted_risk': adjusted_risk,
            'trend_adjustment': trend_adj,
            'volatility_20d': volatility_20d,
            'momentum_1d': momentum_1d,
            'momentum_5d': momentum_5d
        }


# 单例模式
_risk_calculator_instance = None

def get_risk_calculator():
    """获取风险计算器单例"""
    global _risk_calculator_instance
    if _risk_calculator_instance is None:
        _risk_calculator_instance = RiskCalculator()
    return _risk_calculator_instance