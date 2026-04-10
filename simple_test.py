"""
简单测试后端 API
"""
import urllib.request
import json
import socket

print("测试后端 API 连接...")

# 测试连接是否可达
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("✅ 端口 5000 可连接")
    else:
        print("❌ 端口 5000 无法连接")
except Exception as e:
    print(f"❌ 连接测试失败：{e}")

# 测试健康检查接口
try:
    print("\n测试健康检查接口...")
    req = urllib.request.Request('http://localhost:5000/api/health')
    req.add_header('User-Agent', 'Mozilla/5.0')
    response = urllib.request.urlopen(req, timeout=10)
    data = response.read().decode('utf-8')
    result = json.loads(data)
    print(f"✅ 健康检查成功：{result}")
except Exception as e:
    print(f"❌ 健康检查失败：{e}")

# 测试风险历史接口
try:
    print("\n测试风险历史接口...")
    req = urllib.request.Request('http://localhost:5000/api/risk/history?days=5')
    req.add_header('User-Agent', 'Mozilla/5.0')
    response = urllib.request.urlopen(req, timeout=30)
    data = response.read().decode('utf-8')
    result = json.loads(data)
    print(f"✅ 风险历史接口响应：{result.get('success', 'Unknown')}")
    if result.get('success'):
        print(f"   数据条数：{len(result.get('data', []))}")
except Exception as e:
    print(f"❌ 风险历史接口失败：{e}")