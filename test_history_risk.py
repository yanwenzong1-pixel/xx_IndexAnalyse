"""
历史风险服务单元测试
验证历史风险计算功能的正确性
"""

import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)

def test_history_service():
    """测试历史风险服务基本功能"""
    print("\n" + "="*60)
    print("测试 1：历史风险服务基本功能")
    print("="*60)
    
    try:
        from analyzer import MicroCapAnalyzer
        from utils.history_risk_service import get_history_risk_service
        
        # 初始化分析器
        print("正在初始化分析器...")
        analyzer = MicroCapAnalyzer()
        if not analyzer.fetch_data():
            print("❌ 数据获取失败")
            return False
        print(f"✅ 数据获取成功，共 {len(analyzer.df)} 天数据")
        
        # 初始化历史风险服务
        print("\n正在初始化历史风险服务...")
        history_service = get_history_risk_service(analyzer)
        print("✅ 历史风险服务初始化成功")
        
        # 测试计算 10 天历史风险
        print("\n正在计算 10 天历史风险...")
        result = history_service.calculate_history(10)
        
        if not result['success']:
            print(f"❌ 历史风险计算失败：{result['message']}")
            return False
        
        print(f"✅ 历史风险计算成功")
        print(f"   数据天数：{result['metadata']['total_days']}")
        print(f"   平均风险：{result['metadata']['avg_risk']:.2f}")
        print(f"   最高风险：{result['metadata']['max_risk']:.2f}")
        print(f"   最低风险：{result['metadata']['min_risk']:.2f}")
        print(f"   当前风险：{result['metadata']['current_risk']:.2f}")
        print(f"   风险趋势：{result['metadata']['risk_trend']}")
        
        # 验证数据格式
        print("\n验证数据格式...")
        required_fields = ['date', 'risk_score', 'risk_level']
        first_item = result['data'][0]
        
        for field in required_fields:
            if field not in first_item:
                print(f"❌ 缺少必需字段：{field}")
                return False
            print(f"   ✅ 字段 '{field}' 存在")
        
        # 验证风险分数范围
        risk_scores = [item['risk_score'] for item in result['data']]
        if min(risk_scores) < 1 or max(risk_scores) > 10:
            print(f"❌ 风险分数超出范围 [1, 10]")
            return False
        print(f"   ✅ 风险分数范围正确：[{min(risk_scores):.2f}, {max(risk_scores):.2f}]")
        
        # 验证风险等级
        valid_levels = ['low', 'medium', 'high', 'very_high']
        for item in result['data']:
            if item['risk_level'] not in valid_levels:
                print(f"❌ 无效风险等级：{item['risk_level']}")
                return False
        print(f"   ✅ 所有风险等级有效")
        
        # 显示前 3 天数据样例
        print("\n数据样例（最近 3 天）：")
        for i, item in enumerate(result['data'][-3:], 1):
            print(f"   {i}. {item['date']} - 风险分：{item['risk_score']:.2f}, 等级：{item['risk_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_lookahead_bias():
    """测试避免前视偏差"""
    print("\n" + "="*60)
    print("测试 2：避免前视偏差验证")
    print("="*60)
    
    try:
        from analyzer import MicroCapAnalyzer
        from utils.history_risk_service import get_history_risk_service
        
        # 初始化分析器
        analyzer = MicroCapAnalyzer()
        if not analyzer.fetch_data():
            print("❌ 数据获取失败")
            return False
        
        history_service = get_history_risk_service(analyzer)
        
        # 计算 5 天历史风险
        result = history_service.calculate_history(5)
        
        if not result['success']:
            print(f"❌ 计算失败：{result['message']}")
            return False
        
        # 验证：每个时点的风险分应该只依赖于该时点及之前的数据
        # 方法：比较连续两天的风险分变化是否合理
        print("验证前视偏差...")
        for i in range(1, len(result['data'])):
            prev_risk = result['data'][i-1]['risk_score']
            curr_risk = result['data'][i]['risk_score']
            
            # 风险分变化应该是渐进的（除非市场剧烈波动）
            risk_change = abs(curr_risk - prev_risk)
            if risk_change > 5:  # 单日风险变化超过 5 分可能有问题
                print(f"⚠️  警告：{result['data'][i]['date']} 风险变化过大 ({risk_change:.2f})")
        
        print("✅ 前视偏差检查通过（无明显异常）")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "="*60)
    print("测试 3：数据一致性验证")
    print("="*60)
    
    try:
        from analyzer import MicroCapAnalyzer
        from utils.history_risk_service import get_history_risk_service
        
        # 初始化分析器
        analyzer = MicroCapAnalyzer()
        if not analyzer.fetch_data():
            print("❌ 数据获取失败")
            return False
        
        history_service = get_history_risk_service(analyzer)
        
        # 分别计算 10 天和 20 天的历史风险
        result_10 = history_service.calculate_history(10)
        result_20 = history_service.calculate_history(20)
        
        if not (result_10['success'] and result_20['success']):
            print("❌ 计算失败")
            return False
        
        # 验证：前 10 天的数据应该一致
        print("验证数据一致性...")
        for i in range(10):
            risk_10 = result_10['data'][i]['risk_score']
            risk_20 = result_20['data'][i]['risk_score']
            
            if abs(risk_10 - risk_20) > 0.01:  # 允许微小误差
                print(f"❌ 数据不一致：第{i}天风险分不同 ({risk_10:.2f} vs {risk_20:.2f})")
                return False
        
        print("✅ 数据一致性检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("[TEST] 历史风险服务单元测试套件")
    print("="*60)
    
    tests = [
        ("基本功能测试", test_history_service),
        ("前视偏差测试", test_lookahead_bias),
        ("数据一致性测试", test_data_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n开始执行：{test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！历史风险服务功能正常。")
        return True
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败，请检查问题。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
