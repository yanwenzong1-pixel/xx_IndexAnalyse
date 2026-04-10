"""
API 接口层 - 数据接口
提供股票数据查询 API
"""
from flask import Blueprint
from .base_api import success_response, error_response, handle_exception
from ..core.config import HISTORY_DAYS_DEFAULT
from ..service.data_fetch_service import DataFetchService
from ..service.micro_cap_legacy_bridge import refresh_history_after_market_update

data_api = Blueprint('data_api', __name__, url_prefix='/api')


@data_api.route('/data', methods=['GET'])
@handle_exception
def get_stock_data():
    """获取股票数据"""
    service = DataFetchService()
    
    if not service.fetch_data(use_cache=True):
        return error_response('数据获取失败', 'DATA_FETCH_ERROR')
    
    latest = service.get_latest_data()
    history = service.get_history_data(days=60)
    
    if not latest:
        return error_response('数据为空', 'DATA_EMPTY')
    
    return success_response({
        'latest': latest,
        'history': history
    })


@data_api.route('/refresh', methods=['POST'])
@handle_exception
def refresh_data():
    """刷新数据"""
    service = DataFetchService()
    
    if not service.fetch_data(use_cache=False):
        return error_response('刷新失败', 'REFRESH_ERROR')

    # 失效 src/backend 侧衍生缓存，避免刷新后读取旧指标/旧风险。
    service.cache_dao.delete('indicators')
    service.cache_dao.delete('risk')

    recompute = refresh_history_after_market_update(
        days=HISTORY_DAYS_DEFAULT,
        include_evaluation=True,
        include_risk=True,
    )

    return success_response(
        data={
            'recompute': recompute,
        },
        message='刷新成功（已完成历史趋势重算）'
    )
