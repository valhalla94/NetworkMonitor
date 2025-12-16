import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_URL,
});

api.interceptors.request.use((config) => {
    const token = sessionStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const login = (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/token', formData);
};

export const getHosts = () => api.get('/hosts/');
export const createHost = (data) => api.post('/hosts/', data);
export const updateHost = (id, data) => api.put(`/hosts/${id}`, data);
export const deleteHost = (id) => api.delete(`/hosts/${id}`);
export const getMetrics = (hostId, range = '-1h') => api.get(`/metrics/${hostId}`, { params: { range } });
export const getNetworkStatus = () => api.get('/status');
export const getPublicIpHistory = () => api.get('/public-ip-history');
export const getSpeedTestHistory = () => api.get('/speedtest/history');
export const runSpeedTest = () => api.post('/speedtest/run');
export const quickPing = (target) => api.post('/tools/ping', { target });
export const getSettings = () => api.get('/settings');
export const updateNotificationSettings = (url) => api.post('/settings/notifications', { key: 'notification_url', value: url });

export default api;
