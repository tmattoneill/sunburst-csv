// src/utils/api.js
export const API_CONFIG = {
    BASE_URL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:6500',
    API_PATH: process.env.VUE_APP_API_ROOT_PATH || '/api'
}

export const buildApiUrl = (endpoint) => {
    // Remove leading slash from endpoint if present
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
    // Remove trailing slash from API_PATH if present
    if(!API_CONFIG.API_PATH){
        console.error("API_PATH is not defined")
        return
    }
    const cleanApiPath = API_CONFIG.API_PATH.endsWith('/')
        ? API_CONFIG.API_PATH.slice(0, -1)
        : API_CONFIG.API_PATH
    console.log(cleanApiPath)
    return `${API_CONFIG.BASE_URL}${cleanApiPath}/${cleanEndpoint}`
}

export const API_ENDPOINTS = {
    UPLOAD: 'upload',
    PROCESS: 'process',
    DATA: 'data',
    HEALTH: 'health',
    TABLE_DATA: 'table-data',
}