# 静态前端部署（无常驻后端）

## 发布内容（Tier A/B 主路径）

构建并部署 **`src/frontend`** 的产物（推荐 `npm run build` 后的 `dist/`），或对整个前端目录做 HTTP 静态托管。

- **开发**：`cd src/frontend && npm install && npm run dev`（Vite 默认将 `/api` 代理到 `http://127.0.0.1:5000`）。
- **主页面**：构建后为 `dist/index.html`。
- **K 线**：仍可由浏览器请求东方财富 JSONP（受网络策略影响）。
- **历史下跌概率与校准**：来自 `public/data/predict_history_100.json` 或同结构的 `/api/predict/history`。

遗留目录 `web/frontend/`（inline Babel）不再作为推荐入口，仅保留作对照。

## 生成数据文件

在**可联网且允许运行 Python 一次**的环境（仓库根目录）执行：

```bash
pip install -r requirements.txt
python tools/export_static_predict_history.py
```

可选：`python tools/export_static_predict_history.py --days 100`

输出写入 **`src/frontend/public/data/`**：

- `predict_history_100.json` — 与 `GET /api/predict/history?days=100&include_evaluation=true` 同结构
- `static-data.js` — 注入 `window.__STATIC_*`，用于 `file://` 规避对本地 JSON 的 fetch 限制
- `risk_history_sample.json`、`manifest.json`

构建时 Vite 会将 `public/` 原样拷贝到 `dist/`，故静态托管只需更新 `dist/data/*` 即可。

## 自定义数据目录（HTTP 模式）

页面查询参数：`?data=/your/path`（无尾部斜杠亦可），将请求 `{data}/predict_history_100.json` 与 `{data}/manifest.json`。**file:// 模式仍建议依赖 `static-data.js`。**

## 注意

- `file://`：请保留由导出脚本生成的 `static-data.js`。
- 推荐以 HTTP(S) 访问，便于单独更新 JSON。
- 占位 JSON（`success: false`）部署前请替换为导出结果。
