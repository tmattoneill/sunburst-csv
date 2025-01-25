// src/utils/api.js
export const API_CONFIG = {
    BASE_URL: import.meta.env.VITE_APP_BASE_URL,
    API_PATH: import.meta.env.VITE_API_BASE_URL
}

export const buildApiUrl = (endpoint) => {
    // Remove leading slash from endpoint if present
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
    // Remove trailing slash from API_PATH if present
    const cleanApiPath = API_CONFIG.API_PATH.endsWith('/')
        ? API_CONFIG.API_PATH.slice(0, -1)
        : API_CONFIG.API_PATH

    return `${API_CONFIG.BASE_URL}${cleanApiPath}/${cleanEndpoint}`
}

export const API_ENDPOINTS = {
    UPLOAD: 'upload',
    PROCESS: 'process',
    DATA: 'data',
    HEALTH: 'health',
    TABLE_DATA: 'table-data',
}