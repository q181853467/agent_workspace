import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import type { ApiResponse } from '@/types'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config: any) => {
    NProgress.start()
    
    // Add auth token from localStorage directly
    const token = localStorage.getItem('auth_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    NProgress.done()
    
    // Handle business logic errors
    const { code, message, data } = response.data
    
    if (code !== undefined && code !== 0 && code !== 200) {
      ElMessage.error(message || 'Request failed')
      return Promise.reject(new Error(message || 'Request failed'))
    }
    
    return response
  },
  (error) => {
    NProgress.done()
    
    const { response } = error
    
    // Check if we're in demo mode
    const isDemoMode = localStorage.getItem('auth_token')?.startsWith('demo-')
    
    // In demo mode, don't show network errors
    if (isDemoMode && error.code === 'ERR_NETWORK') {
      console.warn('Network error in demo mode - API not available')
      return Promise.reject(error)
    }
    
    if (response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('demo_user')
      window.location.href = '/login'
      ElMessage.error('认证失效，请重新登录')
    } else if (response?.status === 403) {
      ElMessage.error('没有权限访问此资源')
    } else if (response?.status === 429) {
      ElMessage.error('请求过于频繁，请稍后再试')
    } else if (response?.status >= 500) {
      ElMessage.error('服务器错误，请稍后再试')
    } else if (error.code === 'ERR_NETWORK') {
      ElMessage.error('网络连接失败，请检查网络或稍后再试')
    } else {
      const message = response?.data?.message || error.message || 'Request failed'
      ElMessage.error(message)
    }
    
    return Promise.reject(error)
  }
)

export default api

// Utility functions for common API operations
export const apiGet = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  return api.get<ApiResponse<T>>(url, config).then(res => res.data.data)
}

export const apiPost = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  return api.post<ApiResponse<T>>(url, data, config).then(res => res.data.data)
}

export const apiPut = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  return api.put<ApiResponse<T>>(url, data, config).then(res => res.data.data)
}

export const apiDelete = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  return api.delete<ApiResponse<T>>(url, config).then(res => res.data.data)
}