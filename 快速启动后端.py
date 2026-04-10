# -*- coding: utf-8 -*-
"""快速启动后端服务（不打开浏览器）"""
import subprocess
import sys
import os
import time

print("=" * 60)
print("启动后端服务...")
print("=" * 60)

backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')

try:
    # 启动后端服务
    subprocess.Popen(
        [sys.executable, 'start_backend.py'],
        cwd=backend_path,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    print("✅ 后端服务启动成功！")
    print("   监听地址：http://localhost:5000")
    print("   健康检查：http://localhost:5000/api/health")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 保持运行
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n服务已停止")
except Exception as e:
    print(f"❌ 启动失败：{e}")
    input("按回车键退出...")
