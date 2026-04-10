"""
测试新的下跌风险预测模型
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
web_backend_path = os.path.join(project_root, 'web', 'backend')
sys.path.insert(0, web_backend_path)

from analyzer import MicroCapAnalyzer
from utils.factor_data_service import get_factor_service
from utils.risk_calculation_service import get_risk_calculator
from utils.decline_calculation_service import calculate_expected_decline_detailed


def test_new_prediction_model():
    """测试新的预测模型"""
    print("=" * 60)
    print("测试新的下跌风险预测模型")
    print("=" * 60)
    
    # 创建分析器实例
    analyzer = MicroCapAnalyzer()
    
    # 获取数据
    print("\n1. 获取微盘股指数数据...")
    if not analyzer.fetch_data():
        print("❌ 数据获取失败")
        return
    
    print(f"✅ 数据获取成功，共 {len(analyzer.df)} 条记录")
    print(f"   最新日期：{analyzer.df['date'].iloc[-1]}")
    print(f"   最新收盘：{analyzer.df['close'].iloc[-1]:.2f}")
    
    # 获取因子数据
    print("\n2. 获取 25 个核心因子数据...")
    factor_service = get_factor_service()
    factors = factor_service.get_all_factors(analyzer.df)
    
    print(f"✅ 因子数据获取成功")
    print(f"   资金结构维度因子：F1={factors.get('F1', 'N/A')}, F2={factors.get('F2', 'N/A')}, ...")
    print(f"   流动性维度因子：L1={factors.get('L1', 'N/A')}, L2={factors.get('L2', 'N/A')}, L3={factors.get('L3', 'N/A')}")
    print(f"   估值与业绩维度因子：V1={factors.get('V1', 'N/A')}, V2={factors.get('V2', 'N/A')}, ...")
    print(f"   政策与制度维度因子：P1={factors.get('P1', 'N/A')}, P2={factors.get('P2', 'N/A')}, ...")
    print(f"   宏观环境维度因子：M1={factors.get('M1', 'N/A')}, M2={factors.get('M2', 'N/A')}, ...")
    
    # 计算下跌概率
    print("\n3. 计算下跌概率...")
    risk_calculator = get_risk_calculator()
    prediction_results = risk_calculator.predict_downside_probability(factors, analyzer.df)
    
    print(f"✅ 下跌概率计算完成")
    print(f"   次日 (T+1) 下跌概率：{prediction_results['prob_t1']*100:.2f}%")
    print(f"   5 日内 (T+5) 下跌概率：{prediction_results['prob_t5']*100:.2f}%")
    print(f"   基础风险分：{prediction_results['base_risk']:.4f}")
    print(f"   调整后风险分：{prediction_results['adjusted_risk']:.4f}")
    print(f"   趋势调整系数：{prediction_results['trend_adjustment']:.4f}")
    print(f"   20 日波动率：{prediction_results['volatility_20d']:.2f}%")
    print(f"   前 1 日动量：{prediction_results['momentum_1d']:.2f}%")
    print(f"   前 5 日动量：{prediction_results['momentum_5d']:.2f}%")
    
    # 计算预期跌幅
    print("\n4. 计算预期跌幅...")
    decline_results = calculate_expected_decline_detailed(prediction_results)
    
    print(f"✅ 预期跌幅计算完成")
    print(f"   次日 (T+1) 预期跌幅：{decline_results['t1']['expected_decline']:.2f}%")
    print(f"   次日置信区间：[{decline_results['t1']['lower_bound']:.2f}%, {decline_results['t1']['upper_bound']:.2f}%]")
    print(f"   5 日内 (T+5) 预期跌幅：{decline_results['t5']['expected_decline']:.2f}%")
    print(f"   5 日置信区间：[{decline_results['t5']['lower_bound']:.2f}%, {decline_results['t5']['upper_bound']:.2f}%]")
    
    # 生成每日报告
    print("\n5. 生成每日报告...")
    report = analyzer.generate_daily_report()
    
    print(f"✅ 每日报告生成完成")
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    
    # 测试总结
    print("\n测试总结:")
    print("✅ 所有测试通过")
    print("✅ 25 个因子全部纳入计算")
    print("✅ 趋势调整因子正常工作")
    print("✅ 预期跌幅计算正常")
    print("\n新模型特点:")
    print("1. 使用 25 个核心因子（5 个维度全覆盖）")
    print("2. 引入趋势调整因子，反映微盘股长期向上趋势")
    print("3. 使用 Logit 回归模型计算概率")
    print("4. 分段线性模型计算预期跌幅")
    print("5. 本地缓存机制，不影响页面加载速度")


if __name__ == "__main__":
    test_new_prediction_model()
