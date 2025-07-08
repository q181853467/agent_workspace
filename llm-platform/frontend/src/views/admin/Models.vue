<template>
  <div class="admin-models">
    <div class="page-header">
      <div class="header-content">
        <h1>模型管理</h1>
        <p>管理系统接入的大模型，配置模型参数和状态</p>
      </div>
      
      <div class="header-actions">
        <el-button @click="refreshModels" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          添加模型
        </el-button>
      </div>
    </div>
    
    <!-- Search and Filter -->
    <el-card shadow="never" class="search-card">
      <div class="search-form">
        <el-input
          v-model="searchQuery"
          placeholder="搜索模型名称或提供商"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="providerFilter"
          placeholder="提供商"
          clearable
          style="width: 150px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="OpenAI" value="openai" />
          <el-option label="Deepseek" value="deepseek" />
          <el-option label="Claude" value="claude" />
          <el-option label="本地模型" value="local" />
        </el-select>
        
        <el-select
          v-model="statusFilter"
          placeholder="模型状态"
          clearable
          style="width: 150px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="活跃" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </div>
    </el-card>
    
    <!-- Models Table -->
    <el-card shadow="never">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="8" animated />
      </div>
      
      <el-table
        v-else
        :data="filteredModels"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="name" label="模型名称" min-width="180">
          <template #default="{ row }">
            <div class="model-info">
              <div class="model-icon">
                <el-icon size="20" :color="getProviderColor(row.provider)">
                  <Box />
                </el-icon>
              </div>
              <div class="model-details">
                <div class="model-name">{{ row.name }}</div>
                <div class="model-version">{{ row.version || 'v1.0' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="provider" label="提供商" width="120">
          <template #default="{ row }">
            <el-tag
              :type="getProviderTagType(row.provider)"
              size="small"
            >
              {{ formatProvider(row.provider) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="endpoint_url" label="接口地址" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="endpoint-url">{{ row.endpoint_url }}</code>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag
              :type="row.is_active ? 'success' : 'danger'"
              size="small"
            >
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="health_status" label="健康状态" width="100">
          <template #default="{ row }">
            <div class="health-status">
              <el-icon 
                :color="getHealthColor(row.health_status)" 
                size="16"
              >
                <CircleCheckFilled v-if="row.health_status === 'healthy'" />
                <CircleCloseFilled v-else-if="row.health_status === 'unhealthy'" />
                <Loading v-else />
              </el-icon>
              <span class="health-text">{{ formatHealthStatus(row.health_status) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at, 'YYYY-MM-DD') }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="测试">
                <el-button
                  size="small"
                  text
                  type="primary"
                  @click="testModel(row)"
                  :loading="testingModelId === row.id"
                >
                  <el-icon><Position /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="编辑">
                <el-button
                  size="small"
                  text
                  @click="editModel(row)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip :content="row.is_active ? '停用' : '启用'">
                <el-button
                  size="small"
                  text
                  :type="row.is_active ? 'warning' : 'success'"
                  @click="toggleModelStatus(row)"
                >
                  <el-icon><Switch /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="删除">
                <el-button
                  size="small"
                  text
                  type="danger"
                  @click="deleteModel(row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无模型数据" />
        </template>
      </el-table>
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑模型' : '添加模型'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="模型名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="例如: gpt-4o, deepseek-coder-v2"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="提供商" prop="provider">
          <el-select
            v-model="form.provider"
            placeholder="选择模型提供商"
            style="width: 100%"
            @change="handleProviderChange"
          >
            <el-option label="OpenAI" value="openai" />
            <el-option label="Deepseek" value="deepseek" />
            <el-option label="Claude" value="claude" />
            <el-option label="本地模型" value="local" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="接口地址" prop="endpoint_url">
          <el-input
            v-model="form.endpoint_url"
            placeholder="https://api.openai.com/v1/chat/completions"
            type="url"
          />
        </el-form-item>
        
        <el-form-item label="版本" prop="version">
          <el-input
            v-model="form.version"
            placeholder="模型版本（可选）"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="模型描述信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="模型配置">
          <el-card shadow="never" class="config-card">
            <div class="config-row">
              <label>最大Token数：</label>
              <el-input-number
                v-model="form.max_tokens"
                :min="1"
                :max="100000"
                placeholder="4096"
                style="width: 120px"
              />
            </div>
            
            <div class="config-row">
              <label>默认Temperature：</label>
              <el-input-number
                v-model="form.default_temperature"
                :min="0"
                :max="2"
                :step="0.1"
                placeholder="0.7"
                style="width: 120px"
              />
            </div>
            
            <div class="config-row">
              <label>支持流式：</label>
              <el-switch v-model="form.supports_streaming" />
            </div>
            
            <div class="config-row">
              <label>支持函数调用：</label>
              <el-switch v-model="form.supports_functions" />
            </div>
          </el-card>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="submitting"
            @click="submitForm"
          >
            {{ isEditing ? '保存' : '添加' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- Test Result Dialog -->
    <el-dialog
      v-model="testDialogVisible"
      title="模型测试结果"
      width="500px"
    >
      <div class="test-result">
        <div v-if="testResult.success" class="test-success">
          <el-icon color="#67c23a" size="24"><CircleCheckFilled /></el-icon>
          <div class="result-content">
            <h4>测试成功</h4>
            <p>模型响应正常，延迟: {{ testResult.latency }}ms</p>
            <div class="response-content">
              <strong>响应内容:</strong>
              <div class="response-text">{{ testResult.response }}</div>
            </div>
          </div>
        </div>
        
        <div v-else class="test-error">
          <el-icon color="#f56c6c" size="24"><CircleCloseFilled /></el-icon>
          <div class="result-content">
            <h4>测试失败</h4>
            <p class="error-message">{{ testResult.error }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import { formatTime, isValidUrl } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Model, ModelCreate, ModelUpdate } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const testDialogVisible = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const providerFilter = ref('')
const statusFilter = ref('')
const testingModelId = ref<number | null>(null)

const models = ref<Model[]>([])
const currentEditingModel = ref<Model | null>(null)
const testResult = ref<any>({})

const formRef = ref<FormInstance>()
const form = reactive<ModelCreate & { 
  version?: string;
  description?: string;
  max_tokens?: number;
  default_temperature?: number;
  supports_streaming?: boolean;
  supports_functions?: boolean;
}>({
  name: '',
  provider: '',
  endpoint_url: '',
  version: '',
  description: '',
  max_tokens: 4096,
  default_temperature: 0.7,
  supports_streaming: true,
  supports_functions: false,
  is_active: true
})

const validateUrl = (rule: any, value: string, callback: any) => {
  if (value && !isValidUrl(value)) {
    callback(new Error('请输入正确的URL地址'))
  } else {
    callback()
  }
}

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 2, max: 100, message: '模型名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  endpoint_url: [
    { required: true, message: '请输入接口地址', trigger: 'blur' },
    { validator: validateUrl, trigger: 'blur' }
  ]
}

const filteredModels = computed(() => {
  let filtered = models.value
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(model => 
      model.name.toLowerCase().includes(query) ||
      model.provider.toLowerCase().includes(query)
    )
  }
  
  // Provider filter
  if (providerFilter.value) {
    filtered = filtered.filter(model => model.provider === providerFilter.value)
  }
  
  // Status filter
  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(model => model.is_active === isActive)
  }
  
  return filtered
})

const getProviderColor = (provider: string) => {
  const colors: Record<string, string> = {
    openai: '#10b981',
    deepseek: '#6366f1',
    claude: '#f59e0b',
    local: '#8b5cf6',
    other: '#6b7280'
  }
  return colors[provider] || colors.other
}

const getProviderTagType = (provider: string) => {
  const types: Record<string, string> = {
    openai: 'success',
    deepseek: 'primary',
    claude: 'warning',
    local: 'info',
    other: 'info'
  }
  return types[provider] || types.other
}

const formatProvider = (provider: string) => {
  const names: Record<string, string> = {
    openai: 'OpenAI',
    deepseek: 'Deepseek',
    claude: 'Claude',
    local: '本地模型',
    other: '其他'
  }
  return names[provider] || provider
}

const getHealthColor = (status: string) => {
  const colors: Record<string, string> = {
    healthy: '#67c23a',
    unhealthy: '#f56c6c',
    unknown: '#909399'
  }
  return colors[status] || colors.unknown
}

const formatHealthStatus = (status: string) => {
  const labels: Record<string, string> = {
    healthy: '健康',
    unhealthy: '异常',
    unknown: '未知'
  }
  return labels[status] || '未知'
}

const loadModels = async () => {
  try {
    loading.value = true
    models.value = await adminApi.getModels()
  } catch (error: any) {
    ElMessage.error('获取模型列表失败')
    console.error('Failed to load models:', error)
  } finally {
    loading.value = false
  }
}

const refreshModels = async () => {
  await loadModels()
  ElMessage.success('模型列表已刷新')
}

const handleSearch = () => {
  // Search is reactive through computed property
}

const handleFilter = () => {
  // Filter is reactive through computed property
}

const handleProviderChange = (provider: string) => {
  // Set default endpoint based on provider
  const defaultEndpoints: Record<string, string> = {
    openai: 'https://api.openai.com/v1/chat/completions',
    deepseek: 'https://api.deepseek.com/v1/chat/completions',
    claude: 'https://api.anthropic.com/v1/messages',
    local: 'http://localhost:8000/v1/chat/completions'
  }
  
  if (defaultEndpoints[provider]) {
    form.endpoint_url = defaultEndpoints[provider]
  }
}

const showCreateDialog = () => {
  isEditing.value = false
  dialogVisible.value = true
}

const editModel = (model: Model) => {
  isEditing.value = true
  currentEditingModel.value = model
  
  form.name = model.name
  form.provider = model.provider
  form.endpoint_url = model.endpoint_url
  form.version = model.metadata?.version || ''
  form.description = model.metadata?.description || ''
  form.max_tokens = model.metadata?.max_tokens || 4096
  form.default_temperature = model.metadata?.default_temperature || 0.7
  form.supports_streaming = model.metadata?.supports_streaming ?? true
  form.supports_functions = model.metadata?.supports_functions ?? false
  form.is_active = model.is_active
  
  dialogVisible.value = true
}

const resetForm = () => {
  form.name = ''
  form.provider = ''
  form.endpoint_url = ''
  form.version = ''
  form.description = ''
  form.max_tokens = 4096
  form.default_temperature = 0.7
  form.supports_streaming = true
  form.supports_functions = false
  form.is_active = true
  currentEditingModel.value = null
  formRef.value?.resetFields()
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        
        const metadata = {
          version: form.version,
          description: form.description,
          max_tokens: form.max_tokens,
          default_temperature: form.default_temperature,
          supports_streaming: form.supports_streaming,
          supports_functions: form.supports_functions
        }
        
        if (isEditing.value && currentEditingModel.value) {
          // Update model
          const updateData: ModelUpdate = {
            name: form.name,
            provider: form.provider,
            endpoint_url: form.endpoint_url,
            metadata,
            is_active: form.is_active
          }
          
          await adminApi.updateModel(currentEditingModel.value.id, updateData)
          ElMessage.success('模型信息已更新')
        } else {
          // Create model
          await adminApi.createModel({
            name: form.name,
            provider: form.provider,
            endpoint_url: form.endpoint_url,
            metadata,
            is_active: form.is_active
          })
          ElMessage.success('模型添加成功')
        }
        
        dialogVisible.value = false
        await loadModels()
        
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const testModel = async (model: Model) => {
  try {
    testingModelId.value = model.id
    const result = await adminApi.testModel(model.id)
    testResult.value = result
    testDialogVisible.value = true
  } catch (error: any) {
    testResult.value = {
      success: false,
      error: error.message || '测试失败'
    }
    testDialogVisible.value = true
  } finally {
    testingModelId.value = null
  }
}

const toggleModelStatus = async (model: Model) => {
  try {
    await ElMessageBox.confirm(
      `确定要${model.is_active ? '停用' : '启用'}模型 "${model.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await adminApi.updateModel(model.id, {
      is_active: !model.is_active
    })
    
    ElMessage.success(`模型已${model.is_active ? '停用' : '启用'}`)
    await loadModels()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const deleteModel = async (model: Model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.name}" 吗？此操作不可恢复。`,
      '危险操作',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    await adminApi.deleteModel(model.id)
    ElMessage.success('模型已删除')
    await loadModels()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(async () => {
  await loadModels()
})
</script>

<style scoped>
.admin-models {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-details {
  display: flex;
  flex-direction: column;
}

.model-name {
  font-weight: 600;
  color: var(--text-primary);
}

.model-version {
  font-size: 12px;
  color: var(--text-secondary);
}

.endpoint-url {
  font-size: 12px;
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text-secondary);
}

.health-status {
  display: flex;
  align-items: center;
  gap: 4px;
}

.health-text {
  font-size: 12px;
}

.table-actions {
  display: flex;
  gap: 4px;
}

.config-card {
  border: 1px solid var(--border-light);
}

.config-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-row:last-child {
  margin-bottom: 0;
}

.config-row label {
  font-size: 14px;
  color: var(--text-secondary);
}

.test-result {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.test-success,
.test-error {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
}

.result-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.result-content p {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
}

.response-content {
  margin-top: 12px;
}

.response-text {
  background: var(--bg-tertiary);
  padding: 12px;
  border-radius: 6px;
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.error-message {
  color: var(--error-color);
}

.loading {
  padding: 20px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-form .el-input,
  .search-form .el-select {
    width: 100% !important;
  }
}
</style>