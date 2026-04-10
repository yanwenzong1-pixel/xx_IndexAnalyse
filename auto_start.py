# -*- coding: utf-8 -*-
"""自动启动后端服务和前端服务器"""
import subprocess
import sys
import os
import time
import webbrowser
import socket

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_backend():
    """启动后端服务"""
    print("=" * 60)
    print("启动后端服务...")
    print("=" * 60)
    
    backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
    
    try:
        # 在新窗口启动后端服务
        subprocess.Popen(
            [sys.executable, 'start_backend.py'],
            cwd=backend_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print("✅ 后端服务已启动 (端口 5000)")
        return True
    except Exception as e:
        print(f"❌ 后端服务启动失败：{e}")
        return False

def start_frontend():
    """启动前端服务器"""
    print("=" * 60)
    print("启动前端服务器...")
    print("=" * 60)
    
    try:
        # 使用 Python 内置的 HTTP 服务器
        frontend_path = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
        
        # 在新窗口启动前端服务
        subprocess.Popen(
            [sys.executable, '-m', 'http.server', '5500'],
            cwd=frontend_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print("✅ 前端服务已启动 (端口 5500)")
        return True
    except Exception as e:
        print(f"❌ 前端服务启动失败：{e}")
        return False

def open_browser():
    """打开浏览器"""
    print("=" * 60)
    print("打开浏览器...")
    print("=" * 60)
    
    # 等待后端服务启动
    print("等待后端服务启动...")
    for i in range(10):
        if check_port(5000):
            print("✅ 检测到后端服务运行")
            break
        time.sleep(1)
    else:
        print("⚠️ 后端服务可能未正常启动，但仍将打开页面")
    
    # 打开浏览器
    url = "http://localhost:5500/web/frontend/index.html"
    webbrowser.open(url)
    print(f"✅ 已打开浏览器：{url}")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("微盘股指数分析系统 - 自动启动")
    print("=" * 60)
    print()
    
    # 检查端口
    if check_port(5000):
        print("✅ 后端服务已在运行 (端口 5000)")
    else:
        start_backend()
    
    if check_port(5500):
        print("✅ 前端服务已在运行 (端口 5500)")
    else:
        start_frontend()
    
    print()
    print("=" * 60)
    print("服务启动中...")
    print("=" * 60)
    print()
    
    # 等待服务启动
    time.sleep(3)
    
    # 打开浏览器
    open_browser()
    
    print()
    print("=" * 60)
    print("系统启动完成！")
    print("- 后端服务：http://localhost:5000")
    print("- 前端服务：http://localhost:5500")
    print("- 访问地址：http://localhost:5500/web/frontend/index.html")
    print("=" * 60)
    print()
    print("按 Ctrl+C 停止所有服务")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        print("服务已停止")

if __name__ == "__main__":
    main()
