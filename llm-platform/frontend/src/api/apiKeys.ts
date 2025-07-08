import { apiGet, apiPost, apiPut, apiDelete } from './index'
import type { ApiKey, ApiKeyCreate, ApiKeyCreateResponse } from '@/types'

export const apiKeysApi = {
  // Get user's API keys
  getApiKeys(): Promise<ApiKey[]> {
    return apiGet('/api-keys')
  },
  
  // Get active API keys
  getActiveApiKeys(): Promise<ApiKey[]> {
    return apiGet('/api-keys/active')
  },
  
  // Create new API key
  createApiKey(data: ApiKeyCreate): Promise<ApiKeyCreateResponse> {
    return apiPost('/api-keys', data)
  },
  
  // Update API key
  updateApiKey(id: number, data: { name?: string; is_active?: boolean }): Promise<ApiKey> {
    return apiPut(`/api-keys/${id}`, data)
  },
  
  // Delete API key
  deleteApiKey(id: number): Promise<void> {
    return apiDelete(`/api-keys/${id}`)
  }
}