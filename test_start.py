# -*- coding: utf-8 -*-
"""测试并启动后端服务"""
import subprocess
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')

print("=" * 60)
print("尝试启动后端服务...")
print("=" * 60)

try:
    # 直接运行并捕获输出（start_backend.py 在根目录）
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), 'start_backend.py')],
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\n返回码：{result.returncode}")
    
except subprocess.TimeoutExpired:
    print("⏱️ 启动超时（30 秒）")
except Exception as e:
    print(f"❌ 启动失败：{e}")
    import traceback
    traceback.print_exc()

input("\n按回车键退出...")
