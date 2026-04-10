/**
 * 前端 API 统一封装
 * 统一 API 调用（规则 5.3）
 */
import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('响应错误:', error);
    const message = error.response?.data?.message || '请求失败';
    return Promise.reject(new Error(message));
  }
);

export const dataApi = {
  getData: async () => {
    return api.get('/data');
  },
  refresh: async () => {
    return api.post('/refresh');
  },
};

export const indicatorApi = {
  getIndicators: async () => {
    return api.get('/indicators');
  },
};

export const riskApi = {
  getRisk: async () => {
    return api.get('/risk');
  },
};

export const reportApi = {
  getReport: async () => {
    return api.get('/report');
  },
};

export default api;
