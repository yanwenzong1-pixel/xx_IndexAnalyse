# -*- coding: utf-8 -*-
"""一键启动微盘股指数分析系统"""
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

def print_banner(text):
    """打印横幅"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def main():
    """主函数"""
    print_banner("微盘股指数分析系统 - 一键启动")
    
    # 检查 Python
    print("✅ 检查 Python 环境...")
    try:
        python_version = sys.version
        print(f"   Python 版本：{python_version.split()[0]}")
    except Exception as e:
        print(f"❌ Python 检查失败：{e}")
        input("按回车键退出...")
        return
    
    # 启动后端服务
    if check_port(5000):
        print("\n✅ 后端服务已在运行 (端口 5000)")
    else:
        print("\n[1/3] 启动后端服务...")
        backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
        try:
            subprocess.Popen(
                [sys.executable, 'start_backend.py'],
                cwd=backend_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            print("   ✅ 后端服务启动成功")
        except Exception as e:
            print(f"   ❌ 后端服务启动失败：{e}")
    
    # 启动前端服务
    if check_port(5500):
        print("\n✅ 前端服务已在运行 (端口 5500)")
    else:
        print("\n[2/3] 启动前端服务...")
        frontend_path = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
        try:
            subprocess.Popen(
                [sys.executable, '-m', 'http.server', '5500'],
                cwd=frontend_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            print("   ✅ 前端服务启动成功")
        except Exception as e:
            print(f"   ❌ 前端服务启动失败：{e}")
    
    # 等待服务启动
    print("\n[3/3] 等待服务启动...")
    for i in range(10):
        if check_port(5000) and check_port(5500):
            print("   ✅ 所有服务已就绪")
            break
        time.sleep(1)
    else:
        print("   ⚠️ 服务可能未完全启动")
    
    # 打开浏览器
    print("\n🌐 打开浏览器...")
    url = "http://localhost:5500/index.html"
    webbrowser.open(url)
    print(f"   ✅ 访问地址：{url}")
    
    # 完成
    print_banner("系统启动完成！")
    print("后端服务：http://localhost:5000")
    print("前端服务：http://localhost:5500")
    print("访问地址：http://localhost:5500/index.html")
    print("\n按 Ctrl+C 或关闭窗口停止服务")
    print("=" * 60 + "\n")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        print("服务已停止\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
