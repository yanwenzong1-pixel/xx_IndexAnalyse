import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const fetchData = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    console.error('获取数据失败:', error);
    return { success: false, message: '获取数据失败' };
  }
};

export const fetchIndicators = async () => {
  try {
    const response = await api.get('/indicators');
    return response.data;
  } catch (error) {
    console.error('获取指标失败:', error);
    return { success: false, message: '获取指标失败' };
  }
};

export const fetchRisk = async () => {
  try {
    const response = await api.get('/risk');
    return response.data;
  } catch (error) {
    console.error('获取风险评估失败:', error);
    return { success: false, message: '获取风险评估失败' };
  }
};

export const fetchReport = async () => {
  try {
    const response = await api.get('/report');
    return response.data;
  } catch (error) {
    console.error('获取报告失败:', error);
    return { success: false, message: '获取报告失败' };
  }
};

export const refreshData = async () => {
  try {
    const response = await api.post('/refresh');
    return response.data;
  } catch (error) {
    console.error('刷新数据失败:', error);
    return { success: false, message: '刷新数据失败' };
  }
};
