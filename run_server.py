"""
启动后端服务（不使用 reloader）
"""
import sys
import os
import traceback

# 添加 backend 目录
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

print("正在启动后端服务...")
print("=" * 60)

try:
    # 直接导入并运行，不使用 reloader
    from simple_app import app
    
    print("Flask 应用已加载")
    print("启动服务器...")
    print("=" * 60)
    
    # 使用 use_reloader=False 避免多进程问题
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
except Exception as e:
    print(f"❌ 启动失败：{e}")
    traceback.print_exc()
    sys.exit(1)
