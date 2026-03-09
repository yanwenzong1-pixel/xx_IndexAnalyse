import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';

const PriceChart = ({ data }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [isChartInitialized, setIsChartInitialized] = useState(false);

  useEffect(() => {
    if (chartRef.current && data && Array.isArray(data) && data.length > 0) {
      // 确保DOM渲染完成后初始化图表
      const initChart = () => {
        try {
          // 检查DOM元素是否存在且可见
          if (!chartRef.current || chartRef.current.offsetWidth === 0 || chartRef.current.offsetHeight === 0) {
            // 延迟重试
            setTimeout(initChart, 100);
            return;
          }

          // 初始化图表
          if (!chartInstance.current) {
            chartInstance.current = echarts.init(chartRef.current);
            setIsChartInitialized(true);
          }

          // 验证数据结构
          const validData = data.filter(item => 
            item && 
            typeof item === 'object' && 
            item.date && 
            typeof item.close === 'number'
          );

          if (validData.length === 0) {
            throw new Error('无效的图表数据');
          }

          // 准备数据
          const dates = validData.map(item => item.date);
          const closePrices = validData.map(item => item.close);

          // 计算MA5和MA20
          const ma5 = [];
          const ma20 = [];
          
          for (let i = 0; i < validData.length; i++) {
            if (i >= 4) {
              let sum = 0;
              for (let j = 0; j < 5; j++) {
                sum += validData[i - j].close;
              }
              ma5.push(sum / 5);
            } else {
              ma5.push(null);
            }

            if (i >= 19) {
              let sum = 0;
              for (let j = 0; j < 20; j++) {
                sum += validData[i - j].close;
              }
              ma20.push(sum / 20);
            } else {
              ma20.push(null);
            }
          }

          // 配置选项
          const option = {
            title: {
              text: '微盘股指数价格走势',
              left: 'center'
            },
            tooltip: {
              trigger: 'axis',
              formatter: function(params) {
                let result = params[0].name + '<br/>';
                params.forEach(param => {
                  result += `${param.marker} ${param.seriesName}: ${param.value.toFixed(2)}<br/>`;
                });
                return result;
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
              containLabel: true
            },
            xAxis: {
              type: 'category',
              boundaryGap: false,
              data: dates,
              axisLabel: {
                rotate: 45
              }
            },
            yAxis: {
              type: 'value',
              scale: true
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

          // 设置选项
          chartInstance.current.setOption(option);
        } catch (error) {
          console.error('图表初始化失败:', error);
          // 失败后重试
          setTimeout(initChart, 100);
        }
      };

      // 使用requestAnimationFrame确保DOM渲染完成
      requestAnimationFrame(initChart);

      // 响应式
      const resizeHandler = () => {
        chartInstance.current?.resize();
      };

      window.addEventListener('resize', resizeHandler);

      return () => {
        window.removeEventListener('resize', resizeHandler);
        // 销毁图表实例，避免内存泄漏
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
      <div ref={chartRef} style={{ width: '100%', height: '400px' }}></div>
    </div>
  );
};

export default PriceChart;
