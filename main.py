"""
主启动脚本 - 根目录唯一入口
"""
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.main import create_app
from backend.core.config import BACKEND_HOST, BACKEND_PORT

if __name__ == '__main__':
    app = create_app()
    print(f"🚀 后端服务启动中...")
    print(f"📍 地址：http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"📝 健康检查：http://{BACKEND_HOST}:{BACKEND_PORT}/api/health")
    app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=True)
