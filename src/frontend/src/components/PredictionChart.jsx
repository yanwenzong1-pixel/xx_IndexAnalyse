import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

/** 根据实际概率序列（0–100）计算 Y 轴范围，留出上下边距并夹在 [0,100]。 */
function computeProbabilityYAxisRange(values) {
  const vals = values.filter((v) => typeof v === 'number' && Number.isFinite(v));
  if (!vals.length) return { min: 0, max: 100 };
  const vmin = Math.min(...vals);
  const vmax = Math.max(...vals);
  const span = Math.max(vmax - vmin, 1e-6);
  const pad = Math.max(span * 0.12, 0.5);
  let min = vmin - pad;
  let max = vmax + pad;
  min = Math.max(0, min);
  max = Math.min(100, max);
  if (max - min < 2) {
    const mid = (vmin + vmax) / 2;
    min = Math.max(0, mid - 1);
    max = Math.min(100, mid + 1);
    if (max <= min) max = Math.min(100, min + 2);
  }
  return { min, max };
}

const PredictionChart = ({ data, type, title, color = '#ef4444' }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!chartRef.current || !data?.length) return;

    if (chartInstance.current) {
      chartInstance.current.dispose();
    }

    const dates = data.map((item) => {
      const [y, m, d] = item.date.split('-');
      return `${m}-${d}`;
    });
    const probabilities = data.map((item) => item[type]);
    const yAxisRange = computeProbabilityYAxisRange(probabilities);

    chartInstance.current = echarts.init(chartRef.current);

    const option = {
      title: {
        text: title,
        left: 'center',
        textStyle: { fontSize: 12, fontWeight: 'normal' },
      },
      tooltip: {
        trigger: 'axis',
        formatter(params) {
          const first = Array.isArray(params) ? params[0] : null;
          if (!first) return '';
          const idx = Number.isInteger(first.dataIndex) ? first.dataIndex : -1;
          const fullDate = idx >= 0 && data[idx]?.date ? data[idx].date : first.axisValue;
          return `日期: ${fullDate}<br/>下跌概率: ${first.value}%`;
        },
      },
      grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        top: 30,
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLabel: {
          fontSize: 8,
          interval: Math.floor(dates.length / 10),
        },
      },
      yAxis: {
        type: 'value',
        min: yAxisRange.min,
        max: yAxisRange.max,
        scale: true,
        splitNumber: 4,
        axisLabel: {
          fontSize: 8,
          formatter(v) {
            return `${Number(v).toFixed(1)}%`;
          },
        },
      },
      series: [
        {
          name: '下跌概率',
          type: 'line',
          data: probabilities,
          smooth: true,
          lineStyle: { width: 1.2, color },
          itemStyle: { color },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: `${color}4D` },
              { offset: 1, color: `${color}1A` },
            ]),
          },
          symbol: 'none',
        },
      ],
    };

    chartInstance.current.setOption(option);
    const onResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, [data, type, title, color]);

  return (
    <div ref={chartRef} style={{ width: '100%', height: '100%', minHeight: 180 }} />
  );
};

export default PredictionChart;
