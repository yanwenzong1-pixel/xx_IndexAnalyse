# -*- coding: utf-8 -*-
"""测试后端服务是否可访问"""
import requests
import time

print("等待服务启动...")
time.sleep(3)

try:
    # 测试健康检查
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    if response.status_code == 200:
        print("✅ 后端服务启动成功！")
        print(f"   响应：{response.json()}")
    else:
        print(f"❌ 健康检查失败，状态码：{response.status_code}")
    
    # 测试风险历史接口
    response = requests.get('http://localhost:5000/api/risk/history?days=5', timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ 风险历史接口正常！")
            print(f"   数据条数：{len(result['data'])}")
            print(f"   平均风险：{result['metadata']['avg_risk']:.2f}")
        else:
            print(f"❌ 接口返回错误：{result}")
    else:
        print(f"❌ 风险历史接口失败，状态码：{response.status_code}")
    
    # 测试当前风险接口
    response = requests.get('http://localhost:5000/api/risk/current', timeout=10)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ 当前风险接口正常！")
            print(f"   日期：{result['data']['date']}")
            print(f"   风险分：{result['data']['risk_score']}")
            print(f"   等级：{result['data']['risk_level']}")
        else:
            print(f"❌ 接口返回错误：{result}")
    else:
        print(f"❌ 当前风险接口失败，状态码：{response.status_code}")
    
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到后端服务")
    print("   请确保服务已启动")
except Exception as e:
    print(f"❌ 测试失败：{e}")
