"""
使用 Waitress WSGI 服务器启动后端服务
Waitress 是生产级服务器，不会有 Flask 开发服务器的死锁问题
"""
import sys
import os

# 添加 backend 目录
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

print("正在启动 Waitress 服务器...")
print("=" * 60)

try:
    from waitress import serve
    from simple_app import app
    
    print("✅ Flask 应用已加载")
    print("📡 监听地址：http://0.0.0.0:5000")
    print("🚀 启动服务器...")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务\n")
    
    # 使用 waitress 生产级服务器
    serve(app, host='0.0.0.0', port=5000, threads=4)
    
except KeyboardInterrupt:
    print("\n👋 服务器已停止")
except Exception as e:
    print(f"\n❌ 服务器错误：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
