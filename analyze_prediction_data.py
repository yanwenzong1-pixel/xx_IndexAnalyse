"""
数据一致性分析脚本
分析下跌风险预测数据不匹配的原因
"""

import numpy as np
import pandas as pd

def analyze_probability_range():
    """分析当前代码生成的概率范围"""
    print("=" * 70)
    print("问题 1：近 100 个交易日下跌概率趋势分析")
    print("=" * 70)
    
    # 前端代码中的生成逻辑
    print("\n前端代码中的生成逻辑（第 1248-1249 行）：")
    print("  T+1 概率：seededRandom(dateSeed) * 60 + 20  # 范围 20-80%")
    print("  T+5 概率：seededRandom(dateSeed + 1000) * 50 + 30  # 范围 30-80%")
    
    print("\n实际观察到的波动范围：25%-75%")
    print("理论波动范围：20%-80% (T+1), 30%-80% (T+5)")
    
    # 模拟生成 100 个数据点
    np.random.seed(42)
    t1_probs = np.random.random(100) * 60 + 20
    t5_probs = np.random.random(100) * 50 + 30
    
    print(f"\n模拟统计结果：")
    print(f"  T+1 概率：最小值={t1_probs.min():.1f}%, 最大值={t1_probs.max():.1f}%, 平均值={t1_probs.mean():.1f}%")
    print(f"  T+5 概率：最小值={t5_probs.min():.1f}%, 最大值={t5_probs.max():.1f}%, 平均值={t5_probs.mean():.1f}%")
    
    print("\n结论：前端生成的数据范围 (25%-75%) 在理论范围 (20%-80%) 内，属于正常波动")


def analyze_data_mismatch():
    """分析两个模块数据不匹配的原因"""
    print("\n" + "=" * 70)
    print("问题 2：下跌风险预测 vs 综合风险评估 - 数据不匹配分析")
    print("=" * 70)
    
    print("\n观察到的数据：")
    print("  下跌风险预测模块：")
    print("    - 次日下跌概率：51%")
    print("    - 5 日内下跌概率：49%")
    print("\n  综合风险评估模块：")
    print("    - 次日下跌概率：42%")
    print("    - 5 日内下跌概率：58%")
    
    print("\n差异分析：")
    print("  1. 次日下跌概率差异：51% - 42% = 9%")
    print("  2. 5 日内下跌概率差异：49% - 58% = -9%")
    
    print("\n根本原因定位：")
    print("  ✓ 下跌风险预测模块：使用前端模拟数据（第 1248-1249 行）")
    print("    - T+1 Prob = seededRandom(dateSeed) * 60 + 20")
    print("    - T+5 Prob = seededRandom(dateSeed + 1000) * 50 + 30")
    print("\n  ✓ 综合风险评估模块：使用后端真实计算数据")
    print("    - 调用 /api/predict 接口")
    print("    - 使用 25 因子模型计算（risk_calculation_service.py）")
    print("    - T+1 概率公式：1 / (1 + exp(-linear_combination_t1))")
    print("    - T+5 概率公式：1 / (1 + exp(-linear_combination_t5))")
    
    print("\n数据源对比：")
    print("  ┌─────────────────────┬──────────────────┬──────────────────┐")
    print("  │ 模块                │ 数据源           │ 计算方式         │")
    print("  ├─────────────────────┼──────────────────┼──────────────────┤")
    print("  │ 下跌风险预测        │ 前端模拟生成     │ 随机数种子生成   │")
    print("  │ 综合风险评估        │ 后端 API 实时计算  │ 25 因子 Logit 模型  │")
    print("  └─────────────────────┴──────────────────┴──────────────────┘")


def analyze_formula_consistency():
    """分析计算公式与实际数据的匹配性"""
    print("\n" + "=" * 70)
    print("问题 3：计算公式与数据匹配性分析")
    print("=" * 70)
    
    print("\n后端计算公式（risk_calculation_service.py 第 319-409 行）：")
    print("\nT+1 模型：")
    print("  ln(P/(1-P)) = α₀ + α₁·R_adjusted + α₂·R_adjusted² + α₃·Volatility + α₄·Momentum")
    print("  参数：α₀=-1.5, α₁=2.0, α₂=0.5, α₃=0.03, α₄=-0.02")
    print("\nT+5 模型：")
    print("  ln(P/(1-P)) = β₀ + β₁·R_adjusted + β₂·R_adjusted² + β₃·Volatility + β₄·Momentum_5d")
    print("              + β₅·MacroUncertainty + β₆·(R_adjusted · Momentum_5d)")
    print("  参数：β₀=-1.2, β₁=1.8, β₂=0.4, β₃=0.04, β₄=-0.03, β₅=0.05, β₆=-0.02")
    
    print("\n前端模拟数据逻辑（index.html 第 1248-1249 行）：")
    print("  T+1 Prob = seededRandom(dateSeed) * 60 + 20  # 20-80%")
    print("  T+5 Prob = seededRandom(dateSeed + 1000) * 50 + 30  # 30-80%")
    
    print("\n匹配性分析：")
    print("  ✗ 前端模拟数据与后端计算公式完全不一致")
    print("  ✗ 前端使用固定范围的随机数，未使用 25 因子模型")
    print("  ✗ 前端未考虑：综合风险分、波动率、动量、宏观不确定性等核心变量")
    
    print("\n当前 100 日趋势图的数据含义：")
    print("  - 数据点：基于日期种子的伪随机数")
    print("  - 趋势：无实际市场含义，仅用于可视化占位")
    print("  - 与真实行情：无映射关系")


def generate_logic_explanation():
    """生成逻辑介绍文本（如果需要证明当前数据的合理性）"""
    print("\n" + "=" * 70)
    print("问题 4：逻辑介绍文本（当前数据的合理性说明）")
    print("=" * 70)
    
    print("""
【重要说明】当前近 100 个交易日下跌概率趋势图的数据为模拟数据，
仅用于 UI 展示占位，不代表真实市场预测。

当前实现逻辑：
1. 数据生成方式：
   - 使用日期作为种子 (dateSeed = YYYYMMDD)
   - T+1 概率 = seededRandom(dateSeed) * 60 + 20
   - T+5 概率 = seededRandom(dateSeed + 1000) * 50 + 30

2. 数据范围控制：
   - T+1 概率范围：20% - 80%
   - T+5 概率范围：30% - 80%
   - 实际波动范围：25% - 75%（正常随机波动）

3. 与真实行情的映射关系：
   当前实现：无直接映射关系（模拟数据）
   目标实现：应接入后端 API，基于 25 因子模型计算历史 100 日的预测值

4. 建议修改方案：
   - 方案 A（推荐）：调用后端 API 获取真实历史预测数据
   - 方案 B（临时）：在文档中明确标注"示意图，非真实预测数据"
    """)


def main():
    """主分析函数"""
    print("\n" + "=" * 70)
    print("下跌风险预测数据分析报告")
    print("=" * 70)
    
    analyze_probability_range()
    analyze_data_mismatch()
    analyze_formula_consistency()
    generate_logic_explanation()
    
    print("\n" + "=" * 70)
    print("总结与建议")
    print("=" * 70)
    print("""
核心问题：
1. 数据源不一致：前端模拟数据 vs 后端真实计算
2. 计算公式不匹配：随机数生成 vs 25 因子 Logit 模型
3. 100 日趋势图无真实市场含义（仅占位）

建议修改：
1. 修改前端：调用后端 API 获取真实历史预测数据
2. 或添加说明：明确标注当前趋势图为"示意图"
3. 统一数据源：两个模块应使用相同的后端 API 接口

优先级：
- 高优先级：统一数据源（解决不一致问题）
- 中优先级：实现真实历史预测数据回溯
- 低优先级：添加说明文档
    """)


if __name__ == "__main__":
    main()
