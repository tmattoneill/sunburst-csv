// src/utils/api.js
import axios from 'axios';

export const API_CONFIG = {
    API_PATH: process.env.VUE_APP_API_ROOT_PATH || '/api'
}

const apiClient = axios.create({
    baseURL: `${API_CONFIG.API_PATH}`,
    timeout: 5000
});

export const buildApiUrl = (endpoint) => {
    const apiUrl = new URL(API_CONFIG.API_PATH, window.location.origin);
    return `${apiUrl.pathname.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;
};


export const API_ENDPOINTS = {
    UPLOAD: 'upload',
    PROCESS: 'process',
    DATA: 'data',
    HEALTH: 'health',
    TABLE_DATA: 'table-data',
}


export const fetchApi = async (endpoint, options = {}) => {
    try {
        const { method = 'get', data, ...rest } = options;
        const response = await apiClient[method.toLowerCase()](endpoint, data, rest);
        return response.data;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error.response?.data || error.message);
        throw new Error(error.response?.data?.message || 'An unexpected error occurred');
    }
};
