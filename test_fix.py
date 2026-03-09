# 测试修复后的系统
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from micro_cap_analysis import MicroCapAnalyzer

print("测试微盘股分析系统修复...")

# 测试数据获取
analyzer = MicroCapAnalyzer()
print("测试数据获取功能...")
try:
    result = analyzer.fetch_data()
    print(f"数据获取结果: {'成功' if result else '失败'}")
    if result and analyzer.df is not None:
        print(f"获取到 {len(analyzer.df)} 条数据")
        print(f"最新日期: {analyzer.df['date'].iloc[-1].strftime('%Y-%m-%d')}")
        print(f"最新收盘价: {analyzer.df['close'].iloc[-1]:.2f}")
except Exception as e:
    print(f"数据获取测试失败: {e}")

# 测试风险评估
print("\n测试风险评估功能...")
try:
    if analyzer.df is not None:
        risk_level = analyzer.assess_risk_level()
        print(f"风险等级: {risk_level}/10")
        downside_probability = analyzer.predict_downside_risk()
        print(f"下跌概率: {downside_probability*100:.2f}%")
except Exception as e:
    print(f"风险评估测试失败: {e}")

# 测试报告生成
print("\n测试报告生成功能...")
try:
    if analyzer.df is not None:
        report = analyzer.generate_daily_report()
        print("报告生成成功")
        print("报告前100字符:")
        print(report[:100] + "...")
except Exception as e:
    print(f"报告生成测试失败: {e}")

# 测试预警检查
print("\n测试预警检查功能...")
try:
    if analyzer.df is not None:
        alert, message = analyzer.check_alert_conditions()
        print(f"预警状态: {'有预警' if alert else '无预警'}")
        if alert:
            print(f"预警信息: {message}")
except Exception as e:
    print(f"预警检查测试失败: {e}")

print("\n测试完成")
