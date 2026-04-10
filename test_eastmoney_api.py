# -*- coding: utf-8 -*-
"""测试东方财富 API 连接"""
import requests

url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

params = {
    "secid": "90.BK1158",
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fields1": "f1,f2,f3,f4,f5,f6",
    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
    "klt": "101",
    "fqt": "1",
    "end": "20500101",
    "lmt": "100",
}

print("正在测试东方财富 API 连接...")
print(f"URL: {url}")
print(f"参数：{params}")
print("-" * 60)

try:
    response = requests.get(url, params=params, timeout=30)
    print(f"响应状态码：{response.status_code}")
    print(f"响应内容长度：{len(response.text)}")
    print(f"响应头：{dict(response.headers)}")
    print("-" * 60)
    
    if response.status_code == 200:
        print("✅ 连接成功！")
        # 显示前 500 个字符
        print(f"响应内容预览：{response.text[:500]}")
    else:
        print(f"❌ 连接失败，状态码：{response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except requests.exceptions.ConnectionError as e:
    print(f"❌ 连接错误：{e}")
except Exception as e:
    print(f"❌ 未知错误：{e}")
