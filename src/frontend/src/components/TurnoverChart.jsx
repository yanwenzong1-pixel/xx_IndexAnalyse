import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';

const TurnoverChart = ({ data }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [, setIsChartInitialized] = useState(false);

  useEffect(() => {
    if (chartRef.current && data && Array.isArray(data) && data.length > 0) {
      const initChart = () => {
        try {
          if (
            !chartRef.current ||
            chartRef.current.offsetWidth === 0 ||
            chartRef.current.offsetHeight === 0
          ) {
            setTimeout(initChart, 100);
            return;
          }
          if (!chartInstance.current) {
            chartInstance.current = echarts.init(chartRef.current);
            setIsChartInitialized(true);
          }
          const validData = data.filter(
            (item) =>
              item &&
              typeof item === 'object' &&
              item.date &&
              typeof item.turnover === 'number' &&
              typeof item.amount === 'number'
          );
          if (validData.length === 0) throw new Error('无效的图表数据');
          const dates = validData.map((item) => item.date);
          const turnover = validData.map((item) => item.turnover);
          const amount = validData.map((item) => item.amount / 100000000);
          chartInstance.current.setOption({
            title: { text: '换手率和成交额', left: 'center' },
            tooltip: {
              trigger: 'axis',
              axisPointer: { type: 'cross', crossStyle: { color: '#999' } },
            },
            legend: { data: ['换手率', '成交额'], top: 30 },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: [
              {
                type: 'category',
                data: dates,
                axisPointer: { type: 'shadow' },
                axisLabel: { rotate: 45 },
              },
            ],
            yAxis: [
              {
                type: 'value',
                name: '换手率(%)',
                min: 0,
                axisLabel: { formatter: '{value}%' },
              },
              {
                type: 'value',
                name: '成交额(亿元)',
                min: 0,
                axisLabel: { formatter: '{value}亿' },
              },
            ],
            series: [
              {
                name: '换手率',
                type: 'bar',
                data: turnover,
                itemStyle: { color: '#3b82f6' },
              },
              {
                name: '成交额',
                type: 'line',
                yAxisIndex: 1,
                data: amount,
                smooth: true,
                itemStyle: { color: '#ef4444' },
                lineStyle: { width: 2 },
                symbol: 'circle',
                symbolSize: 6,
              },
            ],
          });
        } catch (e) {
          console.error('图表初始化失败:', e);
          setTimeout(initChart, 100);
        }
      };
      requestAnimationFrame(initChart);
      const resizeHandler = () => chartInstance.current?.resize();
      window.addEventListener('resize', resizeHandler);
      return () => {
        window.removeEventListener('resize', resizeHandler);
        if (chartInstance.current) {
          chartInstance.current.dispose();
          chartInstance.current = null;
          setIsChartInitialized(false);
        }
      };
    }
  }, [data]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div ref={chartRef} style={{ width: '100%', height: '400px' }} />
    </div>
  );
};

export default TurnoverChart;
