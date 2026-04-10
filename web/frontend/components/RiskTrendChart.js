/**
 * 风险趋势图表组件 - 独立模块
 * 使用方式：<RiskTrendChart data={riskData} />
 * 
 * 功能：
 * - 使用 ECharts 绘制风险打分折线图
 * - 支持 tooltips 显示详细信息
 * - 响应式设计
 * - 数据格式验证和错误处理
 */

function RiskTrendChart({ data }) {
  const chartRef = React.useRef(null);
  
  // 数据验证和格式化
  const validateAndFormatData = (rawData) => {
    console.log('[RiskTrendChart] 原始数据:', rawData);
    
    if (!rawData || !Array.isArray(rawData)) {
      console.error('[RiskTrendChart] 数据格式错误：不是数组');
      return [];
    }
    
    if (rawData.length === 0) {
      console.warn('[RiskTrendChart] 数据为空数组');
      return [];
    }
    
    // 验证并格式化数据
    const formattedData = rawData.map((item, index) => {
      // 检查必需字段
      if (!item.date || item.risk_score === undefined) {
        console.error(`[RiskTrendChart] 第${index}条数据缺少必需字段`);
        return null;
      }
      
      // 确保 risk_score 是数字
      const riskScore = parseFloat(item.risk_score);
      if (isNaN(riskScore)) {
        console.error(`[RiskTrendChart] 第${index}条数据的 risk_score 不是数字:`, item.risk_score);
        return null;
      }
      
      return {
        date: item.date,
        risk_score: riskScore,
        risk_level: item.risk_level || 'unknown'
      };
    }).filter(item => item !== null); // 移除无效数据
    
    console.log('[RiskTrendChart] 格式化后的数据:', formattedData);
    console.log('[RiskTrendChart] 有效数据条数:', formattedData.length);
    
    return formattedData;
  };
  
  // 辅助函数：风险等级文本
  const getRiskLevelText = (score) => {
    if (score <= 3) return '低风险';
    if (score <= 5) return '中等风险';
    if (score <= 7) return '较高风险';
    return '高风险';
  };
  
  // 辅助函数：风险等级颜色
  const getRiskColor = (score) => {
    if (score <= 3) return '#10b981';
    if (score <= 5) return '#fbbf24';
    if (score <= 7) return '#fb923c';
    return '#ef4444';
  };
  
  React.useEffect(() => {
    console.log('[RiskTrendChart] useEffect 触发，data:', data);
    
    // 验证和格式化数据
    const formattedData = validateAndFormatData(data);
    
    if (!chartRef.current) {
      console.error('[RiskTrendChart] chartRef.current 为 null');
      return;
    }
    
    if (!formattedData || formattedData.length === 0) {
      console.warn('[RiskTrendChart] 没有有效数据可渲染');
      return;
    }
    
    console.log('[RiskTrendChart] 开始初始化图表...');
    
    // 销毁现有图表实例
    const existingChart = echarts.getInstanceByDom(chartRef.current);
    if (existingChart) {
      existingChart.dispose();
    }
    
    const chart = echarts.init(chartRef.current);
    console.log('[RiskTrendChart] 图表实例创建成功');
    
    const option = {
      title: {
        text: '历史风险等级趋势',
        left: 'center',
        top: 15,  // 增加标题与顶部距离
        textStyle: {
          fontSize: 18,  // 增大字号
          fontWeight: 'bold',  // 加粗
          color: '#1f2937'  // 使用深灰色，更柔和
        }
      },
      
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const item = formattedData[params[0].dataIndex];
          return `
            <div style="padding: 8px;">
              <div style="font-weight: 600; margin-bottom: 4px;">
                ${item.date}
              </div>
              <div>风险打分：${item.risk_score.toFixed(1)}</div>
              <div style="color: ${getRiskColor(item.risk_score)}">
                风险等级：${getRiskLevelText(item.risk_score)}
              </div>
            </div>
          `;
        }
      },
      
      xAxis: {
        type: 'category',
        data: formattedData.map(item => item.date),
        boundaryGap: false,
        axisLabel: {
          rotate: 0,  // 改为水平显示
          interval: 'auto',  // 自动计算显示间隔，避免重叠
          margin: 10,  // 增加标签与底部距离
          fontSize: 11,  // 稍微缩小字号，增加可读性
          color: '#6b7280'  // 使用柔和的灰色
        }
      },
      
      yAxis: {
        type: 'value',
        min: 0,
        max: 10,
        interval: 1,
        name: '风险打分',
        splitLine: {
          lineStyle: { type: 'dashed' }
        }
      },
      
      series: [{
        name: '风险打分',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: formattedData.map(item => item.risk_score),
        lineStyle: {
          color: '#dc2626',
          width: 2
        },
        itemStyle: {
          color: '#dc2626'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(220, 38, 38, 0.5)' },
            { offset: 1, color: 'rgba(220, 38, 38, 0.1)' }
          ])
        }
      }],
      
      grid: {
        left: '5%',  // 增加左侧边距
        right: '5%',  // 增加右侧边距
        bottom: '50px',  // 增加底部空间，给 X 标签留足位置
        top: '80px',  // 增加顶部空间，标题不再贴边
        containLabel: true
      }
    };
    
    console.log('[RiskTrendChart] 设置图表配置...');
    chart.setOption(option);
    console.log('[RiskTrendChart] 图表渲染完成');
    
    const handleResize = () => {
      chart.resize();
    };
    window.addEventListener('resize', handleResize);
    
    return () => {
      console.log('[RiskTrendChart] 清理图表实例');
      window.removeEventListener('resize', handleResize);
      const chartInstance = echarts.getInstanceByDom(chartRef.current);
      if (chartInstance) {
        chartInstance.dispose();
      }
    };
  }, [data]);
  
  console.log('[RiskTrendChart] 渲染组件，data:', data);
  return <div ref={chartRef} className="w-full h-full" />;
}

// 导出组件
window.RiskTrendChart = RiskTrendChart;
