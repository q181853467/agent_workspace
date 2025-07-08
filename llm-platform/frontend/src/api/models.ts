import { apiGet, apiPost, apiPut, apiDelete } from './index'
import type { Model, ModelCreate } from '@/types'

export const modelsApi = {
  // Get all models
  getModels(): Promise<Model[]> {
    return apiGet('/models')
  },
  
  // Get active models only
  getActiveModels(): Promise<Model[]> {
    return apiGet('/models/active')
  },
  
  // Get model by ID
  getModel(id: number): Promise<Model> {
    return apiGet(`/models/${id}`)
  },
  
  // Get model by name
  getModelByName(name: string): Promise<Model> {
    return apiGet(`/models/name/${name}`)
  },
  
  // Create new model (admin only)
  createModel(data: ModelCreate): Promise<Model> {
    return apiPost('/admin/models', data)
  },
  
  // Update model (admin only)
  updateModel(id: number, data: Partial<ModelCreate>): Promise<Model> {
    return apiPut(`/admin/models/${id}`, data)
  },
  
  // Delete model (admin only)
  deleteModel(id: number): Promise<void> {
    return apiDelete(`/admin/models/${id}`)
  },
  
  // Get all models (admin only)
  getAllModels(): Promise<Model[]> {
    return apiGet('/admin/models')
  }
}