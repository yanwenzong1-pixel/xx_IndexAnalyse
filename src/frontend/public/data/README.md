# Static data (optional)

- `predict_history_100.json`, `manifest.json`, `risk_history_sample.json`, `static-data.js` — generate with:

```bash
python tools/export_static_predict_history.py
```

Output targets this directory (`src/frontend/public/data/`) for Vite dev and static builds.

For `file://` usage, `static-data.js` injects `window.__STATIC_*` so fetches are not required.
