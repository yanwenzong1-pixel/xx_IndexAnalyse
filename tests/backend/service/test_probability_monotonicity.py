import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]  # repo root
WEB_BACKEND = ROOT / "web" / "backend"
sys.path.insert(0, str(WEB_BACKEND))

from utils.factor_data_service import get_factor_service  # noqa: E402
from utils.risk_calculation_service import get_risk_calculator  # noqa: E402


def make_df(change_pct_value: float, n: int = 40):
    """
    构造合成 K 线数据：change_pct 全程固定为 change_pct_value（单位：百分比点）
    """
    dates = pd.date_range("2024-01-01", periods=n)
    change_pct = [change_pct_value] * n
    # 简化：用累计涨跌幅构造 close
    cumulative = sum(change_pct) / 100.0
    # 为了避免数值过大，使用逐日累计
    closes = []
    running = 0.0
    for c in change_pct:
        running += c / 100.0
        closes.append(1000.0 * (1.0 + running))

    df = pd.DataFrame(
        {
            "date": dates,
            "close": closes,
            "amount": [2e9] * n,
            "turnover": [4.0] * n,
            "change_pct": change_pct,
        }
    )
    return df


def test_uptrend_has_lower_downside_probability():
    # 准备上行与下行情景
    up_df = make_df(0.2)     # 每日 +0.2%
    down_df = make_df(-0.2)  # 每日 -0.2%

    factor_service = get_factor_service()
    risk_calc = get_risk_calculator()

    up_factors = factor_service.get_all_factors(up_df)
    down_factors = factor_service.get_all_factors(down_df)

    up_pred = risk_calc.predict_downside_probability(up_factors, df=up_df)
    down_pred = risk_calc.predict_downside_probability(down_factors, df=down_df)

    assert 0.0 < up_pred["prob_t1"] < 1.0
    assert 0.0 < down_pred["prob_t1"] < 1.0
    assert 0.0 < up_pred["prob_t5"] < 1.0
    assert 0.0 < down_pred["prob_t5"] < 1.0

    # 上涨趋势应当降低下跌概率
    assert up_pred["prob_t1"] < down_pred["prob_t1"]
    assert up_pred["prob_t5"] < down_pred["prob_t5"]

