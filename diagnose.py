# -*- coding: utf-8 -*-
"""
风险趋势功能诊断工具
用于快速诊断常见问题
"""

import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_backend_files():
    """检查后端文件是否存在"""
    print_header("步骤 1: 检查后端文件")
    
    files_to_check = [
        "web/backend/simple_app.py",
        "web/backend/utils/history_risk_service.py",
        "web/backend/analyzer.py",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print_success(f"{file_path} 存在")
        else:
            print_error(f"{file_path} 不存在")
            all_exist = False
    
    return all_exist

def check_frontend_files():
    """检查前端文件是否存在"""
    print_header("步骤 2: 检查前端文件")
    
    files_to_check = [
        "web/frontend/index.html",
        "web/frontend/components/RiskTrendChart.js",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print_success(f"{file_path} 存在")
        else:
            print_error(f"{file_path} 不存在")
            all_exist = False
    
    return all_exist

def check_backend_service():
    """检查后端服务是否可导入"""
    print_header("步骤 3: 检查后端服务")
    
    try:
        backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
        sys.path.insert(0, backend_path)
        
        from utils.history_risk_service import HistoryRiskService
        print_success("历史风险服务可导入")
        
        # 检查核心方法
        if hasattr(HistoryRiskService, 'calculate_history'):
            print_success("calculate_history 方法存在")
        else:
            print_error("calculate_history 方法不存在")
            return False
        
        return True
        
    except ImportError as e:
        print_error(f"导入失败：{e}")
        return False
    except Exception as e:
        print_error(f"检查过程中出错：{e}")
        return False

def check_api_connection():
    """检查 API 连接"""
    print_header("步骤 4: 检查 API 连接")
    
    try:
        import requests
        
        # 测试健康检查接口
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print_success("后端服务可连接")
            
            # 测试风险接口
            response = requests.get('http://localhost:5000/api/risk/current', timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print_success("风险 API 正常工作")
                    return True
                else:
                    print_error(f"风险 API 返回错误：{result}")
                    return False
            else:
                print_error(f"风险 API 请求失败，状态码：{response.status_code}")
                return False
        else:
            print_error(f"健康检查失败，状态码：{response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("无法连接到后端服务，请先启动 simple_app.py")
        print_info("启动命令：python web/backend/simple_app.py")
        return False
    except Exception as e:
        print_error(f"检查过程中出错：{e}")
        return False

def provide_solution(issues):
    """根据问题提供解决方案"""
    print_header("诊断结果与建议")
    
    if not issues:
        print_success("所有检查通过！系统运行正常。")
        print_info("\n使用方法:")
        print("  1. 确保后端服务已启动：python web/backend/simple_app.py")
        print("  2. 在浏览器中访问：http://localhost:3000")
        print("  3. 点击'风险趋势'标签查看图表")
        return
    
    print_warning("发现以下问题:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print("\n建议解决方案:")
    
    if any("文件不存在" in issue for issue in issues):
        print("  - 文件缺失：请确认所有文件已正确创建")
    
    if any("导入失败" in issue for issue in issues):
        print("  - 导入错误：检查 Python 环境和依赖")
    
    if any("无法连接" in issue for issue in issues):
        print("  - 连接失败：启动后端服务")
        print("    命令：python web/backend/simple_app.py")
    
    if any("API 返回错误" in issue for issue in issues):
        print("  - API 错误：查看后端服务日志")

def main():
    """主诊断流程"""
    print_header("风险趋势功能诊断工具")
    print("正在检查系统状态...\n")
    
    issues = []
    
    # 执行检查
    if not check_backend_files():
        issues.append("后端文件缺失")
    
    if not check_frontend_files():
        issues.append("前端文件缺失")
    
    if not check_backend_service():
        issues.append("后端服务导入失败")
    
    if not check_api_connection():
        issues.append("无法连接到后端服务")
    
    # 提供解决方案
    provide_solution(issues)
    
    print("\n" + "=" * 60)
    
    return len(issues) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
