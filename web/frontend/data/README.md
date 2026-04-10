# Static prediction data (no running backend)

These JSON files are served alongside `index.html` (same origin). The UI loads them instead of `http://localhost:5000/api/...`.

## Files

| File | Description |
|------|-------------|
| `manifest.json` | Build metadata: `generated_at` (ISO-8601 UTC), `source`, `days`, `include_evaluation`, `success` (from last export). |
| `predict_history_100.json` | Same shape as `GET /api/predict/history?days=100&include_evaluation=true`: `{ success, data, metadata, error }`. `metadata.evaluation` holds T1/T5 calibration metrics when samples are sufficient. |
| `static-data.js` | Injected before the app: sets `window.__STATIC_PREDICT_HISTORY__`, `window.__STATIC_MANIFEST__`, `window.__STATIC_RISK_HISTORY__`. **Required for `file://`** (browsers block `fetch` of local JSON from a null origin). |
| `risk_history_sample.json` | Same shape as `GET /api/risk/history?days=10`: `{ success, data, metadata, error }`. Used by legacy test HTML pages. |

## Regenerate

From repo root (requires network for Eastmoney once per run):

```bash
python tools/export_static_predict_history.py
```

Optional: `python tools/export_static_predict_history.py --days 100`

## Override data directory

Open the app with a query param, e.g. `index.html?data=/your/static/path` (no trailing slash required). The UI fetches `{data}/predict_history_100.json` when served over **http(s)**. For `file://`, load `static-data.js` from the same folder as `index.html` (run the export script to refresh it).

## Serving

Use any static HTTP server or internal IIS/Nginx root pointing at `web/frontend/`. Opening via `file://` may block `fetch()` of local JSON; prefer HTTP.
