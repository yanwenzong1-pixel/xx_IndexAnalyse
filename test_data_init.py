# -*- coding: utf-8 -*-
"""测试数据初始化"""
import sys
import os

# 添加 backend 目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

print("=" * 60)
print("测试数据初始化")
print("=" * 60)

try:
    from analyzer import MicroCapAnalyzer
    
    print("\n初始化分析器...")
    analyzer = MicroCapAnalyzer()
    
    print("获取数据...")
    success = analyzer.fetch_data()
    
    if success:
        print(f"✅ 数据获取成功！")
        print(f"   数据条数：{len(analyzer.df)}")
        print(f"   第一条数据：{analyzer.df.iloc[0]['date']}")
        print(f"   最后一条数据：{analyzer.df.iloc[-1]['date']}")
    else:
        print("❌ 数据获取失败")
        print("   请检查网络连接或数据源")
        
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
