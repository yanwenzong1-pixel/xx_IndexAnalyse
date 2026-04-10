import React from 'react';

const AlertMessage = ({ message }) => {
  const isRiskAlert = message.includes('下跌风险');
  return (
    <div
      className={`rounded-lg shadow p-4 mb-6 ${
        isRiskAlert
          ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
          : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
      }`}
    >
      <div className="flex items-center">
        <div className="mr-3 text-2xl">{isRiskAlert ? '⚠️' : '📈'}</div>
        <div>
          <h3 className="font-bold text-lg">
            {isRiskAlert ? '风险警报' : '买点信号'}
          </h3>
          <p className="mt-1">{message}</p>
        </div>
      </div>
    </div>
  );
};

export default AlertMessage;
