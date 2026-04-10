# -*- coding: utf-8 -*-
"""Embed web/frontend/data/predict_history_100.json into JS shims for file:// hosting."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def esc_json(s: str) -> str:
    return s.replace("</", "<\\/")


def _verify_js_file(path: Path) -> None:
    raw = path.read_bytes()
    if b"\x00" in raw:
        raise RuntimeError(f"output appears binary/corrupted: {path}")
    text = raw.decode("utf-8")
    if "window.__STATIC_PREDICT_HISTORY__ =" not in text:
        raise RuntimeError(f"output missing window assignment: {path}")


def main() -> int:
    root = _repo_root()
    json_path = root / "web" / "frontend" / "data" / "predict_history_100.json"
    out_paths = [
        root / "web" / "frontend" / "data" / "static-data.js",
        root / "web" / "frontend" / "data" / "static-data.generated.js",
        root / "web" / "frontend" / "data" / "predict-history.embed.js",
        root / "web" / "frontend" / "data" / "predict-history.embed.txt",
        root / "web" / "frontend" / "predict-history.embed.js",
        root / "web" / "frontend" / "predict-history.embed.txt",
        root / "src" / "frontend" / "public" / "data" / "static-data.js",
        root / "src" / "frontend" / "public" / "data" / "static-data.generated.js",
        root / "src" / "frontend" / "public" / "data" / "predict-history.embed.js",
        root / "src" / "frontend" / "public" / "data" / "predict-history.embed.txt",
    ]
    if not json_path.is_file():
        print(f"missing: {json_path}", file=sys.stderr)
        return 2
    with open(json_path, "r", encoding="utf-8") as f:
        predict_result = json.load(f)
    data = predict_result.get("data") or []
    if len(data) < 1:
        print("predict_history_100.json has empty data", file=sys.stderr)
        return 2
    metadata = predict_result.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    metadata["total_days"] = len(data)
    metadata.setdefault("requested_days", 100)
    metadata.setdefault("embedded_source", "tools/sync_static_data_from_json.py")
    predict_result["metadata"] = metadata
    pj = esc_json(json.dumps(predict_result, ensure_ascii=False))
    content = (
        "// UTF-8 text only. Do not open/save as Excel or other binary tools.\n"
        "//\n"
        "// Embedded payload for static/`file://` when fetch(predict_history_100.json) fails.\n"
        "// Synced from web/frontend/data/predict_history_100.json — regenerate:\n"
        "//   python tools/sync_static_data_from_json.py\n"
        "\n"
        f"window.__STATIC_PREDICT_HISTORY__ = {pj};\n"
        "window.__STATIC_MANIFEST__ = null;\n"
        "window.__STATIC_RISK_HISTORY__ = null;\n"
    )
    for out_path in out_paths:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        tmp_path.replace(out_path)
        _verify_js_file(out_path)
        print(f"wrote {out_path} (data rows={len(data)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
