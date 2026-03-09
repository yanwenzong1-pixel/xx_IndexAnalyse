import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';

const TurnoverChart = ({ data }) => {
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
            typeof item.turnover === 'number' && 
            typeof item.amount === 'number'
          );

          if (validData.length === 0) {
            throw new Error('无效的图表数据');
          }

          // 准备数据
          const dates = validData.map(item => item.date);
          const turnover = validData.map(item => item.turnover);
          const amount = validData.map(item => item.amount / 100000000); // 转换为亿元

          // 配置选项
          const option = {
            title: {
              text: '换手率和成交额',
              left: 'center'
            },
            tooltip: {
              trigger: 'axis',
              axisPointer: {
                type: 'cross',
                crossStyle: {
                  color: '#999'
                }
              }
            },
            legend: {
              data: ['换手率', '成交额'],
              top: 30
            },
            grid: {
              left: '3%',
              right: '4%',
              bottom: '3%',
              containLabel: true
            },
            xAxis: [
              {
                type: 'category',
                data: dates,
                axisPointer: {
                  type: 'shadow'
                },
                axisLabel: {
                  rotate: 45
                }
              }
            ],
            yAxis: [
              {
                type: 'value',
                name: '换手率(%)',
                min: 0,
                axisLabel: {
                  formatter: '{value}%'
                }
              },
              {
                type: 'value',
                name: '成交额(亿元)',
                min: 0,
                axisLabel: {
                  formatter: '{value}亿'
                }
              }
            ],
            series: [
              {
                name: '换手率',
                type: 'bar',
                data: turnover,
                itemStyle: {
                  color: '#3b82f6'
                }
              },
              {
                name: '成交额',
                type: 'line',
                yAxisIndex: 1,
                data: amount,
                smooth: true,
                itemStyle: {
                  color: '#ef4444'
                },
                lineStyle: {
                  width: 2
                },
                symbol: 'circle',
                symbolSize: 6
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

export default TurnoverChart;
