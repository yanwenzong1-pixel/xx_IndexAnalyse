"""Contract tests for /api/predict/history (evaluation fields)."""
from __future__ import annotations

from unittest.mock import patch


def test_predict_history_evaluation_shape():
    from backend.main import create_app

    sample = {
        "success": True,
        "data": [{"date": "2024-01-02", "prob_t1": 0.4, "prob_t5": 0.45}],
        "metadata": {
            "total_days": 1,
            "evaluation": {
                "t1_brier": 0.1,
                "t1_event_rate": 0.5,
                "t1_pred_mean": 0.46,
                "t1_bias": -0.04,
                "t1_logloss": 0.2,
                "t1_ece": 0.05,
                "calibration_status_t1": "normal",
                "calibration_alert_level_t1": "none",
                "t1_reliability_bins": [
                    {"pred_mean": 0.4, "obs_rate": 0.3, "count": 10}
                ],
                "t5_brier": 0.11,
                "t5_event_rate": 0.4,
                "t5_pred_mean": 0.36,
                "t5_bias": -0.04,
                "t5_logloss": 0.21,
                "t5_ece": 0.06,
                "calibration_status_t5": "normal",
                "calibration_alert_level_t5": "none",
                "t5_reliability_bins": [],
            },
        },
        "error": None,
    }

    app = create_app()
    with patch(
        "backend.api.predict_history_api.predict_history_payload",
        return_value=sample,
    ):
        c = app.test_client()
        r = c.get("/api/predict/history?days=100&include_evaluation=true")
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        ev = body["metadata"]["evaluation"]
        assert "t1_ece" in ev and "t5_ece" in ev
        assert "t1_pred_mean" in ev and "t5_pred_mean" in ev
        assert "t1_bias" in ev and "t5_bias" in ev
        assert ev["calibration_status_t1"] in ("normal", "underestimate", "overestimate")
        assert ev["calibration_status_t5"] in ("normal", "underestimate", "overestimate")
        assert ev["calibration_alert_level_t1"] in ("none", "yellow", "red")
        assert ev["calibration_alert_level_t5"] in ("none", "yellow", "red")
        assert isinstance(ev["t1_reliability_bins"], list)
