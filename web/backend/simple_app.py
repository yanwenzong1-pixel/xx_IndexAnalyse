"""
简化版启动脚本 - 用于测试部署
支持 CORS 跨域访问
"""

import os
import json
from flask import Flask, jsonify, request, make_response
from analyzer import MicroCapAnalyzer
from utils.history_backtest_service import get_history_service
from utils.history_risk_service import get_history_risk_service

app = Flask(__name__)
HISTORY_DAYS_DEFAULT = 300
HISTORY_DAYS_MAX = 300

# 添加 CORS 支持（手动添加响应头）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 全局分析器实例
analyzer = MicroCapAnalyzer()
RISK_OUTPUT_SOURCE = "backend-live"
RISK_OUTPUT_VERSION = "risk-v2-2dp"

# 历史回溯服务（延迟初始化）
history_service = None

# 历史风险服务（延迟初始化）
history_risk_service = None

# 初始化数据
print("正在初始化数据...")
try:
    analyzer.fetch_data()
    print("✅ 数据初始化成功")
    
    # 初始化历史回溯服务
    history_service = get_history_service(analyzer)
    print("✅ 历史回溯服务初始化成功")
    
    # 初始化历史风险服务
    history_risk_service = get_history_risk_service(analyzer)
    print("✅ 历史风险服务初始化成功")
except Exception as e:
    print(f"⚠️ 数据初始化失败：{e}")

# API 路由
@app.route('/api/data', methods=['GET'])
def get_data():
    """获取微盘股指数数据"""
    if analyzer.df is None:
        return jsonify({"success": False, "message": "数据获取失败"})
    
    # 获取最新数据
    latest = analyzer.df.iloc[-1]
    return jsonify({
        "success": True,
        "data": {
            "date": latest['date'].strftime('%Y-%m-%d'),
            "close": latest['close'],
            "change_pct": latest['change_pct'],
            "amount": latest['amount'],
            "turnover": latest['turnover']
        }
    })

@app.route('/api/predict', methods=['GET'])
def get_predict():
    """获取预测数据"""
    if analyzer.df is None:
        return jsonify({"success": False, "message": "数据获取失败"})
    
    # 获取详细预测结果
    results = analyzer.predict_downside_probability_detailed()
    return jsonify({
        "success": True,
        "data": results
    })

@app.route('/api/predict/history', methods=['GET'])
def get_predict_history():
    """
    获取历史预测数据
    
    Query Parameters:
        days (int): 回溯天数，默认 300，范围 1-300
        include_factors (bool): 是否包含因子详情，默认 false
        
    Returns:
        JSON: {
            success: bool,
            data: List[Dict],
            metadata: Dict,
            error: Optional[str]
        }
    """
    if history_service is None:
        return jsonify({
            "success": False,
            "error": "service_not_initialized",
            "message": "历史回溯服务未初始化"
        })
    
    try:
        # 获取参数
        days = request.args.get('days', HISTORY_DAYS_DEFAULT, type=int)
        include_factors = request.args.get('include_factors', False, type=bool)
        include_evaluation = request.args.get('include_evaluation', False, type=bool)
        
        # 参数验证
        if days < 1:
            return jsonify({
                "success": False,
                "error": "invalid_days",
                "message": "days 参数必须大于 0"
            }), 400
        
        if days > HISTORY_DAYS_MAX:
            return jsonify({
                "success": False,
                "error": "invalid_days",
                "message": f"days 参数不能超过 {HISTORY_DAYS_MAX}"
            }), 400
        
        # 调用历史回溯服务
        result = history_service.calculate_history(days, include_evaluation=include_evaluation)
        
        # 如果不包含因子详情，简化返回数据
        if not include_factors and result['success']:
            # 可以选择移除或简化某些字段以减少响应大小
            pass
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": "invalid_parameter",
            "message": f"参数错误：{str(e)}"
        }), 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "calculation_failed",
            "message": f"计算失败：{str(e)}"
        }), 500


@app.route('/api/predict/history/summary', methods=['GET'])
def get_predict_history_summary():
    """
    获取历史预测数据的统计摘要
    
    Query Parameters:
        days (int): 回溯天数，默认 300
        
    Returns:
        JSON: 统计摘要数据
    """
    if history_service is None:
        return jsonify({
            "success": False,
            "error": "service_not_initialized",
            "message": "历史回溯服务未初始化"
        })
    
    try:
        days = request.args.get('days', HISTORY_DAYS_DEFAULT, type=int)
        
        if days < 1 or days > HISTORY_DAYS_MAX:
            return jsonify({
                "success": False,
                "error": "invalid_days",
                "message": f"days 参数必须在 1-{HISTORY_DAYS_MAX} 范围内"
            }), 400
        
        result = history_service.get_history_summary(days)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "calculation_failed",
            "message": f"计算失败：{str(e)}"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "success": True,
        "message": "服务运行正常",
        "version": "2.1.0 (历史回溯版)"
    })


@app.route('/api/save_index_data', methods=['POST'])
def save_index_data():
    """
    保存指数数据到静态 JSON 文件
    
    Request Body:
        {
            "data": [...],  # 指数数据数组
            "filename": "index_history_data.json"  # 文件名
        }
    
    Returns:
        JSON 格式响应
    """
    import os
    import json
    
    print("[API] 收到保存指数数据请求")
    
    try:
        # 解析请求体
        req_data = request.get_json()
        if not req_data:
            print("[API] 错误：请求体为空")
            return jsonify({
                "success": False,
                "error": "empty_request",
                "message": "请求体为空"
            }), 400
        
        data = req_data.get('data')
        filename = req_data.get('filename', 'index_history_data.json')
        
        print(f"[API] 数据条数：{len(data) if data else 0}, 文件名：{filename}")
        
        # 验证数据
        if not data or not isinstance(data, list):
            print("[API] 错误：数据格式错误")
            return jsonify({
                "success": False,
                "error": "invalid_data",
                "message": "数据格式错误"
            }), 400
        
        # 确定文件路径
        # 前端静态文件目录
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        file_path = os.path.join(frontend_dir, filename)
        
        print(f"[API] 文件路径：{file_path}")
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[API] ✅ 文件保存成功：{file_path}")
        
        return jsonify({
            "success": True,
            "message": f"成功保存 {len(data)} 条数据",
            "file": file_path,
            "count": len(data)
        })
        
    except Exception as e:
        print(f"[API] ❌ 保存失败：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "save_failed",
            "message": f"保存失败：{str(e)}"
        }), 500


# ========== 新增：风险趋势相关路由 ==========

@app.route('/api/risk/history', methods=['GET'])
def get_risk_history():
    """
    获取历史风险打分数据
    
    Query Parameters:
        days (int): 回溯天数，默认 300，范围 1-300
        
    Returns:
        JSON 格式的历史风险数据
    """
    print(f"[API] 收到风险历史数据请求，参数: {request.args}")
    
    if history_risk_service is None:
        print("[API] 错误：历史风险服务未初始化")
        return jsonify({
            "success": False,
            "error": "service_not_initialized",
            "message": "历史风险服务未初始化"
        }), 500
    
    try:
        # 获取参数
        days = request.args.get('days', HISTORY_DAYS_DEFAULT, type=int)
        print(f"[API] 解析参数：days = {days}")
        
        # 参数验证
        if days < 1:
            print("[API] 错误：days 参数小于 1")
            return jsonify({
                "success": False,
                "error": "invalid_days",
                "message": "days 参数必须大于 0"
            }), 400
        
        if days > HISTORY_DAYS_MAX:
            print(f"[API] 错误：days 参数超过 {HISTORY_DAYS_MAX}")
            return jsonify({
                "success": False,
                "error": "invalid_days",
                "message": f"days 参数不能超过 {HISTORY_DAYS_MAX}"
            }), 400
        
        # 调用历史风险服务
        print(f"[API] 开始计算历史风险数据，天数: {days}")
        result = history_risk_service.calculate_history(days)

        # 输出兜底：统一风险分为两位小数
        if result.get("success") and isinstance(result.get("data"), list):
            for item in result["data"]:
                if "risk_score" in item:
                    item["risk_score"] = round(float(item["risk_score"]), 2)
                item.setdefault("source", RISK_OUTPUT_SOURCE)
            metadata = result.setdefault("metadata", {})
            for key in ("avg_risk", "max_risk", "min_risk", "current_risk"):
                if key in metadata:
                    metadata[key] = round(float(metadata[key]), 2)
            metadata.setdefault("source", RISK_OUTPUT_SOURCE)
            metadata.setdefault("version", RISK_OUTPUT_VERSION)
        print(f"[API] 历史风险计算完成，结果: {result['success'] if 'success' in result else 'ERROR'}")
        
        return jsonify(result)
        
    except ValueError as e:
        print(f"[API] 参数错误：{e}")
        return jsonify({
            "success": False,
            "error": "invalid_parameter",
            "message": f"参数错误：{str(e)}"
        }), 400
        
    except Exception as e:
        print(f"[API] 计算失败：{e}")
        import traceback
        traceback.print_exc()  # 输出详细错误信息
        return jsonify({
            "success": False,
            "error": "calculation_failed",
            "message": f"计算失败：{str(e)}"
        }), 500


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """刷新行情并重算历史模块（旧链路兼容）。"""
    global history_service, history_risk_service
    try:
        ok = analyzer.fetch_data()
        if not ok or analyzer.df is None:
            return jsonify({"success": False, "message": "刷新失败：行情数据获取失败"}), 500

        history_service = get_history_service(analyzer)
        history_risk_service = get_history_risk_service(analyzer)
        predict_res = history_service.calculate_history(HISTORY_DAYS_DEFAULT, include_evaluation=True)
        risk_res = history_risk_service.calculate_history(HISTORY_DAYS_DEFAULT)
        return jsonify({
            "success": True,
            "message": "刷新成功（已完成历史重算）",
            "data": {
                "predict_history_success": bool(predict_res.get("success")),
                "predict_history_days": len(predict_res.get("data") or []),
                "risk_history_success": bool(risk_res.get("success")),
                "risk_history_days": len(risk_res.get("data") or []),
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "refresh_failed",
            "message": f"刷新失败：{str(e)}"
        }), 500


@app.route('/api/risk/current', methods=['GET'])
def get_current_risk():
    """
    获取当前风险打分（快速接口）
    
    Returns:
        JSON 格式的当前风险数据
    """
    if analyzer.df is None:
        return jsonify({
            "success": False,
            "message": "数据未初始化"
        }), 500
    
    try:
        risk_score = round(float(analyzer.assess_risk_level()), 2)
        
        # 获取日期
        latest_date = analyzer.df.iloc[-1]['date']
        date_str = latest_date.strftime('%Y-%m-%d') if hasattr(latest_date, 'strftime') else str(latest_date)
        
        # 风险等级文本
        if risk_score <= 3:
            risk_level = 'low'
        elif risk_score <= 5:
            risk_level = 'medium'
        elif risk_score <= 7:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        return jsonify({
            "success": True,
            "data": {
                "date": date_str,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "source": RISK_OUTPUT_SOURCE,
                "version": RISK_OUTPUT_VERSION
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "calculation_failed",
            "message": f"计算失败：{str(e)}"
        }), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("微盘股指数分析系统 v2.1")
    print("25 因子优化版 - 风险趋势增强版")
    print("=" * 60)
    print("\n服务地址：http://localhost:5000")
    print("API 端点:")
    print("  - /api/data - 获取指数数据")
    print("  - /api/predict - 获取预测数据")
    print("  - /api/predict/history - 获取历史预测数据")
    print("  - /api/predict/history/summary - 获取历史统计摘要")
    print("  - /api/risk/history - 获取历史风险打分（新增）")
    print("  - /api/risk/current - 获取当前风险打分（新增）")
    print("  - /api/health - 健康检查")
    print("  - /api/save_index_data - 保存指数数据（新增）")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60 + "\n")
    
    # 关闭 debug 模式，使用 threaded=True 处理并发请求
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
