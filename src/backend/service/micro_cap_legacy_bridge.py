"""
Bridge to legacy micro-cap implementation under web/backend (analyzer + utils).

Tier A single entry uses src/backend; algorithms remain in web/backend until fully inlined.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    pass

_REPO_ROOT = Path(__file__).resolve().parents[3]
_WEB_BACKEND = _REPO_ROOT / "web" / "backend"
_LEGACY_CACHE_DIR = _WEB_BACKEND / "data" / "cache"


def ensure_legacy_web_backend_path() -> None:
    s = str(_WEB_BACKEND.resolve())
    if s not in sys.path:
        sys.path.insert(0, s)


class MicroCapLegacyFacade:
    """Lazy MicroCapAnalyzer + history services (legacy modules)."""

    _instance: Optional["MicroCapLegacyFacade"] = None

    def __init__(self) -> None:
        ensure_legacy_web_backend_path()
        from analyzer import MicroCapAnalyzer  # type: ignore  # noqa: PLC0415

        self._analyzer = MicroCapAnalyzer()
        self._history_backtest = None
        self._history_risk = None

    @classmethod
    def reset_singleton(cls) -> None:
        cls._instance = None

    @classmethod
    def instance(cls) -> "MicroCapLegacyFacade":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def ensure_data(self) -> bool:
        if self._analyzer.df is None:
            return bool(self._analyzer.fetch_data())
        return True

    @property
    def analyzer(self) -> Any:
        return self._analyzer

    def history_backtest(self) -> Any:
        if self._history_backtest is None:
            import utils.history_backtest_service as hbs  # type: ignore  # noqa: PLC0415

            hbs._history_service_instance = None  # type: ignore[attr-defined]
            from utils.history_backtest_service import get_history_service  # type: ignore  # noqa: PLC0415

            self._history_backtest = get_history_service(self._analyzer)
        return self._history_backtest

    def history_risk(self) -> Any:
        if self._history_risk is None:
            from utils.history_risk_service import get_history_risk_service  # type: ignore  # noqa: PLC0415

            self._history_risk = get_history_risk_service(self._analyzer)
        return self._history_risk


def get_legacy_facade() -> MicroCapLegacyFacade:
    return MicroCapLegacyFacade.instance()


def predict_history_payload(days: int, include_evaluation: bool) -> Dict[str, Any]:
    """Compute predict/history JSON (same contract as legacy simple_app)."""
    facade = get_legacy_facade()
    if not facade.ensure_data():
        return {
            "success": False,
            "data": [],
            "metadata": {},
            "error": "市场数据获取失败",
        }
    return facade.history_backtest().calculate_history(
        days, include_evaluation=include_evaluation
    )


def risk_history_payload(days: int) -> Dict[str, Any]:
    facade = get_legacy_facade()
    if not facade.ensure_data():
        return {
            "success": False,
            "error": "data_not_initialized",
            "message": "基础数据未初始化",
        }
    return facade.history_risk().calculate_history(days)


def predict_history_summary_payload(days: int) -> Dict[str, Any]:
    facade = get_legacy_facade()
    if not facade.ensure_data():
        return {"success": False, "error": "市场数据获取失败"}
    return facade.history_backtest().get_history_summary(days)


def _clear_legacy_cache_files() -> Dict[str, Any]:
    cleared: list[str] = []
    failed: list[str] = []
    if not _LEGACY_CACHE_DIR.exists():
        return {"cleared": cleared, "failed": failed}

    explicit_names = {
        "all_factors.json",
        "macro_factors.json",
        "policy_factors.json",
    }
    for path in _LEGACY_CACHE_DIR.glob("*.json"):
        name = path.name
        if name in explicit_names or name.endswith("_history.json"):
            try:
                path.unlink()
                cleared.append(name)
            except OSError:
                failed.append(name)
    return {"cleared": cleared, "failed": failed}


def refresh_history_after_market_update(
    days: int,
    include_evaluation: bool = True,
    include_risk: bool = True,
) -> Dict[str, Any]:
    """
    Reset legacy singleton and precompute history payloads after market refresh.
    """
    cache_result = _clear_legacy_cache_files()
    MicroCapLegacyFacade.reset_singleton()

    predict_result = predict_history_payload(days, include_evaluation=include_evaluation)
    risk_result = None
    if include_risk:
        risk_result = risk_history_payload(days)

    return {
        "refreshed_at": datetime.now().isoformat(),
        "requested_days": days,
        "legacy_cache_cleared_count": len(cache_result["cleared"]),
        "legacy_cache_clear_failed_count": len(cache_result["failed"]),
        "predict_history_success": bool(predict_result.get("success")),
        "predict_history_days": len(predict_result.get("data") or []),
        "risk_history_success": None if risk_result is None else bool(risk_result.get("success")),
        "risk_history_days": 0 if not risk_result else len(risk_result.get("data") or []),
    }
