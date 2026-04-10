# API 文档

## 基础信息

- **Base URL**: `/api`
- **格式**: JSON
- **CORS**: 已启用

---

## 数据接口

### GET /api/data

获取股票数据

**响应示例**:
```json
{
  "success": true,
  "message": "成功",
  "data": {
    "latest": {
      "date": "2024-03-06",
      "close": 1500.0,
      "change_pct": 2.5,
      "amount": 1000000000,
      "turnover": 5.2
    },
    "history": [
      {
        "date": "2024-03-05",
        "close": 1463.5,
        "change_pct": -1.2
      }
    ]
  }
}
```

### POST /api/refresh

刷新数据

**响应示例**:
```json
{
  "success": true,
  "message": "刷新成功"
}
```

---

## 指标接口

### GET /api/indicators

获取 5 大维度指标

**响应示例**:
```json
{
  "success": true,
  "data": {
    "liquidity": {
      "amount_to_market_cap": 0.2,
      "avg_turnover_5d": 5.0
    },
    "fund_structure": {...},
    "valuation": {...},
    "policy": {...},
    "macro": {...}
  }
}
```

---

## 风险接口

### GET /api/risk

获取风险评估

**响应示例**:
```json
{
  "success": true,
  "data": {
    "risk_level": 5.5,
    "risk_level_text": "中等风险",
    "downside_probability": 0.45,
    "alert": false,
    "decline": {
      "t1": {
        "expected_decline": 3.5,
        "lower_bound": 2.5,
        "upper_bound": 5.5
      }
    }
  }
}
```

### GET /api/risk/current

获取当前风险打分（快速接口，风险趋势主入口之一）

**字段契约**:
- `risk_score`：`number`，统一保留两位小数语义（例如 `5.00`）
- `risk_level`：`low|medium|high|very_high`
- `source`：数据来源标识，固定为 `backend-live`
- `version`：风险趋势输出版本，固定为 `risk-v2-2dp`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "date": "2026-04-10",
    "risk_score": 5.00,
    "risk_level": "medium",
    "source": "backend-live",
    "version": "risk-v2-2dp"
  }
}
```

### GET /api/risk/history

获取历史风险趋势数据（前端风险趋势图权威数据源）

**Query 参数**:
- `days`：回溯天数（1-300，默认 300）

**字段契约**:
- `data[].risk_score`：`number`，统一保留两位小数语义
- `data[].source`：单条来源标识，固定为 `backend-live`
- `metadata.source`：数据集来源标识，固定为 `backend-live`
- `metadata.version`：风险趋势输出版本，固定为 `risk-v2-2dp`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2026-04-08",
      "risk_score": 4.75,
      "risk_level": "low",
      "source": "backend-live"
    },
    {
      "date": "2026-04-09",
      "risk_score": 5.10,
      "risk_level": "medium",
      "source": "backend-live"
    }
  ],
  "metadata": {
    "total_days": 300,
    "avg_risk": 5.23,
    "max_risk": 8.40,
    "min_risk": 2.90,
    "current_risk": 5.10,
    "risk_trend": "stable",
    "source": "backend-live",
    "version": "risk-v2-2dp"
  }
}
```

---

## 预测历史与校准接口

### GET /api/predict/history

获取近 N 日预测结果；可选返回校准评估信息。

**Query 参数**:
- `days`：回溯天数（1-252，默认 100）
- `include_evaluation`：是否返回 `metadata.evaluation`（`true/false`）

**响应示例（含校准）**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2026-04-03",
      "prob_t1": 0.2556,
      "prob_t5": 0.3371
    }
  ],
  "metadata": {
    "total_days": 100,
    "prob_model_params_version": 1,
    "temperature_t1": 1.0,
    "temperature_t5": 1.0,
    "evaluation": {
      "t1_event_rate": 0.4242,
      "t1_pred_mean": 0.2223,
      "t1_bias": -0.2019,
      "t1_ece": 0.2019,
      "calibration_status_t1": "underestimate",
      "calibration_alert_level_t1": "red",
      "t5_event_rate": 0.3894,
      "t5_pred_mean": 0.2625,
      "t5_bias": -0.1269,
      "t5_ece": 0.1679,
      "calibration_status_t5": "underestimate",
      "calibration_alert_level_t5": "red"
    }
  },
  "error": null
}
```

### 校准字段口径

- `*_pred_mean`：该窗口下模型概率均值
- `*_bias`：`pred_mean - event_rate`（负值表示低估，正值表示高估）
- `calibration_status_*`：
  - `normal`：`abs(bias) <= 0.05 && ece <= 0.08`
  - `underestimate`：`bias < -0.05`
  - `overestimate`：`bias > 0.05`
- `calibration_alert_level_*`：
  - `yellow`：`ece > 0.10`
  - `red`：`ece > 0.15` 或 `abs(bias) > 0.12`
  - `none`：其余情况

### 前端展示建议

- 卡片概率值必须与趋势图最后一点一致，禁止硬编码静态值。
- 出现 `yellow/red` 告警时，文案应提示“以趋势信号为主，降低绝对概率权重”。

### 手工验收清单（预测与校准）

**HTTP 静态数据模式**（通过本地服务器打开 `web/frontend`，可加载 `predict_history_100.json`）

1. 清空浏览器 `localStorage` 中 `predictionData`、`predictionDataEvaluation`、`predictionDataTimestamp` 后强刷页面。
2. 确认「下跌风险预测」卡片中 T+1、T+5 概率与各自趋势图最后一个点一致（数值与走势末端对齐）。
3. 确认校准区展示 `pred_mean`、`event_rate`、`ECE`，以及「偏低估/偏高估/正常」与「黄/红告警」标签与导出 JSON 一致。
4. 点击「导出校准诊断」，确认 JSON 中含 `pred_mean`、`bias`、`ece`、`reliability_bins`，且在后端返回时含 `calibration_status`、`calibration_alert_level`。

**file:// 模式**（仅 `static-data.js` 注入）

1. 运行 `tools/export_static_predict_history.py` 生成或更新 `data/static-data.js`，确保内含 `metadata.evaluation`。
2. 用 `file://` 打开页面，确认预测区能加载；若更新了 manifest 时间戳，确认旧缓存被丢弃（卡片与注入数据一致）。
3. 重复 HTTP 模式步骤 2–4（导出依赖注入的 evaluation 字段）。

---

## 报告接口

### GET /api/report

获取每日报告

**响应示例**:
```json
{
  "success": true,
  "data": {
    "report": "微盘股指数每日监控报告..."
  }
}
```

---

## 健康检查

### GET /api/health

服务健康检查

**响应示例**:
```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```

---

## 错误响应

### 通用错误格式

```json
{
  "success": false,
  "message": "错误消息",
  "error_code": "ERROR_CODE"
}
```

### 常见错误码

- `DATA_FETCH_ERROR`: 数据获取失败
- `DATA_EMPTY`: 数据为空
- `REFRESH_ERROR`: 刷新失败
- `INTERNAL_ERROR`: 内部错误

---

**版本**: 2.0  
**更新日期**: 2026-03-19
