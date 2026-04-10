"""
微盘股指数分析系统 - 后端主入口
唯一启动入口（规则 1.4）
"""
from flask import Flask
from flask_cors import CORS
from .core.config import BACKEND_HOST, BACKEND_PORT, DEBUG, LOG_LEVEL, LOG_FORMAT
from .api.data_api import data_api as data_blueprint
from .api.indicator_api import indicator_api as indicator_blueprint
from .api.risk_api import risk_api as risk_blueprint
from .api.report_api import report_api as report_blueprint
from .api.predict_history_api import predict_history_api as predict_history_blueprint
import logging
import os


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 启用 CORS
    CORS(app)
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册健康检查
    register_health_check(app)
    
    return app


def setup_logging(app):
    """配置日志"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    app.logger.setLevel(getattr(logging, LOG_LEVEL))


def register_blueprints(app):
    """注册蓝图"""
    app.register_blueprint(data_blueprint)
    app.register_blueprint(indicator_blueprint)
    app.register_blueprint(risk_blueprint)
    app.register_blueprint(report_blueprint)
    app.register_blueprint(predict_history_blueprint)


def register_health_check(app):
    """注册健康检查接口"""
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': '服务运行正常'}


if __name__ == '__main__':
    app = create_app()
    app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=DEBUG)
