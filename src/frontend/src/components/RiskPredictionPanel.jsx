import React, { useEffect, useState } from 'react';
import PredictionChart from './PredictionChart.jsx';
import {
  IS_FILE,
  PREDICT_HISTORY_DAYS,
  loadManifest,
  loadPredictHistoryData,
} from '../lib/predictHistorySource.js';

function escapeHtml(text) {
  if (text == null) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function levelForProb(pct) {
  if (pct < 30) return { label: '较低', cls: 'bg-green-100 dark:bg-green-900 text-green-700' };
  if (pct < 50)
    return { label: '中等', cls: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-600' };
  if (pct < 70)
    return { label: '较高', cls: 'bg-orange-100 dark:bg-orange-900 text-orange-600' };
  return { label: '高', cls: 'bg-red-100 dark:bg-red-900 text-red-600' };
}

function evaluateCalibrationStatus(bias, ece) {
  if (!Number.isFinite(bias) || !Number.isFinite(ece)) return 'unknown';
  if (Math.abs(bias) <= 0.05 && ece <= 0.08) return 'normal';
  if (bias < -0.05) return 'underestimate';
  if (bias > 0.05) return 'overestimate';
  return 'normal';
}

function calibrationStyle(status) {
  if (status === 'underestimate') {
    return { label: '偏低估', cls: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300' };
  }
  if (status === 'overestimate') {
    return { label: '偏高估', cls: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300' };
  }
  if (status === 'normal') {
    return { label: '正常', cls: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300' };
  }
  return { label: '未知', cls: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300' };
}

function evaluationLooksComplete(ev) {
  return (
    ev &&
    typeof ev === 'object' &&
    (ev.t1_ece !== undefined || ev.t1_event_rate !== undefined)
  );
}

function alertStyle(level) {
  if (level === 'red') {
    return { label: '红色告警', cls: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300' };
  }
  if (level === 'yellow') {
    return { label: '黄色告警', cls: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300' };
  }
  return { label: '无告警', cls: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300' };
}

export default function RiskPredictionPanel() {
  const CACHE_KEYS = {
    data: 'predictionDataV2',
    evaluation: 'predictionDataEvaluationV2',
    timestamp: 'predictionDataTimestampV2',
    meta: 'predictionDataMetaV2',
  };
  const [predictionData, setPredictionData] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [predictMeta, setPredictMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalError, setEvalError] = useState(null);
  const [staticManifest, setStaticManifest] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const m = await loadManifest();
      if (!cancelled && m) setStaticManifest(m);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const cached = localStorage.getItem(CACHE_KEYS.data);
        const ts = localStorage.getItem(CACHE_KEYS.timestamp);
        const cachedEvaluation = localStorage.getItem(CACHE_KEYS.evaluation);
        const cachedMeta = localStorage.getItem(CACHE_KEYS.meta);
        const manifestTimeMs = staticManifest?.generated_at
          ? Date.parse(String(staticManifest.generated_at))
          : NaN;
        if (cached && ts) {
          const hours = (Date.now() - parseInt(ts, 10)) / (1000 * 60 * 60);
          // file:// 静态模式下，若 manifest 比缓存新，必须强制丢弃缓存避免“看起来不更新”
          const cacheMs = parseInt(ts, 10);
          const cacheIsOlderThanManifest =
            IS_FILE &&
            Number.isFinite(manifestTimeMs) &&
            Number.isFinite(cacheMs) &&
            manifestTimeMs > cacheMs;
          if (hours < 24 && !cacheIsOlderThanManifest) {
            let parsedEv = null;
            let parsedMeta = null;
            try {
              parsedEv = cachedEvaluation ? JSON.parse(cachedEvaluation) : null;
            } catch (_) {
              parsedEv = null;
            }
            try {
              parsedMeta = cachedMeta ? JSON.parse(cachedMeta) : null;
            } catch (_) {
              parsedMeta = null;
            }
            let series = JSON.parse(cached);
            let ev = evaluationLooksComplete(parsedEv) ? parsedEv : null;
            let meta =
              parsedMeta &&
              typeof parsedMeta === 'object' &&
              Number.isFinite(parsedMeta.expectedDays) &&
              Number.isFinite(parsedMeta.actualDays)
                ? parsedMeta
                : {
                    source: 'cache-legacy',
                    expectedDays: PREDICT_HISTORY_DAYS,
                    actualDays: Array.isArray(series) ? series.length : 0,
                    isPartial:
                      !Array.isArray(series) ||
                      series.length < PREDICT_HISTORY_DAYS,
                  };

            if (
              Array.isArray(series) &&
              series.length > 0 &&
              meta.actualDays < PREDICT_HISTORY_DAYS
            ) {
              const payload = await loadPredictHistoryData();
              if (payload && payload.actualDays > series.length) {
                series = payload.series;
                ev = payload.evaluation ?? ev;
                meta = {
                  source: payload.source,
                  expectedDays: payload.expectedDays,
                  actualDays: payload.actualDays,
                  isPartial: payload.isPartial,
                };
                try {
                  localStorage.setItem(CACHE_KEYS.data, JSON.stringify(series));
                  localStorage.setItem(CACHE_KEYS.timestamp, String(Date.now()));
                  localStorage.setItem(
                    CACHE_KEYS.evaluation,
                    JSON.stringify(ev ?? null)
                  );
                  localStorage.setItem(CACHE_KEYS.meta, JSON.stringify(meta));
                } catch (_) {}
              }
            }
            if (!evaluationLooksComplete(ev)) {
              const payload = await loadPredictHistoryData();
              const fromRaw = payload?.evaluation ?? null;
              if (evaluationLooksComplete(fromRaw)) {
                ev = fromRaw;
                try {
                  localStorage.setItem(
                    CACHE_KEYS.evaluation,
                    JSON.stringify(ev)
                  );
                } catch (_) {}
              }
            }
            setPredictionData(series);
            setEvaluation(ev);
            setPredictMeta(meta);
            if (meta.isPartial) {
              setError(
                `当前仅加载到 ${meta.actualDays}/${meta.expectedDays} 个交易日预测数据。` +
                  '如在 file:// 模式下，请执行 python tools/sync_static_data_from_json.py 后刷新。'
              );
            }
            setLoading(false);
            return;
          }
        }
        const payload = await loadPredictHistoryData();
        if (payload && payload.actualDays > 0) {
          setPredictionData(payload.series);
          setEvaluation(payload.evaluation ?? null);
          setPredictMeta({
            source: payload.source,
            expectedDays: payload.expectedDays,
            actualDays: payload.actualDays,
            isPartial: payload.isPartial,
          });
          localStorage.setItem(CACHE_KEYS.data, JSON.stringify(payload.series));
          localStorage.setItem(
            CACHE_KEYS.evaluation,
            JSON.stringify(payload.evaluation ?? null)
          );
          localStorage.setItem(CACHE_KEYS.timestamp, String(Date.now()));
          localStorage.setItem(
            CACHE_KEYS.meta,
            JSON.stringify({
              source: payload.source,
              expectedDays: payload.expectedDays,
              actualDays: payload.actualDays,
              isPartial: payload.isPartial,
            })
          );
          if (payload.isPartial) {
            setError(
              `当前仅加载到 ${payload.actualDays}/${payload.expectedDays} 个交易日预测数据。` +
                '如在 file:// 模式下，请执行 python tools/sync_static_data_from_json.py 后刷新。'
            );
          }
        } else {
          setPredictionData(null);
          setEvaluation(null);
          setPredictMeta(null);
          setError(
            IS_FILE
              ? 'file:// 下请运行 python tools/sync_static_data_from_json.py 或 export_static_predict_history.py 写入 static-data.js 后刷新。'
              : '无法加载预测数据：请启动后端 (python main.py) 或生成静态 JSON。'
          );
        }
      } catch (e) {
        console.error(e);
        setPredictionData(null);
        setEvaluation(null);
        setPredictMeta(null);
        setError(e.message || '加载失败');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [staticManifest?.generated_at]);

  const handleExportEvaluation = async () => {
    setEvalLoading(true);
    setEvalError(null);
    let w = null;
    let exportStage = 'init';
    try {
      exportStage = 'popup';
      w = window.open('', '_blank');
      if (!w) throw new Error('浏览器拦截了弹窗，请允许弹出窗口后重试。');
      exportStage = 'fetch';
      const payload = await loadPredictHistoryData();
      const result = payload?.raw || null;
      if (!result) {
        throw new Error('无法加载历史预测 payload。');
      }
      const evaluation = result?.metadata?.evaluation;
      if (!result?.success || !evaluation) {
        throw new Error(
          'metadata.evaluation 缺失。请重新运行 export 脚本或请求 include_evaluation=true 的接口。'
        );
      }
      const extractBlock = (prefix) => {
        const out = {};
        [
          'event_rate',
          'pred_mean',
          'bias',
          'brier',
          'logloss',
          'ece',
          'reliability_bins',
        ].forEach((k) => {
          const fn = `${prefix}_${k}`;
          if (evaluation[fn] !== undefined) out[k] = evaluation[fn];
        });
        return out;
      };
      const exportPayload = {
        t1: {
          ...extractBlock('t1'),
          ...(evaluation.calibration_status_t1 !== undefined && {
            calibration_status: evaluation.calibration_status_t1,
          }),
          ...(evaluation.calibration_alert_level_t1 !== undefined && {
            calibration_alert_level: evaluation.calibration_alert_level_t1,
          }),
        },
        t5: {
          ...extractBlock('t5'),
          ...(evaluation.calibration_status_t5 !== undefined && {
            calibration_status: evaluation.calibration_status_t5,
          }),
          ...(evaluation.calibration_alert_level_t5 !== undefined && {
            calibration_alert_level: evaluation.calibration_alert_level_t5,
          }),
        },
      };
      const jsonText = JSON.stringify(exportPayload, null, 2);
      exportStage = 'write';
      const safe = escapeHtml(jsonText);
      w.document.open();
      w.document.write(
        `<!DOCTYPE html><html><head><meta charset="utf-8"><title>prediction evaluation</title></head>` +
          `<body style="font-family:monospace;padding:16px">` +
          `<h2 style="margin:0 0 12px 0">校准诊断（evaluation: t1 + t5）</h2>` +
          `<textarea readonly style="width:100%;height:90vh">${safe}</textarea>` +
          `</body></html>`
      );
      w.document.close();
    } catch (err) {
      if (w && !w.closed) {
        try {
          w.document.open();
          w.document.write(
            `<body style="font-family:monospace;padding:16px"><h2>导出失败</h2><pre>${escapeHtml(
              err?.message || String(err)
            )}</pre></body>`
          );
          w.document.close();
        } catch (_) {}
      }
      setEvalError(`[${exportStage}] ${err?.message || '导出失败'}`);
    } finally {
      setEvalLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-xl font-bold animate-pulse">加载预测数据中...</div>
      </div>
    );
  }

  if (!predictionData) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
        <div className="text-center py-12">
          <div className="text-red-500 text-xl font-bold mb-2">数据加载失败</div>
          <div className="text-gray-600 dark:text-gray-400 text-sm">
            {error || '未知错误'}
          </div>
        </div>
      </div>
    );
  }

  const last = predictionData[predictionData.length - 1];
  const trendPointCount = predictionData.length;
  const t1 = last?.t1Prob ?? 0;
  const t5 = last?.t5Prob ?? 0;
  const t1Lv = levelForProb(t1);
  const t5Lv = levelForProb(t5);
  const t1PredMean =
    Number.isFinite(evaluation?.t1_pred_mean)
      ? evaluation.t1_pred_mean
      : Number.isFinite(evaluation?.t1_reliability_bins?.[0]?.pred_mean)
      ? evaluation.t1_reliability_bins[0].pred_mean
      : NaN;
  const t1EventRate = Number.isFinite(evaluation?.t1_event_rate) ? evaluation.t1_event_rate : NaN;
  const t1Ece = Number.isFinite(evaluation?.t1_ece) ? evaluation.t1_ece : NaN;
  const t1Bias =
    Number.isFinite(evaluation?.t1_bias) ? evaluation.t1_bias : t1PredMean - t1EventRate;
  const t1Status = calibrationStyle(
    evaluation?.calibration_status_t1 || evaluateCalibrationStatus(t1Bias, t1Ece)
  );
  const t1Alert = alertStyle(evaluation?.calibration_alert_level_t1 || 'none');

  const t5PredMean =
    Number.isFinite(evaluation?.t5_pred_mean)
      ? evaluation.t5_pred_mean
      : Number.isFinite(evaluation?.t5_reliability_bins?.[0]?.pred_mean)
      ? evaluation.t5_reliability_bins[0].pred_mean
      : NaN;
  const t5EventRate = Number.isFinite(evaluation?.t5_event_rate) ? evaluation.t5_event_rate : NaN;
  const t5Ece = Number.isFinite(evaluation?.t5_ece) ? evaluation.t5_ece : NaN;
  const t5Bias =
    Number.isFinite(evaluation?.t5_bias) ? evaluation.t5_bias : t5PredMean - t5EventRate;
  const t5Status = calibrationStyle(
    evaluation?.calibration_status_t5 || evaluateCalibrationStatus(t5Bias, t5Ece)
  );
  const t5Alert = alertStyle(evaluation?.calibration_alert_level_t5 || 'none');
  const manifestTimeMs = staticManifest?.generated_at
    ? Date.parse(String(staticManifest.generated_at))
    : NaN;
  const manifestAgeHours = Number.isFinite(manifestTimeMs)
    ? (Date.now() - manifestTimeMs) / (1000 * 60 * 60)
    : null;
  const staticIsStale = IS_FILE && (manifestAgeHours == null || manifestAgeHours > 12);
  const modelVersion = staticManifest?.prob_model_params_version;
  const t1Temp = staticManifest?.temperature_t1;
  const t5Temp = staticManifest?.temperature_t5;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
      <div className="flex items-center mb-6">
        <h3 className="text-xl font-semibold bg-gradient-to-r from-red-600 to-orange-500 bg-clip-text text-transparent">
          下跌风险预测
        </h3>
        <span className="ml-3 px-3 py-1 bg-gradient-to-r from-red-100 to-orange-100 dark:from-red-900/30 dark:to-orange-900/30 text-red-600 dark:text-red-400 text-xs font-medium rounded-full">
          模型输出
        </span>
      </div>
      {staticManifest?.generated_at && (
        <div className="-mt-4 mb-4 text-xs text-gray-500">
          静态 manifest.generated_at：{String(staticManifest.generated_at)}
        </div>
      )}
      {IS_FILE && (
        <div
          className={`mb-4 rounded-lg p-3 text-xs ${
            staticIsStale
              ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
              : 'bg-green-50 text-green-800 border border-green-200'
          }`}
        >
          <div>
            静态模式校验：
            {staticIsStale
              ? ` 数据可能过期。请运行 tools/export_static_predict_history.py --days ${PREDICT_HISTORY_DAYS} 后刷新页面。`
              : ' 静态数据时间在可接受范围内。'}
          </div>
          <div className="mt-1">
            参数版本：{modelVersion ?? 'unknown'}，temperature_t1：
            {t1Temp ?? 'unknown'}，temperature_t5：{t5Temp ?? 'unknown'}
          </div>
          <div className="mt-1">
            若刚更新参数但图未变化：请清理 localStorage 中 predictionDataV2 / predictionDataEvaluationV2 / predictionDataTimestampV2 / predictionDataMetaV2 并强刷。
          </div>
        </div>
      )}
      {predictMeta?.isPartial && (
        <div className="mb-4 rounded-lg p-3 text-xs border border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
          当前仅加载到 {predictMeta.actualDays}/{predictMeta.expectedDays}{' '}
          个交易日预测数据（source: {predictMeta.source}）。请执行{' '}
          <code>python tools/sync_static_data_from_json.py</code> 后刷新页面。
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/10 rounded-xl p-6 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h4 className="text-lg font-medium">次日（T+1）预测</h4>
            <div className="flex gap-2">
              <button
                type="button"
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg text-sm"
                onClick={handleExportEvaluation}
                disabled={evalLoading}
              >
                {evalLoading ? '导出中...' : '导出校准诊断'}
              </button>
            </div>
          </div>
          {evalError && (
            <div className="mb-4 text-sm text-yellow-700 bg-yellow-50 dark:bg-yellow-900/30 p-2 rounded">
              {evalError}
            </div>
          )}
          <div className="mb-2 text-xs text-gray-500 dark:text-gray-400">
            预测基准日（与趋势图末点一致）：{last?.date || 'N/A'}
          </div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-500 mb-1">下跌概率</div>
              <div className="text-2xl font-bold text-red-600">{t1.toFixed(1)}%</div>
              <div className={`inline-block px-2 py-0.5 text-xs rounded mt-2 ${t1Lv.cls}`}>
                {t1Lv.label}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-500 mb-1">预期跌幅（示意）</div>
              <div className="text-2xl font-bold text-green-600">—</div>
              <div className="text-xs text-gray-400 mt-2">详见后端 decline 模块</div>
            </div>
          </div>
          <div className="h-52 mb-4 bg-white dark:bg-gray-700 rounded-lg p-2">
            <PredictionChart
              data={predictionData}
              type="t1Prob"
              title={`近${trendPointCount}个交易日次日下跌概率`}
              color="#ef4444"
            />
          </div>
          <div className="rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 p-3 text-xs text-gray-600 dark:text-gray-300">
            <div className="mb-2 flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded ${t1Status.cls}`}>{t1Status.label}</span>
              <span className={`px-2 py-0.5 rounded ${t1Alert.cls}`}>{t1Alert.label}</span>
            </div>
            <div>
              校准诊断（T+1）：预测均值 {Number.isFinite(t1PredMean) ? `${(t1PredMean * 100).toFixed(1)}%` : 'N/A'} vs
              实际发生率 {Number.isFinite(t1EventRate) ? `${(t1EventRate * 100).toFixed(1)}%` : 'N/A'}，校准误差（ECE）{' '}
              {Number.isFinite(t1Ece) ? t1Ece.toFixed(3) : 'N/A'}
            </div>
            {(t1Alert.label !== '无告警') && (
              <div className="mt-1">
                当前窗口校准偏差较大，建议以趋势信号为主，降低绝对概率权重。
              </div>
            )}
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/10 rounded-xl p-6 shadow-sm">
          <h4 className="text-lg font-medium mb-6">5日内（T+5）预测</h4>
          <div className="mb-2 text-xs text-gray-500 dark:text-gray-400">
            预测基准日（与趋势图末点一致）：{last?.date || 'N/A'}
          </div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-500 mb-1">下跌概率</div>
              <div className="text-2xl font-bold text-purple-600">{t5.toFixed(1)}%</div>
              <div className={`inline-block px-2 py-0.5 text-xs rounded mt-2 ${t5Lv.cls}`}>
                {t5Lv.label}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-500 mb-1">预期跌幅（示意）</div>
              <div className="text-2xl font-bold text-green-600">—</div>
            </div>
          </div>
          <div className="h-52 mb-4 bg-white dark:bg-gray-700 rounded-lg p-2">
            <PredictionChart
              data={predictionData}
              type="t5Prob"
              title={`近${trendPointCount}个交易日 T+5 下跌概率`}
              color="#8b5cf6"
            />
          </div>
          <div className="rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 p-3 text-xs text-gray-600 dark:text-gray-300">
            <div className="mb-2 flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded ${t5Status.cls}`}>{t5Status.label}</span>
              <span className={`px-2 py-0.5 rounded ${t5Alert.cls}`}>{t5Alert.label}</span>
            </div>
            <div>
              校准诊断（T+5）：预测均值 {Number.isFinite(t5PredMean) ? `${(t5PredMean * 100).toFixed(1)}%` : 'N/A'} vs
              实际发生率 {Number.isFinite(t5EventRate) ? `${(t5EventRate * 100).toFixed(1)}%` : 'N/A'}，校准误差（ECE）{' '}
              {Number.isFinite(t5Ece) ? t5Ece.toFixed(3) : 'N/A'}
            </div>
            {(t5Alert.label !== '无告警') && (
              <div className="mt-1">
                当前窗口校准偏差较大，建议以趋势信号为主，降低绝对概率权重。
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-gray-600">
        风险提示：预测基于历史统计与因子模型，仅供参考，不构成投资建议。
      </div>
    </div>
  );
}
