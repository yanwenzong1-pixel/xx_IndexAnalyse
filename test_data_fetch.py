import requests
import json
import pandas as pd
import traceback

# 测试数据获取功能
def test_data_fetch():
    try:
        print("开始测试数据获取...")
        
        base_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "cb": "jQuery35108745723541970376_1772087141861",
            "secid": "90.BK1158",
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "end": "20500101",
            "lmt": "100",  # 只获取100条数据
            "_": "1772703835"
        }
        
        print("正在发送请求...")
        response = requests.get(base_url, params=params, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("数据获取成功！")
            print(f"响应内容长度: {len(response.text)}")
            
            # 处理JSONP响应
            content = response.text
            print(f"响应前100字符: {content[:100]}...")
            
            try:
                json_str = content.split('(', 1)[1].rstrip(')')
                print(f"解析后的JSON前100字符: {json_str[:100]}...")
                data = json.loads(json_str)
                
                print(f"数据结构: {list(data.keys())}")
                if 'data' in data:
                    print(f"data结构: {list(data['data'].keys())}")
                    if 'klines' in data['data']:
                        klines = data['data']['klines']
                        print(f"共获取到 {len(klines)} 条数据")
                        
                        # 解析数据
                        data_list = []
                        for kline in klines[:5]:  # 只显示前5条
                            parts = kline.split(',')
                            print(f"K线数据: {parts}")
                            data_list.append({
                                'date': parts[0],
                                'open': float(parts[1]),
                                'close': float(parts[2]),
                                'high': float(parts[3]),
                                'low': float(parts[4]),
                                'volume': float(parts[5]),
                                'amount': float(parts[6]),
                                'amplitude': float(parts[7]),
                                'change_pct': float(parts[8]),
                                'change': float(parts[9]),
                                'turnover': float(parts[10])
                            })
                        
                        # 转换为DataFrame并显示
                        df = pd.DataFrame(data_list)
                        print("\n前5条数据:")
                        print(df)
                        return True
                    else:
                        print("数据中没有klines字段")
                        return False
                else:
                    print("数据中没有data字段")
                    return False
            except Exception as e:
                print(f"JSON解析错误: {e}")
                print(traceback.format_exc())
                return False
        else:
            print(f"数据获取失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"测试过程中出错: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("测试开始")
    result = test_data_fetch()
    print(f"测试结果: {'成功' if result else '失败'}")
    print("测试结束")
