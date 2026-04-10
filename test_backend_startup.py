# -*- coding: utf-8 -*-
"""测试后端服务启动"""
import sys
import os

print("=" * 60)
print("测试后端服务启动")
print("=" * 60)

# 添加 backend 目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
print(f"Python 路径：{sys.path[0]}")

try:
    print("\n导入模块...")
    from analyzer import MicroCapAnalyzer
    from utils.history_risk_service import get_history_risk_service
    print("✅ 模块导入成功")
    
    print("\n初始化分析器...")
    analyzer = MicroCapAnalyzer()
    print("✅ 分析器初始化成功")
    
    print("\n获取数据...")
    if analyzer.fetch_data():
        print(f"✅ 数据获取成功，共 {len(analyzer.df)} 条记录")
    else:
        print("❌ 数据获取失败")
        sys.exit(1)
    
    print("\n初始化历史风险服务...")
    history_risk_service = get_history_risk_service(analyzer)
    print("✅ 历史风险服务初始化成功")
    
    print("\n测试计算 5 天历史风险...")
    result = history_risk_service.calculate_history(5)
    if result['success']:
        print(f"✅ 计算成功，共 {result['metadata']['total_days']} 天")
        print(f"   平均风险：{result['metadata']['avg_risk']:.2f}")
        print(f"   当前风险：{result['metadata']['current_risk']:.2f}")
    else:
        print(f"❌ 计算失败：{result['message']}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("所有测试通过！后端服务可以正常运行。")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
