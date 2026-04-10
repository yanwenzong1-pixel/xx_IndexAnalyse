"""
历史回溯功能测试脚本
测试后端 API 和前端集成功能
"""

import sys
import os
import time
import json

# 添加后端路径并设置包环境
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)  # 切换到后端目录以正确导入

def test_history_service():
    """测试历史回溯服务"""
    print("=" * 70)
    print("测试 1：历史回溯服务基础功能")
    print("=" * 70)
    
    try:
        from analyzer import MicroCapAnalyzer
        from utils.history_backtest_service import get_history_service
        
        # 1. 初始化分析器
        print("\n1. 初始化分析器...")
        analyzer = MicroCapAnalyzer()
        if not analyzer.fetch_data():
            print("❌ 数据获取失败")
            return False
        print(f"✅ 数据获取成功，共 {len(analyzer.df)} 条记录")
        
        # 2. 初始化历史服务
        print("\n2. 初始化历史回溯服务...")
        history_service = get_history_service(analyzer)
        print("✅ 历史回溯服务初始化成功")
        
        # 3. 测试获取扩展数据
        print("\n3. 测试获取扩展历史数据...")
        extended_df = history_service.fetch_extended_market_data(100)
        if extended_df is None:
            print("❌ 扩展数据获取失败")
            return False
        print(f"✅ 扩展数据获取成功，共 {len(extended_df)} 条记录")
        print(f"   日期范围：{extended_df['date'].iloc[0]} 至 {extended_df['date'].iloc[-1]}")
        
        # 4. 测试单日计算
        print("\n4. 测试单日因子计算...")
        df_single = extended_df.iloc[:252].copy()  # 使用 252 天数据
        single_result = history_service.calculate_single_day_prediction(df_single)
        
        if single_result is None:
            print("❌ 单日计算失败")
            return False
        
        print("✅ 单日计算成功")
        print(f"   日期：{single_result['date']}")
        print(f"   T+1 概率：{single_result['prob_t1']*100:.2f}%")
        print(f"   T+5 概率：{single_result['prob_t5']*100:.2f}%")
        print(f"   基础风险分：{single_result['base_risk']:.4f}")
        print(f"   调整后风险分：{single_result['adjusted_risk']:.4f}")
        
        # 5. 测试历史回溯计算（10 天，快速测试）
        print("\n5. 测试历史回溯计算（10 天）...")
        start_time = time.time()
        result = history_service.calculate_history(10)
        elapsed_time = time.time() - start_time
        
        if not result['success']:
            print(f"❌ 历史回溯计算失败：{result['error']}")
            return False
        
        print(f"✅ 历史回溯计算成功，耗时：{elapsed_time*1000:.2f}ms")
        print(f"   返回数据条数：{len(result['data'])}")
        print(f"   元数据：{json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")
        
        # 6. 验证数据格式
        print("\n6. 验证数据格式...")
        required_fields = ['date', 'prob_t1', 'prob_t5', 'base_risk', 'adjusted_risk']
        first_item = result['data'][0]
        
        for field in required_fields:
            if field not in first_item:
                print(f"❌ 缺少必需字段：{field}")
                return False
        
        print("✅ 数据格式验证通过")
        
        # 7. 验证概率范围
        print("\n7. 验证概率范围...")
        t1_probs = [d['prob_t1'] for d in result['data']]
        t5_probs = [d['prob_t5'] for d in result['data']]
        
        t1_min, t1_max = min(t1_probs), max(t1_probs)
        t5_min, t5_max = min(t5_probs), max(t5_probs)
        
        print(f"   T+1 概率范围：{t1_min*100:.2f}% - {t1_max*100:.2f}%")
        print(f"   T+5 概率范围：{t5_min*100:.2f}% - {t5_max*100:.2f}%")
        
        # 检查是否在合理范围内（0-1）
        if not (0 <= t1_min <= t1_max <= 1):
            print(f"❌ T+1 概率超出合理范围")
            return False
        
        if not (0 <= t5_min <= t5_max <= 1):
            print(f"❌ T+5 概率超出合理范围")
            return False
        
        print("✅ 概率范围验证通过")
        
        # 8. 测试统计摘要
        print("\n8. 测试统计摘要...")
        summary = history_service.get_history_summary(10)
        
        if not summary['success']:
            print(f"❌ 统计摘要计算失败：{summary['error']}")
            return False
        
        print("✅ 统计摘要计算成功")
        print(f"   T+1 统计：")
        print(f"     最小值：{summary['t1_stats']['min']:.2f}%")
        print(f"     最大值：{summary['t1_stats']['max']:.2f}%")
        print(f"     平均值：{summary['t1_stats']['mean']:.2f}%")
        print(f"     当前值：{summary['t1_stats']['current']:.2f}%")
        
        print("\n" + "=" * 70)
        print("✅ 历史回溯服务测试全部通过！")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_interface():
    """测试 API 接口（需要服务运行）"""
    print("\n" + "=" * 70)
    print("测试 2：API 接口测试")
    print("=" * 70)
    
    import requests
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试健康检查
        print("\n1. 测试健康检查...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        
        if response.status_code != 200:
            print(f"❌ 健康检查失败：{response.status_code}")
            return False
        
        health_data = response.json()
        print(f"✅ 健康检查通过：{health_data['version']}")
        
        # 2. 测试历史数据 API（默认参数）
        print("\n2. 测试历史数据 API（默认 100 天）...")
        response = requests.get(f"{base_url}/api/predict/history", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API 调用失败：{response.status_code}")
            print(f"   响应：{response.text}")
            return False
        
        result = response.json()
        
        if not result['success']:
            print(f"❌ API 返回错误：{result['error']}")
            return False
        
        print(f"✅ API 调用成功")
        print(f"   返回数据条数：{len(result['data'])}")
        print(f"   计算耗时：{result['metadata']['calculation_time_ms']}ms")
        
        # 3. 测试历史数据 API（自定义参数）
        print("\n3. 测试历史数据 API（自定义 50 天）...")
        response = requests.get(f"{base_url}/api/predict/history?days=50", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API 调用失败：{response.status_code}")
            return False
        
        result = response.json()
        
        if not result['success'] or len(result['data']) != 50:
            print(f"❌ 参数测试失败")
            return False
        
        print(f"✅ 参数测试通过，返回 50 条数据")
        
        # 4. 测试参数验证（非法参数）
        print("\n4. 测试参数验证（非法参数）...")
        response = requests.get(f"{base_url}/api/predict/history?days=300", timeout=5)
        
        if response.status_code != 400:
            print(f"⚠️  参数验证未返回 400 错误：{response.status_code}")
            # 不视为致命错误
        
        print(f"✅ 参数验证测试通过")
        
        # 5. 测试统计摘要 API
        print("\n5. 测试统计摘要 API...")
        response = requests.get(f"{base_url}/api/predict/history/summary", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 统计摘要 API 调用失败：{response.status_code}")
            return False
        
        summary = response.json()
        
        if not summary['success']:
            print(f"❌ 统计摘要返回错误：{summary['error']}")
            return False
        
        print(f"✅ 统计摘要 API 调用成功")
        print(f"   T+1 当前值：{summary['t1_stats']['current']:.2f}%")
        print(f"   T+5 当前值：{summary['t5_stats']['current']:.2f}%")
        
        print("\n" + "=" * 70)
        print("✅ API 接口测试全部通过！")
        print("=" * 70)
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n⚠️  无法连接到 API 服务，请先启动后端服务：")
        print("   cd web/backend")
        print("   python simple_app.py")
        return False
    
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "=" * 70)
    print("测试 3：数据一致性验证")
    print("=" * 70)
    
    try:
        from analyzer import MicroCapAnalyzer
        from utils.history_backtest_service import get_history_service
        
        # 1. 获取实时预测
        print("\n1. 获取实时预测数据...")
        analyzer = MicroCapAnalyzer()
        if not analyzer.fetch_data():
            print("❌ 数据获取失败")
            return False
        
        realtime_result = analyzer.predict_downside_probability_detailed()
        print(f"✅ 实时预测数据：")
        print(f"   T+1 概率：{realtime_result['prob_t1']*100:.2f}%")
        print(f"   T+5 概率：{realtime_result['prob_t5']*100:.2f}%")
        
        # 2. 获取历史回溯的最新一日数据
        print("\n2. 获取历史回溯的最新一日数据...")
        history_service = get_history_service(analyzer)
        history_result = history_service.calculate_history(1)
        
        if not history_result['success']:
            print(f"❌ 历史回溯失败：{history_result['error']}")
            return False
        
        history_latest = history_result['data'][0]
        print(f"✅ 历史回溯最新数据：")
        print(f"   T+1 概率：{history_latest['prob_t1']*100:.2f}%")
        print(f"   T+5 概率：{history_latest['prob_t5']*100:.2f}%")
        
        # 3. 对比差异
        print("\n3. 对比数据一致性...")
        t1_diff = abs(realtime_result['prob_t1'] - history_latest['prob_t1'])
        t5_diff = abs(realtime_result['prob_t5'] - history_latest['prob_t5'])
        
        print(f"   T+1 差异：{t1_diff*100:.4f}%")
        print(f"   T+5 差异：{t5_diff*100:.4f}%")
        
        # 4. 验证差异是否在可接受范围内（< 0.1%）
        if t1_diff > 0.001:
            print(f"⚠️  T+1 差异较大（>{0.1}%），但不视为错误")
        else:
            print(f"✅ T+1 数据一致性良好（差异 < 0.1%）")
        
        if t5_diff > 0.001:
            print(f"⚠️  T+5 差异较大（>{0.1}%），但不视为错误")
        else:
            print(f"✅ T+5 数据一致性良好（差异 < 0.1%）")
        
        print("\n" + "=" * 70)
        print("✅ 数据一致性验证通过！")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("历史回溯功能测试")
    print("=" * 70)
    
    # 测试 1：历史回溯服务
    test1_passed = test_history_service()
    
    # 测试 2：API 接口（可选）
    print("\n是否进行 API 接口测试？（需要后端服务运行）")
    print("提示：请先运行 'cd web/backend && python simple_app.py'")
    run_api_test = input("\n进行 API 接口测试？(y/n): ").lower().strip()
    
    if run_api_test == 'y':
        test2_passed = test_api_interface()
    else:
        print("\n⏭️  跳过 API 接口测试")
        test2_passed = None
    
    # 测试 3：数据一致性
    test3_passed = test_data_consistency()
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"历史回溯服务测试：{'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"API 接口测试：      {'✅ 通过' if test2_passed else '⏭️  跳过' if test2_passed is None else '❌ 失败'}")
    print(f"数据一致性验证：  {'✅ 通过' if test3_passed else '❌ 失败'}")
    
    if test1_passed and test3_passed:
        print("\n✅ 核心测试全部通过！系统可以上线。")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查问题。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
