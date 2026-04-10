# -*- coding: utf-8 -*-
"""最简单的后端启动测试"""
import sys
import os

# 添加路径
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

print("Python 路径:", sys.path)
print("当前目录:", os.getcwd())
print()

try:
    print("正在导入 flask...")
    from flask import Flask
    print("✅ Flask 导入成功")
    
    print("正在导入 flask_cors...")
    from flask_cors import CORS
    print("✅ flask_cors 导入成功")
    
    print("正在导入 analyzer...")
    from analyzer import MicroCapAnalyzer
    print("✅ analyzer 导入成功")
    
    print("正在创建应用...")
    app = Flask(__name__)
    CORS(app)
    print("✅ 应用创建成功")
    
    print("正在初始化分析器...")
    analyzer = MicroCapAnalyzer()
    print("✅ 分析器创建成功")
    
    print("正在获取数据...")
    result = analyzer.fetch_data()
    print(f"数据获取结果：{result}")
    
    print("\n✅ 所有测试通过！")
    print("\n现在启动服务...")
    app.run(host='0.0.0.0', port=5000, debug=False)
    
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
    input("\n按回车键退出...")
