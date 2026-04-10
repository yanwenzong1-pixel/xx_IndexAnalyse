# -*- coding: utf-8 -*-
"""测试 CORS 修复"""
import requests

print("测试 CORS 修复...")
print("=" * 60)

try:
    # 测试健康检查
    response = requests.options('http://localhost:5000/api/health')
    print("OPTIONS 请求状态:", response.status_code)
    print("响应头:", dict(response.headers))
    
    # 测试 GET 请求
    response = requests.get('http://localhost:5000/api/health')
    print("\nGET 请求状态:", response.status_code)
    print("响应头:", dict(response.headers))
    
    # 检查 CORS 头
    cors_headers = [key for key in response.headers.keys() if 'access-control' in key.lower()]
    if cors_headers:
        print(f"\n✅ 发现 CORS 头: {cors_headers}")
        for header in cors_headers:
            print(f"   {header}: {response.headers[header]}")
    else:
        print("\n❌ 未发现 CORS 头")
    
    # 测试风险接口
    response = requests.get('http://localhost:5000/api/risk/current')
    print(f"\n风险接口状态: {response.status_code}")
    print("风险接口 CORS 头:", [key for key in response.headers.keys() if 'access-control' in key.lower()])
    
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到后端服务")
    print("   请确保服务已启动")
except Exception as e:
    print(f"❌ 测试失败：{e}")
