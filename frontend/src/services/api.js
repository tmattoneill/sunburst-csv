// src/utils/api.js
import axios from 'axios';

export const API_CONFIG = {
    BASE_URL: process.env.VUE_APP_API_BASE_URL || 'http://localhost',
    API_PORT: process.env.VUE_APP_API_PORT || 6500,
    API_PATH: process.env.VUE_APP_API_ROOT_PATH || '/api'
}

const apiClient = axios.create({
    baseURL: `${API_CONFIG.BASE_URL}:${API_CONFIG.API_PORT}${API_CONFIG.API_PATH}`,
    timeout: 5000
});

export const buildApiUrl = (endpoint) => {
    // Remove leading slash from endpoint if present
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
    // Remove trailing slash from API_PATH if present

    const cleanApiPath = API_CONFIG.API_PATH.endsWith('/')
        ? API_CONFIG.API_PATH.slice(0, -1)
        : API_CONFIG.API_PATH

    const fullUrl = `${API_CONFIG.BASE_URL}:${API_CONFIG.API_PORT}${cleanApiPath}/${cleanEndpoint}`
    // DEBUG: Logging after variables are defined
    console.log({
        fullUrl,
        raw_endpoint: endpoint,
        cleanEndpoint,
        cleanApiPath,
        BASE_URL: API_CONFIG.BASE_URL,
        FLASK_PORT: API_CONFIG.API_PORT,
        API_PATH: API_CONFIG.API_PATH
    });

    return `${API_CONFIG.BASE_URL}:${API_CONFIG.API_PORT}${cleanApiPath}/${cleanEndpoint}`
}

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
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
};