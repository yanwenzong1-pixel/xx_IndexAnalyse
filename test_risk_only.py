"""
超简单测试 - 只测试 5 天数据
"""
import sys
import os

# 添加 backend 目录
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)

from analyzer import MicroCapAnalyzer
from utils.history_risk_service import get_history_risk_service

print("初始化数据...")
analyzer = MicroCapAnalyzer()

if not analyzer.fetch_data():
    print("❌ 数据获取失败")
    sys.exit(1)

print(f"✅ 数据获取成功，共 {len(analyzer.df)} 条记录")

print("\n初始化历史风险服务...")
risk_service = get_history_risk_service(analyzer)

print("\n计算最近 5 天的历史风险...")
result = risk_service.calculate_history(5)

if result['success']:
    print(f"✅ 计算成功！")
    print(f"数据条数：{len(result['data'])}")
    print(f"\n最近 5 天的风险打分:")
    for item in result['data']:
        print(f"  {item['date']}: {item['risk_score']} 分 ({item['risk_level']})")
    print(f"\n元数据：{result['metadata']}")
else:
    print(f"❌ 计算失败：{result.get('error')} - {result.get('message')}")
