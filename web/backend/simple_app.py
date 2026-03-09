from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用CORS

# 模拟数据
def get_mock_data():
    return {
        "latest": {
            "date": "2024-03-06",
            "close": 1500.0,
            "change_pct": 2.5,
            "amount": 1000000000,
            "turnover": 5.2
        },
        "history": [
            {
                "date": "2024-03-05",
                "close": 1463.5,
                "change_pct": -1.2,
                "amount": 950000000,
                "turnover": 4.8
            },
            {
                "date": "2024-03-04",
                "close": 1481.3,
                "change_pct": 0.5,
                "amount": 980000000,
                "turnover": 5.0
            }
        ]
    }

# API路由
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "success": True,
        "data": get_mock_data()
    })

@app.route('/api/risk', methods=['GET'])
def get_risk():
    return jsonify({
        "success": True,
        "data": {
            "risk_level": 5,
            "downside_probability": 0.4,
            "alert": False,
            "alert_message": ""
        }
    })

@app.route('/api/refresh', methods=['POST'])
def refresh():
    return jsonify({"success": True, "message": "数据刷新成功"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
