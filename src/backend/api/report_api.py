"""
API 接口层 - 报告接口
提供报告生成 API
"""
from flask import Blueprint
from .base_api import success_response, error_response, handle_exception
from ..service.data_fetch_service import DataFetchService
from ..service.risk_service import RiskService
from ..service.decline_prediction_service import DeclinePredictionService
from ..service.report_service import ReportService

report_api = Blueprint('report_api', __name__, url_prefix='/api')


@report_api.route('/report', methods=['GET'])
@handle_exception
def get_report():
    """获取每日报告"""
    fetch_service = DataFetchService()
    
    if not fetch_service.fetch_data(use_cache=True):
        return error_response('数据获取失败', 'DATA_FETCH_ERROR')
    
    df = fetch_service.get_dataframe()
    if df is None:
        return error_response('数据为空', 'DATA_EMPTY')
    
    risk_service = RiskService(df)
    prediction_service = DeclinePredictionService(df)
    
    prediction = prediction_service.predict_downside_probability()
    risk_data = risk_service.get_risk_data(
        downside_probability=prediction['prob_t1'],
        expected_decline=0.0
    )
    
    decline_results = prediction_service.calculate_expected_decline(
        prediction['prob_t1'],
        prediction['prob_t5']
    )
    
    report_service = ReportService(df, risk_data, {}, decline_results)
    report = report_service.generate_daily_report()
    
    return success_response({'report': report})
