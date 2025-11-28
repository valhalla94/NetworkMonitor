import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_URL,
});

export const getHosts = () => api.get('/hosts/');
export const createHost = (data) => api.post('/hosts/', data);
export const updateHost = (id, data) => api.put(`/hosts/${id}`, data);
export const deleteHost = (id) => api.delete(`/hosts/${id}`);
export const getMetrics = (hostId, range = '-1h') => api.get(`/metrics/${hostId}`, { params: { range } });
export const getNetworkStatus = () => api.get('/status');
export const getPublicIpHistory = () => api.get('/public-ip-history');
export const getSpeedTestHistory = () => api.get('/speedtest/history');
export const runSpeedTest = () => api.post('/speedtest/run');

export default api;
