<template>
  <div class="models-page">
    <div class="page-header">
      <div class="header-content">
        <h1>模型管理</h1>
        <p>查看和管理可用的 AI 模型</p>
      </div>
      
      <div class="header-actions">
        <el-button @click="refreshModels" :loading="modelsStore.loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- Models Grid -->
    <div v-if="modelsStore.loading" class="loading">
      <el-skeleton :rows="6" animated />
    </div>
    
    <div v-else class="models-grid">
      <el-card
        v-for="model in modelsStore.models"
        :key="model.id"
        class="model-card"
        :class="{ 
          'selected': modelsStore.selectedModel?.id === model.id,
          'inactive': !model.is_active 
        }"
        shadow="hover"
        @click="selectModel(model)"
      >
        <template #header>
          <div class="model-header">
            <div class="model-info">
              <div class="model-name">{{ model.display_name }}</div>
              <div class="model-provider">
                {{ getProviderIcon(model.provider) }} {{ model.provider }}
              </div>
            </div>
            
            <div class="model-status">
              <el-tag
                :type="getStatusColor(model.is_active ? 'active' : 'inactive')"
                size="small"
              >
                {{ model.is_active ? '活跃' : '停用' }}
              </el-tag>
            </div>
          </div>
        </template>
        
        <div class="model-content">
          <div v-if="model.description" class="model-description">
            {{ model.description }}
          </div>
          
          <div class="model-specs">
            <div class="spec-item">
              <el-icon><Setting /></el-icon>
              <span>最大 Token: {{ formatNumber(model.max_tokens) }}</span>
            </div>
            
            <div class="spec-item">
              <el-icon><TrendCharts /></el-icon>
              <span>优先级: {{ model.priority }}</span>
            </div>
            
            <div v-if="model.endpoint_url" class="spec-item">
              <el-icon><Link /></el-icon>
              <span class="endpoint">{{ truncateText(model.endpoint_url, 30) }}</span>
            </div>
          </div>
          
          <!-- Model Metadata -->
          <div v-if="model.metadata" class="model-metadata">
            <el-tag
              v-for="(value, key) in getDisplayMetadata(model.metadata)"
              :key="key"
              size="small"
              class="metadata-tag"
            >
              {{ key }}: {{ value }}
            </el-tag>
          </div>
        </div>
        
        <template #footer>
          <div class="model-actions">
            <el-button
              size="small"
              type="primary"
              :disabled="!model.is_active"
              @click.stop="useModel(model)"
            >
              <el-icon><ChatDotRound /></el-icon>
              使用模型
            </el-button>
            
            <el-button
              size="small"
              @click.stop="testModel(model)"
              :disabled="!model.is_active"
            >
              <el-icon><Monitor /></el-icon>
              测试
            </el-button>
            
            <el-dropdown
              v-if="authStore.isAdmin"
              @command="handleModelAction"
              @click.stop
            >
              <el-button size="small">
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{ action: 'edit', model }">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-dropdown-item>
                  <el-dropdown-item 
                    :command="{ action: 'toggle', model }"
                    :divided="true"
                  >
                    <el-icon><Switch /></el-icon>
                    {{ model.is_active ? '停用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item 
                    :command="{ action: 'delete', model }"
                    class="danger-item"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-card>
    </div>
    
    <!-- Empty State -->
    <div v-if="!modelsStore.loading && modelsStore.models.length === 0" class="empty-state">
      <el-empty description="暂无模型数据" />
    </div>
    
    <!-- Model Details Dialog -->
    <el-dialog
      v-model="detailsDialogVisible"
      :title="selectedModelDetails?.display_name"
      width="600px"
    >
      <div v-if="selectedModelDetails" class="model-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">
            {{ selectedModelDetails.name }}
          </el-descriptions-item>
          <el-descriptions-item label="显示名称">
            {{ selectedModelDetails.display_name }}
          </el-descriptions-item>
          <el-descriptions-item label="提供商">
            {{ getProviderIcon(selectedModelDetails.provider) }} {{ selectedModelDetails.provider }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(selectedModelDetails.is_active ? 'active' : 'inactive')">
              {{ selectedModelDetails.is_active ? '活跃' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大 Token">
            {{ formatNumber(selectedModelDetails.max_tokens) }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            {{ selectedModelDetails.priority }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatTime(selectedModelDetails.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedModelDetails.endpoint_url" label="API 端点" :span="2">
            <el-link :href="selectedModelDetails.endpoint_url" target="_blank">
              {{ selectedModelDetails.endpoint_url }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedModelDetails.description" label="描述" :span="2">
            {{ selectedModelDetails.description }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedModelDetails.metadata" class="metadata-section">
          <h4>元数据</h4>
          <el-tag
            v-for="(value, key) in selectedModelDetails.metadata"
            :key="key"
            class="metadata-tag"
          >
            {{ key }}: {{ typeof value === 'object' ? JSON.stringify(value) : value }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useModelsStore } from '@/store/models'
import { formatNumber, formatTime, getProviderIcon, getStatusColor, truncateText } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Model } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const modelsStore = useModelsStore()

const detailsDialogVisible = ref(false)
const selectedModelDetails = ref<Model | null>(null)

const selectModel = (model: Model) => {
  if (!model.is_active) {
    ElMessage.warning('该模型已停用')
    return
  }
  
  modelsStore.selectModel(model)
  ElMessage.success(`已选择模型：${model.display_name}`)
}

const useModel = (model: Model) => {
  modelsStore.selectModel(model)
  router.push('/chat')
}

const testModel = (model: Model) => {
  modelsStore.selectModel(model)
  router.push('/test')
}

const refreshModels = async () => {
  await modelsStore.refreshModels()
  ElMessage.success('模型列表已刷新')
}

const handleModelAction = async ({ action, model }: { action: string; model: Model }) => {
  switch (action) {
    case 'edit':
      selectedModelDetails.value = model
      detailsDialogVisible.value = true
      break
    case 'toggle':
      await toggleModelStatus(model)
      break
    case 'delete':
      await deleteModel(model)
      break
  }
}

const toggleModelStatus = async (model: Model) => {
  try {
    await ElMessageBox.confirm(
      `确定要${model.is_active ? '停用' : '启用'}模型 "${model.display_name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: Implement toggle model status API call
    ElMessage.success(`模型已${model.is_active ? '停用' : '启用'}`)
    
  } catch {
    // User cancelled
  }
}

const deleteModel = async (model: Model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.display_name}" 吗？此操作不可恢复。`,
      '危险操作',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    // TODO: Implement delete model API call
    ElMessage.success('模型已删除')
    
  } catch {
    // User cancelled
  }
}

const getDisplayMetadata = (metadata: Record<string, any>) => {
  const displayMeta: Record<string, string> = {}
  
  // Show only important metadata fields
  const importantFields = ['context_length', 'capabilities', 'specialization', 'languages']
  
  for (const field of importantFields) {
    if (metadata[field]) {
      if (Array.isArray(metadata[field])) {
        displayMeta[field] = metadata[field].join(', ')
      } else {
        displayMeta[field] = String(metadata[field])
      }
    }
  }
  
  return displayMeta
}

onMounted(async () => {
  await modelsStore.fetchModels()
})
</script>

<style scoped>
.models-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.header-content p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.model-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.model-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.model-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.model-card.inactive {
  opacity: 0.6;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.model-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.model-provider {
  font-size: 14px;
  color: var(--text-secondary);
}

.model-content {
  margin-bottom: 16px;
}

.model-description {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.model-specs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.endpoint {
  font-family: monospace;
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.model-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.metadata-tag {
  font-size: 11px;
}

.model-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.loading,
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.model-details {
  max-height: 60vh;
  overflow-y: auto;
}

.metadata-section {
  margin-top: 20px;
}

.metadata-section h4 {
  margin-bottom: 12px;
  color: var(--text-primary);
}

.metadata-section .metadata-tag {
  margin: 4px 8px 4px 0;
}

.danger-item {
  color: var(--error-color);
}

@media (max-width: 768px) {
  .models-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .model-actions {
    flex-wrap: wrap;
  }
}
</style>