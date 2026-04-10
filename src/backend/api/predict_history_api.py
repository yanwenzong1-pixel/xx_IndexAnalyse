"""
API - 历史下跌概率回溯与校准评估（legacy 算法经 micro_cap_legacy_bridge）
"""
from flask import Blueprint, jsonify, request

from .base_api import handle_exception
from ..core.config import HISTORY_DAYS_DEFAULT, HISTORY_DAYS_MAX
from ..service.micro_cap_legacy_bridge import (
    predict_history_payload,
    predict_history_summary_payload,
    risk_history_payload,
)

predict_history_api = Blueprint("predict_history_api", __name__, url_prefix="/api")


def _parse_bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


@predict_history_api.route("/predict/history", methods=["GET"])
@handle_exception
def get_predict_history():
    days = request.args.get("days", HISTORY_DAYS_DEFAULT, type=int)
    include_factors = _parse_bool(request.args.get("include_factors"))
    include_evaluation = _parse_bool(request.args.get("include_evaluation"))
    if days < 1:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_days",
                    "message": "days 参数必须大于 0",
                }
            ),
            400,
        )
    if days > HISTORY_DAYS_MAX:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_days",
                    "message": f"days 参数不能超过 {HISTORY_DAYS_MAX}",
                }
            ),
            400,
        )
    result = predict_history_payload(days, include_evaluation=include_evaluation)
    if not include_factors and result.get("success") and isinstance(result.get("data"), list):
        pass
    return jsonify(result)


@predict_history_api.route("/predict/history/summary", methods=["GET"])
@handle_exception
def get_predict_history_summary():
    days = request.args.get("days", HISTORY_DAYS_DEFAULT, type=int)
    if days < 1 or days > HISTORY_DAYS_MAX:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_days",
                    "message": f"days 参数必须在 1-{HISTORY_DAYS_MAX} 范围内",
                }
            ),
            400,
        )
    result = predict_history_summary_payload(days)
    return jsonify(result)


@predict_history_api.route("/risk/history", methods=["GET"])
@handle_exception
def get_risk_history():
    days = request.args.get("days", HISTORY_DAYS_DEFAULT, type=int)
    if days < 1:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_days",
                    "message": "days 参数必须大于 0",
                }
            ),
            400,
        )
    if days > HISTORY_DAYS_MAX:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_days",
                    "message": f"days 参数不能超过 {HISTORY_DAYS_MAX}",
                }
            ),
            400,
        )
    result = risk_history_payload(days)
    return jsonify(result)


@predict_history_api.route("/risk/current", methods=["GET"])
@handle_exception
def get_current_risk():
    from ..service.micro_cap_legacy_bridge import get_legacy_facade  # noqa: PLC0415

    facade = get_legacy_facade()
    if not facade.ensure_data() or facade.analyzer.df is None:
        return (
            jsonify({"success": False, "message": "数据未初始化"}),
            500,
        )
    analyzer = facade.analyzer
    risk_score = analyzer.assess_risk_level()
    latest_date = analyzer.df.iloc[-1]["date"]
    date_str = (
        latest_date.strftime("%Y-%m-%d")
        if hasattr(latest_date, "strftime")
        else str(latest_date)
    )
    if risk_score <= 3:
        risk_level = "low"
    elif risk_score <= 5:
        risk_level = "medium"
    elif risk_score <= 7:
        risk_level = "high"
    else:
        risk_level = "very_high"
    return jsonify(
        {
            "success": True,
            "data": {
                "date": date_str,
                "risk_score": float(risk_score),
                "risk_level": risk_level,
            },
        }
    )
