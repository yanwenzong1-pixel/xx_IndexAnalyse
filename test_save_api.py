# -*- coding: utf-8 -*-
"""测试后端保存 API"""
import requests
import json

url = "http://localhost:5000/api/save_index_data"

# 测试数据
test_data = {
    "data": [
        {"date": "2024-01-03", "close": 1458.32, "change_pct": 0.85, "amount": 0.18, "turnover": 3.21},
        {"date": "2024-01-04", "close": 1462.15, "change_pct": 0.26, "amount": 0.19, "turnover": 3.35}
    ],
    "filename": "test_index_data.json"
}

print("正在测试后端保存 API...")
print(f"URL: {url}")
print(f"测试数据：{json.dumps(test_data, indent=2)}")
print("-" * 60)

try:
    response = requests.post(url, json=test_data, timeout=10)
    print(f"响应状态码：{response.status_code}")
    print(f"响应内容：{response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 保存成功！")
            print(f"文件路径：{result.get('file')}")
            print(f"数据条数：{result.get('count')}")
        else:
            print(f"❌ 保存失败：{result.get('message')}")
    else:
        print(f"❌ HTTP 错误：{response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ 连接失败：后端服务未启动")
    print("💡 请运行：cd web/backend && python start_backend.py")
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except Exception as e:
    print(f"❌ 未知错误：{e}")
