"""
测试 API 响应时间
"""
import requests
import time

print("测试后端 API 响应...")
print("=" * 60)

# 测试健康检查
print("\n1. 测试健康检查接口...")
try:
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    print(f"   状态码：{response.status_code}")
    print(f"   响应：{response.json()}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 测试风险历史 API（60 天）
print("\n2. 测试风险历史接口（60 天）...")
start_time = time.time()
try:
    response = requests.get('http://localhost:5000/api/risk/history?days=60', timeout=60)
    elapsed = time.time() - start_time
    print(f"   状态码：{response.status_code}")
    print(f"   耗时：{elapsed:.2f}秒")
    
    result = response.json()
    if result.get('success'):
        print(f"   ✅ 成功！数据条数：{len(result.get('data', []))}")
        print(f"   元数据：{result.get('metadata', {})}")
    else:
        print(f"   ❌ API 返回错误：{result}")
except requests.Timeout:
    print(f"   ❌ 超时（超过 60 秒）")
except Exception as e:
    print(f"   ❌ 失败：{e}")

print("\n" + "=" * 60)
