# -*- coding: utf-8 -*-
"""测试后端启动"""
import subprocess
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')

print("启动后端服务...")
print("=" * 60)

# 运行并实时显示输出
process = subprocess.Popen(
    [sys.executable, 'app.py'],
    cwd=backend_path,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'
)

try:
    for line in process.stdout:
        print(line, end='')
except KeyboardInterrupt:
    process.kill()
    print("\n服务已停止")
