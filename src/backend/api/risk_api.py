"""
API 接口层 - 风险接口
提供风险评估 API
"""
from flask import Blueprint
from .base_api import success_response, error_response, handle_exception
from ..service.data_fetch_service import DataFetchService
from ..service.risk_service import RiskService
from ..service.decline_prediction_service import DeclinePredictionService

risk_api = Blueprint('risk_api', __name__, url_prefix='/api')


@risk_api.route('/risk', methods=['GET'])
@handle_exception
def get_risk():
    """获取风险评估"""
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
    
    return success_response({
        **risk_data,
        'decline': decline_results
    })
