import React, { useState, useEffect } from 'react';
import { dataApi, riskApi } from './api/index.js';
import cache from './utils/cache.js';
import RiskLevel from './components/RiskLevel.jsx';
import IndicatorCards from './components/IndicatorCards.jsx';
import PriceChart from './components/PriceChart.jsx';
import TurnoverChart from './components/TurnoverChart.jsx';
import AlertMessage from './components/AlertMessage.jsx';
import TabComponent from './components/TabComponent.jsx';
import RiskPredictionPanel from './components/RiskPredictionPanel.jsx';

const CACHE_TTL = 3 * 60 * 60 * 1000;

export default function App() {
  const [data, setData] = useState(null);
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('price');
  const [refreshKey, setRefreshKey] = useState(0);

  const tabs = [
    { id: 'price', label: '价格走势' },
    { id: 'turnover', label: '成交量' },
  ];

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const cachedData = cache.get('data');
      const cachedRisk = cache.get('risk');
      if (cachedData && cachedRisk) {
        setData(cachedData);
        setRisk(cachedRisk);
        setLoading(false);
        return;
      }
      const [dataResponse, riskResponse] = await Promise.all([
        dataApi.getData(),
        riskApi.getRisk(),
      ]);
      if (dataResponse.success && dataResponse.data) {
        setData(dataResponse.data);
        cache.set('data', dataResponse.data, CACHE_TTL);
      }
      if (riskResponse.success && riskResponse.data) {
        setRisk(riskResponse.data);
        cache.set('risk', riskResponse.data, CACHE_TTL);
      }
    } catch (err) {
      setError(err.message || '加载数据失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    setError(null);
    try {
      await dataApi.refresh();
      // 强制清空预测面板本地缓存，确保刷新后读取最新重算结果。
      localStorage.removeItem('predictionDataV2');
      localStorage.removeItem('predictionDataEvaluationV2');
      localStorage.removeItem('predictionDataTimestampV2');
      localStorage.removeItem('predictionDataMetaV2');
      cache.remove('data');
      cache.remove('risk');
      setRefreshKey((k) => k + 1);
      await loadData();
    } catch (err) {
      setError(err.message || '刷新失败：部分历史模块可能仍是旧缓存');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const t = cache.get('activeTab');
    if (t) setActiveTab(t);
    loadData();
    const iv = setInterval(loadData, 3 * 60 * 60 * 1000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const tmr = setTimeout(() => setRefreshKey((k) => k + 1), 100);
    return () => clearTimeout(tmr);
  }, []);

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    cache.set('activeTab', tabId, 7 * 24 * 60 * 60 * 1000);
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
        <div className="text-xl text-gray-700 dark:text-gray-300">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen">
        <div className="text-2xl font-bold text-red-500 mb-4">{error}</div>
        <button
          type="button"
          className="px-4 py-2 bg-blue-500 text-white rounded"
          onClick={loadData}
        >
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-white">
      <header className="bg-white dark:bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            微盘股指数分析系统
          </h1>
          <div className="flex items-center space-x-4">
            {risk?.risk_level !== undefined && (
              <RiskLevel riskLevel={risk.risk_level} />
            )}
            <button
              type="button"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              onClick={handleRefresh}
              disabled={loading}
            >
              {loading ? '刷新中...' : '刷新数据'}
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {risk?.alert && risk?.alert_message && (
          <AlertMessage message={risk.alert_message} />
        )}

        <RiskPredictionPanel />

        {data?.latest ? (
          <IndicatorCards data={data.latest} />
        ) : (
          <div className="text-gray-500 py-4">指标加载中...</div>
        )}

        <TabComponent
          tabs={tabs}
          activeTab={activeTab}
          setActiveTab={handleTabChange}
        />

        {data?.history ? (
          activeTab === 'price' ? (
            <PriceChart key={`price-${refreshKey}`} data={data.history} forceRefreshKey={refreshKey} />
          ) : (
            <TurnoverChart data={data.history} />
          )
        ) : null}
      </main>
    </div>
  );
}
