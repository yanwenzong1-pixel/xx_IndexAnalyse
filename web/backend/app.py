from flask import Flask, jsonify
from flask_cors import CORS
from analyzer import MicroCapAnalyzer
from utils.email_utils import send_email_report
from utils.scheduler_utils import scheduler

app = Flask(__name__)
CORS(app)  # 启用CORS

# 全局分析器实例
analyzer = MicroCapAnalyzer()

# 初始化数据
analyzer.fetch_data()

def refresh_data():
    """刷新数据"""
    print("正在刷新数据...")
    analyzer.fetch_data()
    print("数据刷新完成")

def send_daily_report():
    """发送每日报告"""
    print("正在生成并发送每日报告...")
    report = analyzer.generate_daily_report()
    send_email_report(report)
    print("每日报告发送完成")

# 启动定时任务
def start_scheduler():
    """启动定时任务"""
    # 每3小时刷新一次数据
    scheduler.add_job(refresh_data, 'interval', hours=3)
    # 每天15:30发送报告
    scheduler.add_job(send_daily_report, 'cron', hour=15, minute=30)
    scheduler.start()
    print("定时任务已启动")

# 启动定时任务
start_scheduler()

# API路由
@app.route('/api/data', methods=['GET'])
def get_data():
    """获取微盘股指数数据"""
    if analyzer.df is None:
        return jsonify({"success": False, "message": "数据获取失败"})
    
    # 获取最新数据
    latest = analyzer.df.iloc[-1]
    
    # 获取历史数据（最近60天）
    history = []
    for _, row in analyzer.df.tail(60).iterrows():
        history.append({
            "date": row['date'].strftime('%Y-%m-%d'),
            "close": row['close'],
            "change_pct": row['change_pct'],
            "amount": row['amount'],
            "turnover": row['turnover']
        })
    
    return jsonify({
        "success": True,
        "data": {
            "latest": {
                "date": latest['date'].strftime('%Y-%m-%d'),
                "close": latest['close'],
                "change_pct": latest['change_pct'],
                "amount": latest['amount'],
                "turnover": latest['turnover']
            },
            "history": history
        }
    })

@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    """获取指标数据"""
    if analyzer.df is None:
        return jsonify({"success": False, "message": "数据获取失败"})
    
    return jsonify({
        "success": True,
        "data": {
            "liquidity": analyzer.calculate_liquidity_indicators(),
            "fund_structure": analyzer.calculate_fund_structure_indicators(),
            "valuation": analyzer.calculate_valuation_indicators(),
            "policy": analyzer.calculate_policy_indicators(),
            "macro": analyzer.calculate_macro_indicators()
        }
    })

@app.route('/api/risk', methods=['GET'])
def get_risk():
    """获取风险评估"""
    if analyzer.df is None:
        return jsonify({"success": False, "message": "数据获取失败"})
    
    risk_level = analyzer.assess_risk_level()
    downside_probability = analyzer.predict_downside_risk()
    alert, alert_message = analyzer.check_alert_conditions()
    
    return jsonify({
        "success": True,
        "data": {
            "risk_level": risk_level,
            "downside_probability": downside_probability,
            "alert": alert,
            "alert_message": alert_message
        }
    })

@app.route('/api/report', methods=['GET'])
def get_report():
    """获取每日报告"""
    if analyzer.df is None:
        return jsonify({"success": False, "message": "数据获取失败"})
    
    report = analyzer.generate_daily_report()
    return jsonify({
        "success": True,
        "data": {
            "report": report
        }
    })

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """手动刷新数据"""
    success = analyzer.fetch_data()
    if success:
        return jsonify({"success": True, "message": "数据刷新成功"})
    else:
        return jsonify({"success": False, "message": "数据刷新失败"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
