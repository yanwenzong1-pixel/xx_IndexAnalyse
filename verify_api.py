# -*- coding: utf-8 -*-
"""快速验证风险趋势 API"""
import requests
import json

print("=" * 60)
print("风险趋势 API 快速验证")
print("=" * 60)

try:
    # 测试当前风险接口
    print("\n[1/2] 测试 /api/risk/current...")
    response = requests.get('http://localhost:5000/api/risk/current', timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"✅ 当前风险接口正常")
            print(f"   日期：{result['data']['date']}")
            print(f"   风险分：{result['data']['risk_score']}")
            print(f"   等级：{result['data']['risk_level']}")
        else:
            print(f"❌ 接口返回错误：{result}")
    else:
        print(f"❌ 请求失败，状态码：{response.status_code}")
    
    # 测试历史风险接口
    print("\n[2/2] 测试 /api/risk/history?days=5...")
    response = requests.get('http://localhost:5000/api/risk/history?days=5', timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"✅ 历史风险接口正常")
            print(f"   数据条数：{len(result['data'])}")
            print(f"   平均风险：{result['metadata']['avg_risk']:.2f}")
            print(f"   最新风险：{result['metadata']['current_risk']:.2f}")
            print(f"   风险趋势：{result['metadata']['risk_trend']}")
            
            # 显示前 3 条数据
            print(f"\n   数据预览（前 3 条）:")
            for item in result['data'][:3]:
                print(f"     {item['date']} - {item['risk_score']:.2f} ({item['risk_level']})")
        else:
            print(f"❌ 接口返回错误：{result}")
    else:
        print(f"❌ 请求失败，状态码：{response.status_code}")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)
    
except requests.exceptions.ConnectionError:
    print("\n❌ 无法连接到后端服务，请确保 simple_app.py 已启动")
except Exception as e:
    print(f"\n❌ 测试过程中出现错误：{e}")
