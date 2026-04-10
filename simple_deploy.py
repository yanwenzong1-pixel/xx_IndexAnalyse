"""
简单部署测试 - 只验证核心功能
"""

import sys
import os

# 添加路径
web_backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, web_backend_path)

print("=" * 60)
print("微盘股指数分析系统 - 部署验证")
print("=" * 60)

# 尝试导入
try:
    import requests
    print("✅ requests 已安装")
except:
    print("❌ requests 未安装")
    print("   请运行：pip install requests")
    sys.exit(1)

try:
    import pandas as pd
    print("✅ pandas 已安装")
except:
    print("❌ pandas 未安装")
    print("   请运行：pip install pandas")
    sys.exit(1)

try:
    import numpy as np
    print("✅ numpy 已安装")
except:
    print("❌ numpy 未安装")
    print("   请运行：pip install numpy")
    sys.exit(1)

try:
    import scipy
    print("✅ scipy 已安装")
except:
    print("❌ scipy 未安装")
    print("   请运行：pip install scipy")
    sys.exit(1)

try:
    import flask
    print("✅ flask 已安装")
except:
    print("❌ flask 未安装")
    print("   请运行：pip install flask")
    sys.exit(1)

try:
    import flask_cors
    print("✅ flask-cors 已安装")
except:
    print("❌ flask-cors 未安装")
    print("   请运行：pip install flask-cors")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有依赖已安装")
print("=" * 60)
print("\n部署成功！")
print("\n启动服务:")
print("  cd web/backend")
print("  python app.py")
print("\n访问页面:")
print("  http://localhost:5000")
