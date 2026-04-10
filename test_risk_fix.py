"""
风险打分修复验证脚本
快速验证修复后的风险计算逻辑
"""
import sys
import pandas as pd
import numpy as np

# 添加路径
sys.path.insert(0, 'src')

from backend.service.risk_service import RiskService


def create_test_data(scenario='crash'):
    """创建测试数据"""
    dates = pd.date_range('2024-01-01', periods=30)
    
    if scenario == 'crash':
        # 暴跌场景：最后一日 -5.98%，前几日连续下跌
        changes = [0.5] * 24 + [0.5, -0.3, -1.0, -2.0, -3.0, -5.98]
        closes = []
        close = 1000
        for change in changes:
            close = close * (1 + change / 100)
            closes.append(close)
        amounts = [3e9] * 30
        turnovers = [3.5] * 30
        
    elif scenario == 'continuous_down':
        # 连续下跌场景：连续 5 日下跌
        changes = [0.5] * 25 + [-1.0, -1.5, -2.0, -2.5, -3.0]
        closes = []
        close = 1000
        for change in changes:
            close = close * (1 + change / 100)
            closes.append(close)
        amounts = [2.5e9] * 30
        turnovers = [4.0] * 30
        
    else:  # normal
        # 正常市场
        changes = [0.5] * 30
        closes = []
        close = 1000
        for change in changes:
            close = close * (1 + change / 100)
            closes.append(close)
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


def test_scenario(name, df, expected_min_score):
    """测试场景"""
    print(f"\n{'='*60}")
    print(f"测试场景：{name}")
    print(f"{'='*60}")
    
    # 显示最新数据
    latest = df.iloc[-1]
    print(f"最新收盘价：{latest['close']:.2f}")
    print(f"最新涨跌幅：{latest['change_pct']:.2f}%")
    print(f"5 日累计涨跌：{df['change_pct'].tail(5).sum():.2f}%")
    print(f"换手率：{df['turnover'].tail(5).mean():.2f}%")
    
    # 计算连续下跌天数
    consecutive_down = 0
    for i in range(5):
        if df['change_pct'].iloc[-(i+1)] < 0:
            consecutive_down += 1
        else:
            break
    print(f"连续下跌天数：{consecutive_down}天")
    
    # 计算风险打分
    service = RiskService(df)
    risk_level = service.assess_risk_level()
    risk_text = service.get_risk_level_text(risk_level)
    
    print(f"\n风险打分：{risk_level} 分 ({risk_text})")
    print(f"预期最低分：{expected_min_score}分")
    
    if risk_level >= expected_min_score:
        print(f"✅ 测试通过！风险打分 {risk_level} >= {expected_min_score}")
        return True
    else:
        print(f"❌ 测试失败！风险打分 {risk_level} < {expected_min_score}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("风险打分修复验证测试")
    print("="*60)
    
    results = []
    
    # 测试 1：正常市场
    df_normal = create_test_data('normal')
    results.append(test_scenario('正常市场', df_normal, 3.0))
    
    # 测试 2：暴跌市场（核心测试）
    df_crash = create_test_data('crash')
    results.append(test_scenario('暴跌市场（-5.98%）', df_crash, 8.0))
    
    # 测试 3：连续下跌
    df_continuous = create_test_data('continuous_down')
    results.append(test_scenario('连续下跌', df_continuous, 6.0))
    
    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"通过：{passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！风险打分修复成功！")
        return 0
    else:
        print("❌ 部分测试失败，请检查修复逻辑")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
