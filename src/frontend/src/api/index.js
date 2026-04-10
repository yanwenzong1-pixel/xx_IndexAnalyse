/**
 * 前端 API 统一封装（Tier A：单客户端）
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || error.message || '请求失败';
    return Promise.reject(new Error(message));
  }
);

export const dataApi = {
  getData: () => api.get('/data'),
  refresh: () => api.post('/refresh'),
};

export const riskApi = {
  getRisk: () => api.get('/risk'),
};

export const predictApi = {
  getHistory: (days = 300, includeEvaluation = true) =>
    api.get('/predict/history', {
      params: { days, include_evaluation: includeEvaluation },
    }),
};

export default api;
