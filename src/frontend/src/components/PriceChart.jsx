import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as echarts from 'echarts';

const PriceChart = ({ data, forceRefreshKey }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const dataRef = useRef(null);
  const [chartKey, setChartKey] = useState(0);
  const isMounted = useRef(false);

  const validateData = useCallback((d) => {
    if (!d || !Array.isArray(d) || d.length === 0) return false;
    return d.some(
      (item) =>
        item &&
        typeof item === 'object' &&
        item.date &&
        typeof item.close === 'number' &&
        !Number.isNaN(item.close) &&
        Number.isFinite(item.close)
    );
  }, []);

  const calculateMA = useCallback((d, period) => {
    const ma = [];
    for (let i = 0; i < d.length; i++) {
      if (i >= period - 1) {
        let sum = 0;
        for (let j = 0; j < period; j++) sum += d[i - j].close;
        ma.push(parseFloat((sum / period).toFixed(2)));
      } else {
        ma.push(null);
      }
    }
    return ma;
  }, []);

  const renderChart = useCallback(() => {
    if (!chartRef.current || !data || !validateData(data)) return false;
    try {
      if (dataRef.current?.length > 0 && data.length > 0) {
        const first1 = dataRef.current[0]?.date;
        const last1 = dataRef.current[dataRef.current.length - 1]?.date;
        const first2 = data[0]?.date;
        const last2 = data[data.length - 1]?.date;
        if (first1 === first2 && last1 === last2) return true;
      }
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
      }
      dataRef.current = data;
      chartInstance.current = echarts.init(chartRef.current);
      const dates = data.map((item) => item.date);
      const closePrices = data.map((item) => item.close);
      const ma5 = calculateMA(data, 5);
      const ma20 = calculateMA(data, 20);
      const validPrices = closePrices.filter((p) => p !== null && !Number.isNaN(p));
      const minPrice = Math.min(...validPrices);
      const maxPrice = Math.max(...validPrices);
      const padding = (maxPrice - minPrice) * 0.1 || 10;
      chartInstance.current.setOption(
        {
          title: {
            text: '微盘股指数价格走势',
            left: 'center',
            textStyle: { fontSize: 14, fontWeight: 'normal' },
          },
          tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
          legend: { data: ['收盘价', 'MA5', 'MA20'], top: 30 },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: 80,
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: dates,
            axisLabel: {
              rotate: 0,
              fontSize: 10,
              interval: Math.floor(dates.length / 10),
            },
          },
          yAxis: {
            type: 'value',
            min: minPrice - padding,
            max: maxPrice + padding,
            axisLabel: {
              formatter: (value) => value.toFixed(2),
              color: '#000000',
            },
          },
          series: [
            {
              name: '收盘价',
              type: 'line',
              data: closePrices,
              smooth: true,
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: { width: 2, color: '#3b82f6' },
              areaStyle: { color: 'rgba(59, 130, 246, 0.1)' },
            },
            {
              name: 'MA5',
              type: 'line',
              data: ma5,
              smooth: true,
              symbol: 'none',
              lineStyle: {
                width: 1.5,
                color: '#10b981',
                type: 'dashed',
              },
            },
            {
              name: 'MA20',
              type: 'line',
              data: ma20,
              smooth: true,
              symbol: 'none',
              lineStyle: {
                width: 1.5,
                color: '#f59e0b',
                type: 'dotted',
              },
            },
          ],
        },
        true
      );
      return true;
    } catch (e) {
      console.error('图表渲染失败:', e);
      return false;
    }
  }, [data, validateData, calculateMA]);

  const forceRefresh = useCallback(() => {
    if (chartInstance.current) {
      chartInstance.current.dispose();
      chartInstance.current = null;
    }
    setChartKey((p) => p + 1);
    setTimeout(() => renderChart(), 100);
  }, [renderChart]);

  useEffect(() => {
    if (forceRefreshKey !== undefined) forceRefresh();
  }, [forceRefreshKey, forceRefresh]);

  useEffect(() => {
    if (!isMounted.current) isMounted.current = true;
    const rafId = requestAnimationFrame(() => renderChart());
    const resizeHandler = () => chartInstance.current?.resize();
    window.addEventListener('resize', resizeHandler);
    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resizeHandler);
    };
  }, [renderChart]);

  useEffect(
    () => () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
        dataRef.current = null;
      }
    },
    []
  );

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div
        key={chartKey}
        ref={chartRef}
        style={{ width: '100%', height: '400px' }}
      />
    </div>
  );
};

export default PriceChart;
