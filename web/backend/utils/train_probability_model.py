"""
下跌概率模型参数训练与温度缩放校准（walk-forward 简化版）

目标：
1) 用历史特征 X 构造逻辑回归样本（T+1 / T+5）
2) 通过梯度下降重训 α/β 系数（L2 正则）
3) 用温度缩放（temperature scaling）在验证集最小化 logloss
4) 写入 `web/backend/data/prob_model_params.json`

说明：
该脚本依赖现有 `MicroCapAnalyzer.fetch_data()` 获取真实历史数据。
"""

import json
import sys
from pathlib import Path

import numpy as np

# 让 `web/backend` 作为 python 包根路径，确保 `analyzer.py` 与 `utils` 可被导入
WEB_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEB_BACKEND))

from analyzer import MicroCapAnalyzer  # type: ignore
from utils.factor_data_service import get_factor_service
from utils.risk_calculation_service import get_risk_calculator


def _ensure_utf8_console() -> None:
    """
    Windows PowerShell/Console 可能默认 GBK 编码；
    这里尽量切到 UTF-8，避免打印 Unicode 字符导致脚本中断。
    """
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def sigmoid(z):
    z = np.clip(z, -35, 35)  # 避免 exp 溢出
    return 1.0 / (1.0 + np.exp(-z))


def logloss(p, y, eps=1e-12):
    p = np.clip(p, eps, 1.0 - eps)
    y = y.astype(float)
    return float(-np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))


def fit_logistic_gd(X, y, init_w, lr=0.05, steps=2000, l2=0.01):
    """
    简单批量梯度下降拟合逻辑回归：
    loss = -mean(y*log(p) + (1-y)*log(1-p)) + 0.5*l2*||w||^2（不对截距项正则）
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.asarray(init_w, dtype=float).copy()

    n = X.shape[0]
    if n == 0:
        raise ValueError("empty training set")

    # 不对截距项（w[0]）做 L2
    reg_mask = np.ones_like(w)
    reg_mask[0] = 0.0

    for _ in range(steps):
        logits = np.clip(X @ w, -35, 35)
        p = sigmoid(logits)
        grad = (X.T @ (p - y)) / n
        grad = grad + l2 * (reg_mask * w)
        w = w - lr * grad

    return w


def temperature_search(logits_train, y_train, logits_valid, y_valid):
    """
    1D 网格搜索寻找最优 temperature，使 logloss 最小。
    """
    candidate_ts = np.linspace(0.5, 5.0, 31)
    best_t = 1.0
    best_loss = float("inf")
    for t in candidate_ts:
        p_valid = sigmoid(logits_valid / t)
        cur = logloss(p_valid, y_valid)
        if cur < best_loss:
            best_loss = cur
            best_t = float(t)
    return best_t, best_loss


def train(days=150, factor_window=252, train_ratio=0.7):
    analyzer = MicroCapAnalyzer()
    if not analyzer.fetch_data():
        raise RuntimeError("fetch_data failed")

    factor_service = get_factor_service()
    risk_calculator = get_risk_calculator()

    total_days_needed = days + factor_window
    extended_df = analyzer.df.tail(total_days_needed).copy()

    actual_days = min(days, len(extended_df) - factor_window)
    if actual_days <= 0:
        raise RuntimeError(f"insufficient history: need factor_window={factor_window}")

    end_idx = len(extended_df) - 1
    start_idx = factor_window - 1

    # 样本：X_t1 shape(N,5), X_t5 shape(N,7)
    X1, y1 = [], []
    X5, y5 = [], []

    for i in range(actual_days):
        current_idx = end_idx - i
        if current_idx < start_idx:
            break

        df_up_to_current = extended_df.iloc[: current_idx + 1].copy()
        factors = factor_service.get_all_factors(df_up_to_current)

        # 计算调整后风险等中间特征（注意：不使用 α/β，仅依赖综合风险）
        _, adjusted_risk, _ = risk_calculator.calculate_comprehensive_risk(
            factors, df=df_up_to_current
        )

        # 波动率/动量/宏观不确定性
        if len(df_up_to_current) > 20:
            volatility_20d = df_up_to_current["change_pct"].rolling(20).std().iloc[-1]
        else:
            volatility_20d = 2.0

        if len(df_up_to_current) > 5:
            momentum_1d = float(df_up_to_current["change_pct"].iloc[-1])
            momentum_5d = float(df_up_to_current["change_pct"].tail(5).sum())
        else:
            momentum_1d = 0.0
            momentum_5d = 0.0

        macro_uncertainty = 0.1
        if "M2" in factors and "M3" in factors and "M4" in factors:
            macro_uncertainty = (
                abs(factors["M2"] - 50) / 50
                + abs(factors["M3"]) / 10
                + abs(factors["M4"] - 2) / 2
            ) / 3.0

        # label：T+1 下跌（future change_pct < 0）
        if current_idx + 1 <= end_idx:
            t1_change_pct = float(extended_df["change_pct"].iloc[current_idx + 1])
            y_t1 = 1.0 if t1_change_pct < 0 else 0.0

            X1.append(
                [
                    1.0,
                    float(adjusted_risk),
                    float(adjusted_risk) ** 2,
                    float(volatility_20d),
                    float(momentum_1d),
                ]
            )
            y1.append(y_t1)

        # label：T+5 下跌（未来 5 日累计 change_pct < 0）
        if current_idx + 5 <= end_idx:
            t5_cum_change_pct = float(
                extended_df["change_pct"].iloc[current_idx + 1 : current_idx + 6].sum()
            )
            y_t5 = 1.0 if t5_cum_change_pct < 0 else 0.0

            X5.append(
                [
                    1.0,
                    float(adjusted_risk),
                    float(adjusted_risk) ** 2,
                    float(volatility_20d),
                    float(momentum_5d),
                    float(macro_uncertainty),
                    float(adjusted_risk) * float(momentum_5d),
                ]
            )
            y5.append(y_t5)

    if len(X1) < 50 or len(X5) < 50:
        raise RuntimeError(f"not enough samples: t1={len(X1)}, t5={len(X5)}")

    X1 = np.asarray(X1, dtype=float)
    y1 = np.asarray(y1, dtype=float)
    X5 = np.asarray(X5, dtype=float)
    y5 = np.asarray(y5, dtype=float)

    # train/valid split（简化的 walk-forward）
    n1 = len(X1)
    n1_train = int(n1 * train_ratio)
    X1_tr, y1_tr = X1[:n1_train], y1[:n1_train]
    X1_va, y1_va = X1[n1_train:], y1[n1_train:]

    n5 = len(X5)
    n5_train = int(n5 * train_ratio)
    X5_tr, y5_tr = X5[:n5_train], y5[:n5_train]
    X5_va, y5_va = X5[n5_train:], y5[n5_train:]

    # 初始化权重：用当前 `RiskCalculator` 加载的参数作为起点
    t1w = risk_calculator.prob_model_params.get("t1_weights", {})
    init_w1 = [
        float(t1w.get("alpha_0", -1.5)),
        float(t1w.get("alpha_1", 2.0)),
        float(t1w.get("alpha_2", 0.5)),
        float(t1w.get("alpha_3", 0.03)),
        float(t1w.get("alpha_4", -0.02)),
    ]

    t5w = risk_calculator.prob_model_params.get("t5_weights", {})
    init_w5 = [
        float(t5w.get("beta_0", -1.2)),
        float(t5w.get("beta_1", 1.8)),
        float(t5w.get("beta_2", 0.4)),
        float(t5w.get("beta_3", 0.04)),
        float(t5w.get("beta_4", -0.03)),
        float(t5w.get("beta_5", 0.05)),
        float(t5w.get("beta_6", -0.02)),
    ]

    w1 = fit_logistic_gd(X1_tr, y1_tr, init_w1, lr=0.05, steps=2500, l2=0.01)
    w5 = fit_logistic_gd(X5_tr, y5_tr, init_w5, lr=0.05, steps=2500, l2=0.01)

    logits1_tr = X1_tr @ w1
    logits1_va = X1_va @ w1
    T1, loss1 = temperature_search(logits1_tr, y1_tr, logits1_va, y1_va)

    logits5_tr = X5_tr @ w5
    logits5_va = X5_va @ w5
    T5, loss5 = temperature_search(logits5_tr, y5_tr, logits5_va, y5_va)

    params_path = Path(__file__).resolve().parents[1] / "data" / "prob_model_params.json"
    out = {
        "version": 2,
        "temperature_t1": float(T1),
        "temperature_t5": float(T5),
        "t1_weights": {
            "alpha_0": float(w1[0]),
            "alpha_1": float(w1[1]),
            "alpha_2": float(w1[2]),
            "alpha_3": float(w1[3]),
            "alpha_4": float(w1[4]),
        },
        "t5_weights": {
            "beta_0": float(w5[0]),
            "beta_1": float(w5[1]),
            "beta_2": float(w5[2]),
            "beta_3": float(w5[3]),
            "beta_4": float(w5[4]),
            "beta_5": float(w5[5]),
            "beta_6": float(w5[6]),
        },
        "meta": {
            "days": int(days),
            "samples_t1": int(n1),
            "samples_t5": int(n5),
            "valid_logloss_t1": float(loss1),
            "valid_logloss_t5": float(loss5),
        },
    }

    params_path.parent.mkdir(parents=True, exist_ok=True)
    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[train_probability_model] saved: {params_path}")
    print(f"[train_probability_model] temperature_t1={T1:.4f}, temperature_t5={T5:.4f}")
    return out


if __name__ == "__main__":
    _ensure_utf8_console()
    # 训练规模可按需调整；越大需要越长时间
    out: dict | None = None
    try:
        out = train(days=150)
    except Exception as e:
        # 在无法依赖控制台输出的情况下，仍然把错误落盘，便于定位
        try:
            err_path = Path(__file__).resolve().parents[1] / "data" / "train_probability_model_last_error.json"
            err_path.parent.mkdir(parents=True, exist_ok=True)
            with open(err_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "error_type": type(e).__name__,
                        "message": str(e),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass
        raise

    # 训练成功后也写一份轻量落盘信息
    try:
        ok_path = Path(__file__).resolve().parents[1] / "data" / "train_probability_model_last_ok.json"
        with open(ok_path, "w", encoding="utf-8") as f:
            json.dump({"version": out.get("version"), "temperature_t1": out.get("temperature_t1"), "temperature_t5": out.get("temperature_t5")}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

