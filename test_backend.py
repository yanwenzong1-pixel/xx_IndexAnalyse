# -*- coding: utf-8 -*-
"""测试后端服务是否正常启动"""
import requests
import sys

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端服务正常！")
            print(f"   响应：{data}")
            return True
        else:
            print(f"❌ 服务响应异常：{response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 后端服务未启动或无法连接")
        return False
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False

if __name__ == "__main__":
    success = test_health()
    sys.exit(0 if success else 1)
