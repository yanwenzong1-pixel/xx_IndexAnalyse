import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as echarts from 'echarts';

const PriceChart = ({ data, forceRefreshKey }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const dataRef = useRef(null); // 使用 ref 保存数据，避免引用变化
  const [chartKey, setChartKey] = useState(0);
  const isMounted = useRef(false);

  /**
   * 验证数据有效性
   */
  const validateData = useCallback((data) => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return false;
    }

    return data.some(item => 
      item && 
      typeof item === 'object' && 
      item.date && 
      typeof item.close === 'number' &&
      !isNaN(item.close) &&
      isFinite(item.close)
    );
  }, []);

  /**
   * 计算移动平均线
   */
  const calculateMA = useCallback((data, period) => {
    const ma = [];
    for (let i = 0; i < data.length; i++) {
      if (i >= period - 1) {
        let sum = 0;
        for (let j = 0; j < period; j++) {
          sum += data[i - j].close;
        }
        ma.push(parseFloat((sum / period).toFixed(2)));
      } else {
        ma.push(null);
      }
    }
    return ma;
  }, []);

  /**
   * 渲染图表
   */
  const renderChart = useCallback(() => {
    if (!chartRef.current || !data || !validateData(data)) {
      return false;
    }

    try {
      // 检查数据是否真的变化（通过比较第一个和最后一个元素）
      if (dataRef.current && dataRef.current.length > 0 && data.length > 0) {
        const first1 = dataRef.current[0]?.date;
        const last1 = dataRef.current[dataRef.current.length - 1]?.date;
        const first2 = data[0]?.date;
        const last2 = data[data.length - 1]?.date;
        
        if (first1 === first2 && last1 === last2) {
          // 数据未变化，跳过渲染
          return true;
        }
      }

      // 销毁现有图表
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
      }

      // 保存数据引用
      dataRef.current = data;

      // 初始化图表
      chartInstance.current = echarts.init(chartRef.current);

      // 准备数据
      const dates = data.map(item => item.date);
      const closePrices = data.map(item => item.close);
      const ma5 = calculateMA(data, 5);
      const ma20 = calculateMA(data, 20);

      // 计算 y 轴范围
      const validPrices = closePrices.filter(p => p !== null && !isNaN(p));
      const minPrice = Math.min(...validPrices);
      const maxPrice = Math.max(...validPrices);
      const padding = (maxPrice - minPrice) * 0.1 || 10;

      const option = {
        title: {
          text: '微盘股指数价格走势',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['收盘价', 'MA5', 'MA20'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: 80,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLabel: {
            rotate: 0,
            fontSize: 10,
            interval: Math.floor(dates.length / 10)
          }
        },
        yAxis: {
          type: 'value',
          min: minPrice - padding,
          max: maxPrice + padding,
          axisLabel: {
            formatter: function(value) {
              return value.toFixed(2);
            },
            color: '#000000'
          }
        },
        series: [
          {
            name: '收盘价',
            type: 'line',
            data: closePrices,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              width: 2,
              color: '#3b82f6'
            },
            areaStyle: {
              color: 'rgba(59, 130, 246, 0.1)'
            }
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
              type: 'dashed'
            }
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
              type: 'dotted'
            }
          }
        ]
      };

      // 设置选项，notMerge 确保完全替换旧配置
      chartInstance.current.setOption(option, true);
      
      return true;
    } catch (error) {
      console.error('图表渲染失败:', error);
      return false;
    }
  }, [data, validateData, calculateMA]);

  /**
   * 强制刷新图表
   */
  const forceRefresh = useCallback(() => {
    // 销毁旧实例
    if (chartInstance.current) {
      chartInstance.current.dispose();
      chartInstance.current = null;
    }
    
    // 增加 key 强制重建 DOM
    setChartKey(prev => prev + 1);
    
    // 延迟重新渲染，确保 DOM 已经重建
    setTimeout(() => {
      renderChart();
    }, 100);
  }, [renderChart]);

  // 监听 forceRefreshKey 变化
  useEffect(() => {
    if (forceRefreshKey !== undefined) {
      forceRefresh();
    }
  }, [forceRefreshKey, forceRefresh]);

  // 初始渲染和数据变化时渲染
  useEffect(() => {
    if (!isMounted.current) {
      // 首次挂载
      isMounted.current = true;
    }
    
    // 使用 requestAnimationFrame 确保 DOM 渲染完成
    const rafId = requestAnimationFrame(() => {
      renderChart();
    });

    // 响应式处理
    const resizeHandler = () => {
      if (chartInstance.current) {
        chartInstance.current.resize();
      }
    };

    window.addEventListener('resize', resizeHandler);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resizeHandler);
    };
  }, [renderChart]);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
        dataRef.current = null;
      }
    };
  }, []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div 
        key={chartKey} 
        ref={chartRef} 
        style={{ width: '100%', height: '400px' }}
      ></div>
    </div>
  );
};

export default PriceChart;
