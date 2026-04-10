# -*- coding: utf-8 -*-
"""简化版后端启动脚本"""
import sys
import os

# 添加 backend 目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'web', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

print("=" * 60)
print("启动后端服务...")
print("=" * 60)

try:
    # 导入 Flask
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    # 导入分析器
    from analyzer import MicroCapAnalyzer
    
    # 导入服务
    from utils.history_backtest_service import get_history_service
    from utils.history_risk_service import get_history_risk_service
    
    print("✅ 所有模块导入成功")
    
    # 创建 Flask 应用
    app = Flask(__name__)
    CORS(app)  # 启用 CORS
    
    # 初始化分析器
    print("\n初始化数据...")
    analyzer = MicroCapAnalyzer()
    if analyzer.fetch_data():
        print("✅ 数据初始化成功")
    else:
        print("❌ 数据初始化失败")
        sys.exit(1)
    
    # 初始化服务
    history_service = get_history_service(analyzer)
    print("✅ 历史回溯服务初始化成功")
    
    history_risk_service = get_history_risk_service(analyzer)
    print("✅ 历史风险服务初始化成功")
    
    # 添加健康检查接口
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "success": True,
            "message": "服务运行正常",
            "version": "2.1.0"
        })
    
    # 添加风险历史接口
    @app.route('/api/risk/history', methods=['GET'])
    def get_risk_history():
        try:
            days = request.args.get('days', 252, type=int)
            if days < 1 or days > 252:
                return jsonify({
                    "success": False,
                    "error": "invalid_days",
                    "message": "days 参数必须在 1-252 范围内"
                }), 400
            
            result = history_risk_service.calculate_history(days)
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "calculation_failed",
                "message": str(e)
            }), 500
    
    # 添加当前风险接口
    @app.route('/api/risk/current', methods=['GET'])
    def get_current_risk():
        try:
            risk_score = analyzer.assess_risk_level()
            latest_date = analyzer.df.iloc[-1]['date']
            date_str = latest_date.strftime('%Y-%m-%d') if hasattr(latest_date, 'strftime') else str(latest_date)
            
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
                    "risk_score": float(risk_score),
                    "risk_level": risk_level
                }
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "calculation_failed",
                "message": str(e)
            }), 500
    
    print("\n" + "=" * 60)
    print("服务启动成功！")
    print("监听地址：http://localhost:5000")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务\n")
    
    # 启动服务
    app.run(host='0.0.0.0', port=5000, debug=False)
    
except Exception as e:
    print(f"\n❌ 启动失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
