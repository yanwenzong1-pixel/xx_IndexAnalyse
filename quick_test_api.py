# -*- coding: utf-8 -*-
"""快速测试后端服务"""
import requests
import time

print("等待 5 秒让服务启动...")
time.sleep(5)

print("\n测试后端服务...")
print("=" * 60)

try:
    # 测试健康检查
    print("\n1. 测试健康检查接口...")
    response = requests.get('http://localhost:5000/api/health', timeout=10)
    if response.status_code == 200:
        print(f"   ✅ 成功！响应：{response.json()}")
    else:
        print(f"   ❌ 失败，状态码：{response.status_code}")
    
    # 测试当前风险
    print("\n2. 测试当前风险接口...")
    response = requests.get('http://localhost:5000/api/risk/current', timeout=10)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"   ✅ 成功！")
            print(f"      日期：{result['data']['date']}")
            print(f"      风险分：{result['data']['risk_score']}")
            print(f"      等级：{result['data']['risk_level']}")
        else:
            print(f"   ❌ 失败：{result}")
    else:
        print(f"   ❌ 失败，状态码：{response.status_code}")
    
    # 测试历史风险
    print("\n3. 测试历史风险接口（5 天）...")
    response = requests.get('http://localhost:5000/api/risk/history?days=5', timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"   ✅ 成功！")
            print(f"      数据条数：{len(result['data'])}")
            print(f"      平均风险：{result['metadata']['avg_risk']:.2f}")
            print(f"      当前风险：{result['metadata']['current_risk']:.2f}")
        else:
            print(f"   ❌ 失败：{result}")
    else:
        print(f"   ❌ 失败，状态码：{response.status_code}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
except requests.exceptions.ConnectionError:
    print("\n❌ 无法连接到后端服务")
    print("   服务可能还未启动，请稍后再试")
except Exception as e:
    print(f"\n❌ 测试失败：{e}")
