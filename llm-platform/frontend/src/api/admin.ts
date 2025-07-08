import { apiGet, apiPost, apiPut, apiDelete } from './index'
import type { User, UserCreate, UserUpdate, Model, ModelCreate, OverviewStats, UsageStats, AccessLog } from '@/types'

export const adminApi = {
  // User management
  getUsers(skip = 0, limit = 100): Promise<User[]> {
    return apiGet(`/admin/users?skip=${skip}&limit=${limit}`)
  },
  
  createUser(data: UserCreate): Promise<User> {
    return apiPost('/admin/users', data)
  },
  
  updateUser(id: number, data: UserUpdate): Promise<User> {
    return apiPut(`/admin/users/${id}`, data)
  },
  
  deleteUser(id: number): Promise<void> {
    return apiDelete(`/admin/users/${id}`)
  },
  
  // Model management
  getModels(skip = 0, limit = 100): Promise<Model[]> {
    return apiGet(`/admin/models?skip=${skip}&limit=${limit}`)
  },
  
  createModel(data: ModelCreate): Promise<Model> {
    return apiPost('/admin/models', data)
  },
  
  updateModel(id: number, data: Partial<ModelCreate>): Promise<Model> {
    return apiPut(`/admin/models/${id}`, data)
  },
  
  deleteModel(id: number): Promise<void> {
    return apiDelete(`/admin/models/${id}`)
  },
  
  // Statistics
  getOverviewStats(): Promise<OverviewStats> {
    return apiGet('/admin/stats/overview')
  },
  
  getUsageStats(days = 7): Promise<UsageStats> {
    return apiGet(`/admin/stats/usage?days=${days}`)
  },
  
  // Logs
  getRecentLogs(limit = 50): Promise<AccessLog[]> {
    return apiGet(`/admin/logs/recent?limit=${limit}`)
  }
}