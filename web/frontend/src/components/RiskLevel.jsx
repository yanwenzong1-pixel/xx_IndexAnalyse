import React from 'react';

const RiskLevel = ({ riskLevel }) => {
  const getRiskColor = (level) => {
    if (level <= 3) return 'text-green-500';
    if (level <= 6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getRiskText = (level) => {
    if (level <= 3) return '低风险';
    if (level <= 6) return '中等风险';
    return '高风险';
  };

  return (
    <div className="flex items-center space-x-2">
      <span className="font-medium">风险等级:</span>
      <span className={`text-xl font-bold ${getRiskColor(riskLevel)}`}>
        {riskLevel}/10
      </span>
      <span className={`text-sm ${getRiskColor(riskLevel)}`}>
        ({getRiskText(riskLevel)})
      </span>
    </div>
  );
};

export default RiskLevel;
