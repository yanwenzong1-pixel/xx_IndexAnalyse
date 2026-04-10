# Tier A/B 重构架构说明

## 入口

- **后端**：仓库根目录 `main.py` → `src/backend/main.py`（Flask 蓝图）。
- **前端**：`src/frontend`（React + Vite），`npm run dev` / `npm run build`。

## 历史预测 / 校准 API

- `GET /api/predict/history` — 参数 `days`, `include_evaluation`, `include_factors`（布尔解析与 legacy 一致）。
- `GET /api/predict/history/summary`
- `GET /api/risk/history`
- `GET /api/risk/current`

实现：`src/backend/api/predict_history_api.py`，业务经 `src/backend/service/micro_cap_legacy_bridge.py` 调用 **`web/backend`** 下的 `analyzer` 与 `utils/*`（算法源码暂留 legacy 目录，避免重复维护两份大文件；入口与路由已统一在 `src/backend`）。

## 静态离线数据

- 脚本：`tools/export_static_predict_history.py`
- 输出：`src/frontend/public/data/*`（`predict_history_100.json`, `manifest.json`, `risk_history_sample.json`, `static-data.js`）

## 遗留

- `web/backend/simple_app.py`：不再作为推荐启动方式；能力已映射到 `main.py` 注册的蓝图中。
- `web/frontend/index.html`（inline Babel）：功能已迁移至 `src/frontend`；保留作历史对照。
