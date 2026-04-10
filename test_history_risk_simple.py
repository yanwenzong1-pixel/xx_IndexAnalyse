# -*- coding: utf-8 -*-
"""简化测试脚本"""
import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)

from analyzer import MicroCapAnalyzer
from utils.history_risk_service import get_history_risk_service

print("=" * 60)
print("历史风险服务快速测试")
print("=" * 60)

# 初始化分析器
print("\n[1/3] 初始化分析器...")
analyzer = MicroCapAnalyzer()
if not analyzer.fetch_data():
    print("数据获取失败")
    sys.exit(1)
print(f"数据获取成功，共 {len(analyzer.df)} 天数据")

# 初始化历史风险服务
print("\n[2/3] 初始化历史风险服务...")
history_service = get_history_risk_service(analyzer)
print("服务初始化成功")

# 计算 10 天历史风险
print("\n[3/3] 计算 10 天历史风险...")
result = history_service.calculate_history(10)

if result['success']:
    print("\n计算成功!")
    print(f"  数据天数：{result['metadata']['total_days']}")
    print(f"  平均风险：{result['metadata']['avg_risk']:.2f}")
    print(f"  最高风险：{result['metadata']['max_risk']:.2f}")
    print(f"  最低风险：{result['metadata']['min_risk']:.2f}")
    print(f"  当前风险：{result['metadata']['current_risk']:.2f}")
    print(f"  风险趋势：{result['metadata']['risk_trend']}")
    
    print("\n最近 3 天数据:")
    for i, item in enumerate(result['data'][-3:], 1):
        print(f"  {i}. {item['date']} - 风险分：{item['risk_score']:.2f}, 等级：{item['risk_level']}")
    
    print("\n[SUCCESS] 测试通过!")
else:
    print(f"\n[FAILED] 计算失败：{result['message']}")
    sys.exit(1)
