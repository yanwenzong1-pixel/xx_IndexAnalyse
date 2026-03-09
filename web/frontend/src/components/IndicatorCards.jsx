import React from 'react';

const IndicatorCards = ({ data }) => {
  const indicators = [
    {
      title: '收盘价',
      value: data.close.toFixed(2),
      icon: '📊',
      className: 'bg-blue-100 dark:bg-blue-900'
    },
    {
      title: '涨跌幅',
      value: `${data.change_pct.toFixed(2)}%`,
      icon: data.change_pct >= 0 ? '📈' : '📉',
      className: data.change_pct >= 0 ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'
    },
    {
      title: '成交额',
      value: `${(data.amount / 100000000).toFixed(2)}亿元`,
      icon: '💰',
      className: 'bg-yellow-100 dark:bg-yellow-900'
    },
    {
      title: '换手率',
      value: `${data.turnover.toFixed(2)}%`,
      icon: '🔄',
      className: 'bg-purple-100 dark:bg-purple-900'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {indicators.map((indicator, index) => (
        <div
          key={index}
          className={`${indicator.className} rounded-lg shadow p-4 transition-transform hover:scale-105`}
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-gray-700 dark:text-gray-300">
              {indicator.title}
            </h3>
            <span className="text-2xl">{indicator.icon}</span>
          </div>
          <div className="text-2xl font-bold">{indicator.value}</div>
        </div>
      ))}
    </div>
  );
};

export default IndicatorCards;
