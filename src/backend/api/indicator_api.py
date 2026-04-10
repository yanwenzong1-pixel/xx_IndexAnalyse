"""
API 接口层 - 指标接口
提供指标数据查询 API
"""
from flask import Blueprint
from .base_api import success_response, error_response, handle_exception
from ..service.data_fetch_service import DataFetchService
from ..service.indicator_service import IndicatorService

indicator_api = Blueprint('indicator_api', __name__, url_prefix='/api')


@indicator_api.route('/indicators', methods=['GET'])
@handle_exception
def get_indicators():
    """获取指标数据"""
    fetch_service = DataFetchService()
    
    if not fetch_service.fetch_data(use_cache=True):
        return error_response('数据获取失败', 'DATA_FETCH_ERROR')
    
    df = fetch_service.get_dataframe()
    if df is None:
        return error_response('数据为空', 'DATA_EMPTY')
    
    indicator_service = IndicatorService(df)
    indicators = indicator_service.get_all_indicators()
    
    return success_response(indicators)
