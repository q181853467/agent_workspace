<template>
  <div class="api-keys-page">
    <div class="page-header">
      <div class="header-content">
        <h1>API 密钥管理</h1>
        <p>创建和管理您的 API 密钥，用于访问 LLM Platform API</p>
      </div>
      
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建 API 密钥
        </el-button>
      </div>
    </div>
    
    <!-- API Keys Table -->
    <el-card shadow="never">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="5" animated />
      </div>
      
      <el-table
        v-else
        :data="apiKeys"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="name" label="名称" min-width="150">
          <template #default="{ row }">
            <div class="key-name">
              <strong>{{ row.name }}</strong>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="key_prefix" label="密钥" min-width="200">
          <template #default="{ row }">
            <div class="key-prefix">
              <code>{{ row.key_prefix }}</code>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="usage_count" label="使用次数" width="120">
          <template #default="{ row }">
            {{ formatNumber(row.usage_count) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="last_used_at" label="最后使用" width="160">
          <template #default="{ row }">
            <span v-if="row.last_used_at">
              {{ formatRelativeTime(row.last_used_at) }}
            </span>
            <span v-else class="text-placeholder">未使用</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at, 'YYYY-MM-DD') }}
          </template>
        </el-table-column>
        
        <el-table-column prop="expires_at" label="过期时间" width="160">
          <template #default="{ row }">
            <span v-if="row.expires_at">
              {{ formatTime(row.expires_at, 'YYYY-MM-DD') }}
            </span>
            <span v-else class="text-placeholder">永不过期</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-dropdown @command="handleAction">
              <el-button size="small" text>
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{ action: 'toggle', key: row }">
                    <el-icon><Switch /></el-icon>
                    {{ row.is_active ? '停用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'edit', key: row }">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-dropdown-item>
                  <el-dropdown-item 
                    :command="{ action: 'delete', key: row }"
                    class="danger-item"
                    divided
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无 API 密钥">
            <el-button type="primary" @click="showCreateDialog">
              创建第一个 API 密钥
            </el-button>
          </el-empty>
        </template>
      </el-table>
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑 API 密钥' : '创建 API 密钥'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入 API 密钥名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="过期时间" prop="expires_at">
          <el-date-picker
            v-model="form.expires_at"
            type="datetime"
            placeholder="选择过期时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item v-if="isEditing" label="状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="活跃"
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
            {{ isEditing ? '保存' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- API Key Display Dialog -->
    <el-dialog
      v-model="keyDisplayVisible"
      title="API 密钥创建成功"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="key-display">
        <el-alert
          title="重要提示"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            请保存您的 API 密钥，它只会显示一次。如果丢失，您需要删除并重新创建。
          </template>
        </el-alert>
        
        <div class="key-container">
          <label>您的 API 密钥：</label>
          <div class="key-value">
            <el-input
              :model-value="newApiKey"
              readonly
              type="textarea"
              :rows="3"
            />
            <el-button
              type="primary"
              @click="copyApiKey"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="keyDisplayVisible = false">
            我已保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { apiKeysApi } from '@/api/apiKeys'
import { formatNumber, formatTime, formatRelativeTime, copyToClipboard } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApiKey, ApiKeyCreate } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const keyDisplayVisible = ref(false)
const isEditing = ref(false)
const apiKeys = ref<ApiKey[]>([])
const newApiKey = ref('')
const currentEditingKey = ref<ApiKey | null>(null)

const formRef = ref<FormInstance>()
const form = reactive<ApiKeyCreate & { is_active?: boolean }>({
  name: '',
  expires_at: undefined,
  is_active: true
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入 API 密钥名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

const loadApiKeys = async () => {
  try {
    loading.value = true
    apiKeys.value = await apiKeysApi.getApiKeys()
  } catch (error: any) {
    ElMessage.error('获取 API 密钥列表失败')
    console.error('Failed to load API keys:', error)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEditing.value = false
  dialogVisible.value = true
}

const showEditDialog = (apiKey: ApiKey) => {
  isEditing.value = true
  currentEditingKey.value = apiKey
  form.name = apiKey.name
  form.expires_at = apiKey.expires_at || undefined
  form.is_active = apiKey.is_active
  dialogVisible.value = true
}

const resetForm = () => {
  form.name = ''
  form.expires_at = undefined
  form.is_active = true
  currentEditingKey.value = null
  formRef.value?.resetFields()
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        
        if (isEditing.value && currentEditingKey.value) {
          // Update API key
          await apiKeysApi.updateApiKey(currentEditingKey.value.id, {
            name: form.name,
            is_active: form.is_active
          })
          ElMessage.success('API 密钥已更新')
        } else {
          // Create new API key
          const response = await apiKeysApi.createApiKey({
            name: form.name,
            expires_at: form.expires_at
          })
          
          newApiKey.value = response.key
          keyDisplayVisible.value = true
          ElMessage.success('API 密钥创建成功')
        }
        
        dialogVisible.value = false
        await loadApiKeys()
        
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleAction = async ({ action, key }: { action: string; key: ApiKey }) => {
  switch (action) {
    case 'edit':
      showEditDialog(key)
      break
    case 'toggle':
      await toggleApiKey(key)
      break
    case 'delete':
      await deleteApiKey(key)
      break
  }
}

const toggleApiKey = async (apiKey: ApiKey) => {
  try {
    await ElMessageBox.confirm(
      `确定要${apiKey.is_active ? '停用' : '启用'} API 密钥 "${apiKey.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await apiKeysApi.updateApiKey(apiKey.id, {
      is_active: !apiKey.is_active
    })
    
    ElMessage.success(`API 密钥已${apiKey.is_active ? '停用' : '启用'}`)
    await loadApiKeys()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const deleteApiKey = async (apiKey: ApiKey) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 API 密钥 "${apiKey.name}" 吗？此操作不可恢复。`,
      '危险操作',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    await apiKeysApi.deleteApiKey(apiKey.id)
    ElMessage.success('API 密钥已删除')
    await loadApiKeys()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const copyApiKey = async () => {
  const success = await copyToClipboard(newApiKey.value)
  if (success) {
    ElMessage.success('API 密钥已复制到剪贴板')
  } else {
    ElMessage.error('复制失败')
  }
}

onMounted(async () => {
  await loadApiKeys()
})
</script>

<style scoped>
.api-keys-page {
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

.key-name strong {
  color: var(--text-primary);
}

.key-prefix code {
  background: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: var(--text-primary);
}

.text-placeholder {
  color: var(--text-tertiary);
  font-style: italic;
}

.loading {
  padding: 20px;
}

.danger-item {
  color: var(--error-color);
}

.key-display {
  space-y: 16px;
}

.key-container {
  margin-top: 20px;
}

.key-container label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.key-value {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.key-value .el-input {
  flex: 1;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .key-value {
    flex-direction: column;
  }
}
</style>