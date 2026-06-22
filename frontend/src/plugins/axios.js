import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

console.log('Initializing axios with VITE_API_URL:', import.meta.env.VITE_API_URL)

// Create axios instance with base URL
const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 30000, // Increased timeout to 30 seconds
    withCredentials: true,  // Enable cookie handling
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

// Add request interceptor
axiosInstance.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        
        // Add authorization header if token exists
        if (authStore.access_token) {
            config.headers.Authorization = `Bearer ${authStore.access_token}`
        }

        const timestamp = new Date().toISOString()
        console.group(`[${timestamp}] Axios Request: ${config.method?.toUpperCase()} ${config.url}`)
        console.log('Base URL:', config.baseURL)
        console.log('Full URL:', config.url)
        console.log('Method:', config.method)
        console.log('Headers:', config.headers)
        console.log('With Credentials:', config.withCredentials)
        if (config.data) {
            const dataCopy = { ...config.data }
            if (dataCopy.password) dataCopy.password = '[REDACTED]'
            console.log('Request Data:', dataCopy)
        }
        console.groupEnd()
        return config
    },
    (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
    }
)

// Add response interceptor for error handling
axiosInstance.interceptors.response.use(
    (response) => {
        const timestamp = new Date().toISOString()
        console.group(`[${timestamp}] Axios Response: ${response.config.method?.toUpperCase()} ${response.config.url}`)
        console.log('Status Code:', response.status)
        console.log('Status Text:', response.statusText)
        console.log('Response Data:', response.data)
        console.groupEnd()
        return response
    },
    async (error) => {
        const originalRequest = error.config
        
        if (
            error.response?.status !== 401 ||
            originalRequest._retry ||
            originalRequest.url.includes('/auth/login') ||
            originalRequest.url.includes('/auth/refresh')
        ) {
            return Promise.reject(error)
        }

        const authStore = useAuthStore()
        originalRequest._retry = true
        
        try {
            // Use the new refreshToken method
            const refreshSuccess = await authStore.refreshToken()
            if (refreshSuccess) {
                // Small delay to ensure cookies are set
                await new Promise(resolve => setTimeout(resolve, 300))
                // Retry the original request
                return axiosInstance(originalRequest)
            }
            // If refresh failed, logout and reject
            await authStore.logout()
            return Promise.reject(error)
        } catch (refreshError) {
            console.error('Token refresh failed:', refreshError)
            await authStore.logout()
            return Promise.reject(refreshError)
        }
    }
)

export default axiosInstance
