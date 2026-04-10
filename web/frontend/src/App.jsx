import React, { useState, useEffect } from 'react';
import RiskLevel from './components/RiskLevel';
import IndicatorCards from './components/IndicatorCards';
import PriceChart from './components/PriceChart';
import TurnoverChart from './components/TurnoverChart';
import AlertMessage from './components/AlertMessage';
import TabComponent from './components/TabComponent';
// import { fetchData, fetchRisk, refreshData } from './services/api';

// 模拟数据
const mockData = {
  latest: {
    date: "2024-03-06",
    close: 1500.0,
    change_pct: 2.5,
    amount: 1000000000,
    turnover: 5.2
  },
  history: [
    {
      date: "2024-03-05",
      close: 1463.5,
      change_pct: -1.2,
      amount: 950000000,
      turnover: 4.8
    },
    {
      date: "2024-03-04",
      close: 1481.3,
      change_pct: 0.5,
      amount: 980000000,
      turnover: 5.0
    },
    {
      date: "2024-03-01",
      close: 1474.0,
      change_pct: -0.8,
      amount: 920000000,
      turnover: 4.6
    },
    {
      date: "2024-02-28",
      close: 1486.0,
      change_pct: 1.2,
      amount: 1050000000,
      turnover: 5.3
    },
    {
      date: "2024-02-27",
      close: 1468.0,
      change_pct: -0.5,
      amount: 980000000,
      turnover: 5.0
    }
  ]
};

const mockRisk = {
  risk_level: 5,
  downside_probability: 0.4,
  alert: false,
  alert_message: ""
};

function App() {
  // 从 localStorage 恢复状态
  const [data, setData] = useState(() => {
    const cachedData = localStorage.getItem('microCapData');
    return cachedData ? JSON.parse(cachedData) : null;
  });
  const [risk, setRisk] = useState(() => {
    const cachedRisk = localStorage.getItem('microCapRisk');
    return cachedRisk ? JSON.parse(cachedRisk) : null;
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(() => {
    const cachedTab = localStorage.getItem('activeTab');
    return cachedTab || 'price';
  });
  // 强制刷新 key，用于触发表格重绘
  const [refreshKey, setRefreshKey] = useState(0);

  const tabs = [
    { id: 'price', label: '价格走势' },
    { id: 'turnover', label: '成交量' }
  ];

  // 处理Tab切换并保存状态
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    localStorage.setItem('activeTab', tabId);
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 使用模拟数据
      // 模拟网络请求延迟，更真实地模拟实际场景
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 确保数据结构完整
      if (mockData && 
          typeof mockData === 'object' && 
          mockData.latest && 
          typeof mockData.latest === 'object' && 
          mockData.history && 
          Array.isArray(mockData.history) && 
          mockData.history.length > 0 &&
          // 检查历史数据的结构
          mockData.history.every(item => 
            typeof item === 'object' && 
            item.date && 
            typeof item.close === 'number' && 
            typeof item.change_pct === 'number' && 
            typeof item.amount === 'number' && 
            typeof item.turnover === 'number'
          ) &&
          // 检查最新数据的结构
          typeof mockData.latest.date === 'string' && 
          typeof mockData.latest.close === 'number' && 
          typeof mockData.latest.change_pct === 'number' && 
          typeof mockData.latest.amount === 'number' && 
          typeof mockData.latest.turnover === 'number'
      ) {
        setData(mockData);
        // 保存数据到localStorage
        localStorage.setItem('microCapData', JSON.stringify(mockData));
      } else {
        throw new Error('数据结构不完整或数据类型错误');
      }
      
      if (mockRisk && 
          typeof mockRisk === 'object' && 
          typeof mockRisk.risk_level === 'number' && 
          typeof mockRisk.downside_probability === 'number' && 
          typeof mockRisk.alert === 'boolean'
      ) {
        setRisk(mockRisk);
        // 保存风险数据到localStorage
        localStorage.setItem('microCapRisk', JSON.stringify(mockRisk));
      } else {
        throw new Error('风险数据不完整或数据类型错误');
      }
      
      /*
      const dataResponse = await fetchData();
      const riskResponse = await fetchRisk();
      
      if (dataResponse.success && dataResponse.data && dataResponse.data.latest && dataResponse.data.history) {
        setData(dataResponse.data);
      } else {
        setError(dataResponse.message || '数据加载失败');
      }
      
      if (riskResponse.success && riskResponse.data) {
        setRisk(riskResponse.data);
      } else {
        setError(riskResponse.message || '风险数据加载失败');
      }
      */
    } catch (err) {
      setError(err.message || '加载数据失败');
      console.error(err);
      // 加载失败时使用默认数据，确保页面可以正常显示
      setData(mockData);
      setRisk(mockRisk);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    // 模拟刷新
    setLoading(true);
    try {
      // 模拟网络请求延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 确保数据结构完整
      if (mockData && mockData.latest && mockData.history && Array.isArray(mockData.history)) {
        setData(mockData);
        // 保存数据到 localStorage
        localStorage.setItem('microCapData', JSON.stringify(mockData));
      } else {
        throw new Error('数据结构不完整');
      }
      
      if (mockRisk) {
        setRisk(mockRisk);
        // 保存风险数据到 localStorage
        localStorage.setItem('microCapRisk', JSON.stringify(mockRisk));
      } else {
        throw new Error('风险数据不完整');
      }
      
      // 增加刷新 key，强制图表重绘
      setRefreshKey(prev => prev + 1);
    } catch (err) {
      setError(err.message || '刷新数据失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
    /*
    const response = await refreshData();
    if (response.success) {
      loadData();
    } else {
      setError(response.message);
    }
    */
  };

  useEffect(() => {
    loadData();
    // 每 3 小时自动刷新数据
    const interval = setInterval(loadData, 3 * 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // 监听页面刷新事件，F5 后强制重绘图表
  useEffect(() => {
    // 页面加载完成后延迟触发一次，确保图表正确绘制
    const timer = setTimeout(() => {
      setRefreshKey(prev => prev + 1);
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-screen bg-gray-100 dark:bg-gray-900">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <div className="text-xl font-medium text-gray-700 dark:text-gray-300">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-screen">
        <div className="text-2xl font-bold text-red-500 mb-4">{error}</div>
        <button 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={loadData}
        >
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-white">
      {/* 顶部导航栏 */}
      <header className="bg-white dark:bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            微盘股指数分析系统
          </h1>
          <div className="flex items-center space-x-4">
            {risk && risk.risk_level !== undefined && <RiskLevel riskLevel={risk.risk_level} />}
            <button
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              onClick={handleRefresh}
              disabled={loading}
            >
              {loading ? '刷新中...' : '刷新数据'}
            </button>
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="container mx-auto px-4 py-8">
        {/* 预警信息 */}
        {risk && risk.alert && risk.alert_message && (
          <AlertMessage message={risk.alert_message} />
        )}

        {/* 指标卡片 */}
        {data && data.latest ? (
          <IndicatorCards data={data.latest} />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-gray-100 dark:bg-gray-800 rounded-lg shadow p-4 animate-pulse">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-700 dark:text-gray-300">
                    加载中...
                  </h3>
                  <span className="text-2xl">📊</span>
                </div>
                <div className="text-2xl font-bold text-gray-400">--</div>
              </div>
            ))}
          </div>
        )}

        {/* 图表区域 */}
        <div className="mt-8">
          <TabComponent activeTab={activeTab} setActiveTab={handleTabChange} tabs={tabs} />
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            {data && data.history && Array.isArray(data.history) && data.history.length > 0 ? (
              activeTab === 'price' ? (
                <PriceChart key={refreshKey} data={data.history} forceRefreshKey={refreshKey} />
              ) : (
                <TurnoverChart data={data.history} />
              )
            ) : (
              <div className="flex justify-center items-center h-80">
                <div className="text-gray-400">加载中...</div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* 页脚 */}
      <footer className="bg-white dark:bg-gray-800 shadow-inner mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-gray-600 dark:text-gray-400">
            © 2024 微盘股指数分析系统
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
