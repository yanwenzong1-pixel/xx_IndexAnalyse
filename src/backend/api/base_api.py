"""
API 接口层 - 基础 API 封装
统一响应格式和错误处理
"""
from flask import jsonify
from typing import Any, Optional
from ..model.response_model import APIResponse, ErrorResponse


def success_response(data: Any = None, message: str = '成功') -> Any:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 消息
        
    Returns:
        Flask Response
    """
    response = APIResponse(success=True, message=message, data=data)
    return jsonify(response.to_dict())


def error_response(message: str = '操作失败', error_code: str = 'UNKNOWN_ERROR', 
                   status_code: int = 400, details: Optional[dict] = None) -> Any:
    """
    错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        status_code: HTTP 状态码
        details: 详细信息
        
    Returns:
        Flask Response
    """
    response = ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        details=details
    )
    return jsonify(response.to_dict()), status_code


def handle_exception(func):
    """
    异常处理装饰器
    
    Args:
        func: 被装饰的函数
        
    Returns:
        包装后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"API 异常：{e}")
            return error_response(
                message=str(e),
                error_code='INTERNAL_ERROR',
                status_code=500
            )
    wrapper.__name__ = func.__name__
    return wrapper
