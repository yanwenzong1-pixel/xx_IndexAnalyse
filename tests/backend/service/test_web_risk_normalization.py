import os
import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]  # repo root
WEB_BACKEND = ROOT / "web" / "backend"
sys.path.insert(0, str(WEB_BACKEND))


from utils.factor_data_service import get_factor_service  # noqa: E402
from utils.risk_calculation_service import FactorStandardizer, RiskCalculator  # noqa: E402
from utils.history_risk_service import get_history_risk_service  # noqa: E402


def test_normalize_bidirectional_monotonic_distance():
    """
    双向风险因子：与最优值的“距离”越大，标准化风险值应越大。
    """
    # 构造：history 中主要是 rolling(5).mean=4.0，最后窗口使当前因子接近 5.0
    days = 40
    turnover = [4.0] * (days - 5) + [3.0, 5.0, 5.0, 5.0, 7.0]  # 最后 5 日平均=5.0
    df = pd.DataFrame({"turnover": turnover})

    std = FactorStandardizer()
    optimal = 5.0
    window_days = 30

    risk_opt = std.normalize_bidirectional(
        factor_value=optimal,
        factor_id="L3",
        optimal_value=optimal,
        window_days=window_days,
        df_context=df,
    )
    risk_mid = std.normalize_bidirectional(
        factor_value=4.5,
        factor_id="L3",
        optimal_value=optimal,
        window_days=window_days,
        df_context=df,
    )
    risk_far = std.normalize_bidirectional(
        factor_value=6.0,
        factor_id="L3",
        optimal_value=optimal,
        window_days=window_days,
        df_context=df,
    )

    assert risk_opt == 0.0
    assert 0.0 < risk_mid < risk_far <= 1.0


def test_macro_m1_risk_direction_uses_negative_normalization():
    """
    M1 在 factors_config 中标记为 negative：calculate_dimension_risks() 应传入 normalize(-M1_value, 'M1')。
    """
    calculator = RiskCalculator()
    calculator.standardizer.normalize = Mock(return_value=0.123)
    calculator.standardizer.normalize_bidirectional = Mock(return_value=0.234)

    m1_value = 2.5
    factors = {"M1": m1_value}
    df_context = pd.DataFrame({"turnover": [1.0]})

    dim_risks = calculator.calculate_dimension_risks(factors, df_context=df_context)
    assert "macro" in dim_risks

    assert calculator.standardizer.normalize.called
    args, kwargs = calculator.standardizer.normalize.call_args
    assert args[0] == -m1_value
    assert args[1] == "M1"
    assert not calculator.standardizer.normalize_bidirectional.called


def test_factor_history_is_deterministic_when_df_context_provided():
    service = get_factor_service()

    df1 = pd.DataFrame({"turnover": [4.0] * 30 + [3.0, 5.0, 5.0, 5.0, 7.0]})
    df2 = pd.DataFrame({"turnover": [4.0] * 30 + [2.0, 5.0, 5.0, 5.0, 8.0]})  # 最后 5 日平均不同

    h1_a = service.get_factor_history("L3", days=10, df=df1)
    h1_b = service.get_factor_history("L3", days=10, df=df1)
    h2 = service.get_factor_history("L3", days=10, df=df2)

    assert h1_a == h1_b
    assert h1_a != h2


def test_history_risk_service_returns_two_decimal_scores_with_metadata():
    class DummyAnalyzer:
        def __init__(self):
            self.df = pd.DataFrame({
                "date": pd.date_range("2025-01-01", periods=30, freq="D"),
                "close": np.linspace(100, 120, 30),
                "change_pct": np.linspace(-1.2, 1.3, 30),
                "amount": np.linspace(1e9, 2e9, 30),
                "turnover": np.linspace(2.0, 6.0, 30),
            })

        def assess_risk_level(self):
            # 模拟上游返回高精度浮点，服务层应收口到两位小数。
            return 5.6789

    service = get_history_risk_service(DummyAnalyzer())
    result = service.calculate_history(days=10)

    assert result["success"] is True
    assert len(result["data"]) > 0
    assert result["metadata"]["source"] == "backend-live"
    assert result["metadata"]["version"] == "risk-v2-2dp"

    for item in result["data"]:
        assert "source" in item
        assert item["source"] == "backend-live"
        value = item["risk_score"]
        assert isinstance(value, float)
        assert value == round(value, 2)

    for key in ("avg_risk", "max_risk", "min_risk", "current_risk"):
        value = result["metadata"][key]
        assert isinstance(value, float)
        assert value == round(value, 2)

