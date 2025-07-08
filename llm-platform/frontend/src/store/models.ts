import { defineStore } from 'pinia'
import { ref } from 'vue'
import { modelsApi } from '@/api/models'
import type { Model } from '@/types'
import { ElMessage } from 'element-plus'

export const useModelsStore = defineStore('models', () => {
  // State
  const models = ref<Model[]>([])
  const activeModels = ref<Model[]>([])
  const loading = ref(false)
  const selectedModel = ref<Model | null>(null)
  
  // Actions
  const fetchModels = async () => {
    try {
      loading.value = true
      const data = await modelsApi.getModels()
      models.value = data
    } catch (error: any) {
      ElMessage.error('获取模型列表失败')
      console.error('Failed to fetch models:', error)
    } finally {
      loading.value = false
    }
  }
  
  const fetchActiveModels = async () => {
    try {
      const data = await modelsApi.getActiveModels()
      activeModels.value = data
      
      // Set default selected model if none selected
      if (!selectedModel.value && data.length > 0) {
        selectedModel.value = data[0]
      }
      
    } catch (error: any) {
      ElMessage.error('获取活跃模型列表失败')
      console.error('Failed to fetch active models:', error)
    }
  }
  
  const selectModel = (model: Model) => {
    selectedModel.value = model
    localStorage.setItem('selected_model', JSON.stringify(model))
  }
  
  const initSelectedModel = () => {
    const saved = localStorage.getItem('selected_model')
    if (saved) {
      try {
        selectedModel.value = JSON.parse(saved)
      } catch (error) {
        console.error('Failed to parse saved model:', error)
      }
    }
  }
  
  const getModelByName = (name: string): Model | undefined => {
    return models.value.find(model => model.name === name)
  }
  
  const refreshModels = async () => {
    await Promise.all([
      fetchModels(),
      fetchActiveModels()
    ])
  }
  
  return {
    // State
    models: readonly(models),
    activeModels: readonly(activeModels),
    loading: readonly(loading),
    selectedModel,
    
    // Actions
    fetchModels,
    fetchActiveModels,
    selectModel,
    initSelectedModel,
    getModelByName,
    refreshModels
  }
})