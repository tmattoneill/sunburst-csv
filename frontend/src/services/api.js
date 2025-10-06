// src/utils/api.js
import axios from 'axios';

export const API_CONFIG = {
    API_PATH: process.env.VUE_APP_API_ROOT_PATH || '/api',
    API_BASE_URL: process.env.VUE_APP_BASE_URL || window.location.origin
};


const apiClient = axios.create({
    baseURL: `${API_CONFIG.API_BASE_URL}${API_CONFIG.API_PATH}`,
    timeout: 5000
});

export const API_ENDPOINTS = {
    UPLOAD: 'upload',
    PROCESS: 'process',
    DATA: 'data',
    HEALTH: 'health',
    TABLE_DATA: 'table-data',
    FILE_INFO: 'file-info',
    VALIDATE_COLUMNS: 'validate-columns',
    ANALYZE: 'analyze',
};

export const fetchApi = async (endpoint, options = {}) => {
    try {
        const { method = 'get', data, params, ...rest } = options;

        // Validate method is defined
        if (!method || typeof method !== 'string') {
            throw new Error(`Invalid method parameter: ${method}`);
        }

        // Special handling for GET requests with params
        if (method.toLowerCase() === 'get') {
            // If we have filters in params, ensure they're properly stringified
            if (params?.filters) {
                const serializedParams = new URLSearchParams();

                // Add non-filter params
                Object.entries(params).forEach(([key, value]) => {
                    if (key !== 'filters') {
                        serializedParams.append(key, value);
                    }
                });

                // Add stringified filters
                if (typeof params.filters === 'object' && Object.keys(params.filters).length > 0) {
                    serializedParams.append('filters', JSON.stringify(params.filters));
                }

                // Make the request with serialized params
                const response = await apiClient.get(`${endpoint}?${serializedParams.toString()}`, rest);
                return response.data;
            }

            // Regular GET request
            const response = await apiClient.get(endpoint, { params, ...rest });
            return response.data;
        }

        // For other methods (POST, PUT, etc.)
        const response = await apiClient[method.toLowerCase()](endpoint, data, rest);
        return response.data;
    } catch (error) {
        const requestMethod = options.method || 'get';
        console.error('API Error:', {
            endpoint,
            status: error.response?.status,
            data: error.response?.data,
            message: error.message,
            request: {
                method: requestMethod,
                params: options.params,
                data: options.data
            }
        });
        const errorMessage = error.response?.data?.error ||
                           error.response?.data?.message ||
                           error.message ||
                           'An unexpected error occurred';
        throw new Error(errorMessage);
    }
};
