# -*- coding: utf-8 -*-
"""启动后端服务"""
from simple_app import app

if __name__ == '__main__':
    print("=" * 60)
    print("  微盘股指数分析系统 - 后端服务")
    print("=" * 60)
    print("\n正在启动 Flask 服务器...")
    print("访问地址：http://localhost:5000")
    print("健康检查：http://localhost:5000/api/health")
    print("\n按 Ctrl+C 停止服务\n")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
