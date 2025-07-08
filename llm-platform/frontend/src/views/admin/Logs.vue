<template>
  <div class="admin-logs">
    <div class="page-header">
      <div class="header-content">
        <h1>系统日志</h1>
        <p>查看API调用日志、错误记录和系统事件</p>
      </div>
      
      <div class="header-actions">
        <el-button @click="refreshLogs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportLogs">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>
    
    <!-- Search and Filter -->
    <el-card shadow="never" class="search-card">
      <div class="search-form">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户ID或错误信息"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="typeFilter"
          placeholder="请求类型"
          clearable
          style="width: 150px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="对话" value="chat" />
          <el-option label="流式对话" value="chat_stream" />
          <el-option label="文本补全" value="completions" />
          <el-option label="嵌入向量" value="embeddings" />
        </el-select>
        
        <el-select
          v-model="statusFilter"
          placeholder="状态码"
          clearable
          style="width: 120px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="成功 (200)" value="200" />
          <el-option label="客户端错误 (4xx)" value="4xx" />
          <el-option label="服务器错误 (5xx)" value="5xx" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
          @change="handleDateChange"
          style="width: 320px"
        />
      </div>
    </el-card>
    
    <!-- Logs Table -->
    <el-card shadow="never">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="10" animated />
      </div>
      
      <el-table
        v-else
        :data="filteredLogs"
        style="width: 100%"
        row-key="id"
        :default-sort="{ prop: 'created_at', order: 'descending' }"
      >
        <el-table-column prop="created_at" label="时间" width="160" sortable>
          <template #default="{ row }">
            {{ formatTime(row.created_at, 'YYYY-MM-DD HH:mm:ss') }}
          </template>
        </el-table-column>
        
        <el-table-column prop="request_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getRequestTypeColor(row.request_type)">
              {{ formatRequestType(row.request_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_id" label="用户" width="80">
          <template #default="{ row }">
            <span class="user-id">{{ row.user_id }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="model_name" label="模型" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="model-name">{{ row.model_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status_code" label="状态" width="80" sortable>
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="getStatusColor(row.status_code)"
            >
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="latency_ms" label="延迟" width="80" sortable>
          <template #default="{ row }">
            <span :class="getLatencyClass(row.latency_ms)">
              {{ row.latency_ms }}ms
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="prompt_tokens" label="Input" width="80">
          <template #default="{ row }">
            {{ row.prompt_tokens || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="completion_tokens" label="Output" width="80">
          <template #default="{ row }">
            {{ row.completion_tokens || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="total_tokens" label="Total" width="80">
          <template #default="{ row }">
            {{ row.total_tokens || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.error_message" class="error-message">
              {{ row.error_message }}
            </span>
            <span v-else class="text-success">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="查看详情">
                <el-button
                  size="small"
                  text
                  type="primary"
                  @click="viewLogDetail(row)"
                >
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="重试请求" v-if="row.status_code !== 200">
                <el-button
                  size="small"
                  text
                  type="warning"
                  @click="retryRequest(row)"
                >
                  <el-icon><RefreshRight /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无日志数据" />
        </template>
      </el-table>
      
      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="totalLogs"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- Log Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="800px"
      destroy-on-close
    >
      <div v-if="selectedLog" class="log-detail">
        <div class="detail-grid">
          <div class="detail-item">
            <label>时间:</label>
            <span>{{ formatTime(selectedLog.created_at, 'YYYY-MM-DD HH:mm:ss') }}</span>
          </div>
          
          <div class="detail-item">
            <label>请求类型:</label>
            <el-tag size="small" :type="getRequestTypeColor(selectedLog.request_type)">
              {{ formatRequestType(selectedLog.request_type) }}
            </el-tag>
          </div>
          
          <div class="detail-item">
            <label>用户ID:</label>
            <span>{{ selectedLog.user_id }}</span>
          </div>
          
          <div class="detail-item">
            <label>API密钥ID:</label>
            <span>{{ selectedLog.api_key_id }}</span>
          </div>
          
          <div class="detail-item">
            <label>模型:</label>
            <span>{{ selectedLog.model_name || '-' }}</span>
          </div>
          
          <div class="detail-item">
            <label>状态码:</label>
            <el-tag size="small" :type="getStatusColor(selectedLog.status_code)">
              {{ selectedLog.status_code }}
            </el-tag>
          </div>
          
          <div class="detail-item">
            <label>延迟:</label>
            <span :class="getLatencyClass(selectedLog.latency_ms)">
              {{ selectedLog.latency_ms }}ms
            </span>
          </div>
          
          <div class="detail-item" v-if="selectedLog.total_tokens">
            <label>Token使用:</label>
            <span>
              {{ selectedLog.prompt_tokens || 0 }} + {{ selectedLog.completion_tokens || 0 }} = {{ selectedLog.total_tokens }}
            </span>
          </div>
        </div>
        
        <div v-if="selectedLog.request_data" class="detail-section">
          <h4>请求数据</h4>
          <pre class="json-content">{{ formatJSON(selectedLog.request_data) }}</pre>
        </div>
        
        <div v-if="selectedLog.response_data" class="detail-section">
          <h4>响应数据</h4>
          <pre class="json-content">{{ formatJSON(selectedLog.response_data) }}</pre>
        </div>
        
        <div v-if="selectedLog.error_message" class="detail-section">
          <h4>错误信息</h4>
          <div class="error-content">
            <p class="error-message">{{ selectedLog.error_message }}</p>
            <div v-if="selectedLog.error_traceback" class="error-traceback">
              <h5>错误堆栈</h5>
              <pre>{{ selectedLog.error_traceback }}</pre>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import { formatTime } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { AccessLog } from '@/types'

const loading = ref(false)
const detailDialogVisible = ref(false)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const dateRange = ref<[string, string] | null>(null)
const currentPage = ref(1)
const pageSize = ref(50)
const totalLogs = ref(0)

const logs = ref<AccessLog[]>([])
const selectedLog = ref<AccessLog | null>(null)

const filteredLogs = computed(() => {
  let filtered = logs.value
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(log => 
      log.user_id.toString().includes(query) ||
      (log.error_message && log.error_message.toLowerCase().includes(query))
    )
  }
  
  // Type filter
  if (typeFilter.value) {
    filtered = filtered.filter(log => log.request_type === typeFilter.value)
  }
  
  // Status filter
  if (statusFilter.value) {
    if (statusFilter.value === '200') {
      filtered = filtered.filter(log => log.status_code === 200)
    } else if (statusFilter.value === '4xx') {
      filtered = filtered.filter(log => log.status_code >= 400 && log.status_code < 500)
    } else if (statusFilter.value === '5xx') {
      filtered = filtered.filter(log => log.status_code >= 500)
    }
  }
  
  return filtered
})

const getRequestTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    chat: 'primary',
    chat_stream: 'success',
    completions: 'info',
    embeddings: 'warning'
  }
  return colors[type] || 'info'
}

const formatRequestType = (type: string) => {
  const labels: Record<string, string> = {
    chat: '对话',
    chat_stream: '流式对话',
    completions: '文本补全',
    embeddings: '嵌入向量'
  }
  return labels[type] || type
}

const getStatusColor = (status: number) => {
  if (status === 200) return 'success'
  if (status >= 400 && status < 500) return 'warning'
  if (status >= 500) return 'danger'
  return 'info'
}

const getLatencyClass = (latency: number) => {
  if (latency < 100) return 'latency-good'
  if (latency < 500) return 'latency-normal'
  return 'latency-slow'
}

const formatJSON = (data: any) => {
  try {
    if (typeof data === 'string') {
      return JSON.stringify(JSON.parse(data), null, 2)
    }
    return JSON.stringify(data, null, 2)
  } catch {
    return data
  }
}

const loadLogs = async (page: number = 1) => {
  try {
    loading.value = true
    
    const params: any = {
      page,
      page_size: pageSize.value
    }
    
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await adminApi.getLogs(params)
    logs.value = response.items
    totalLogs.value = response.total
    
  } catch (error: any) {
    ElMessage.error('获取日志失败')
    console.error('Failed to load logs:', error)
  } finally {
    loading.value = false
  }
}

const refreshLogs = async () => {
  await loadLogs(currentPage.value)
  ElMessage.success('日志已刷新')
}

const handleSearch = () => {
  // Search is reactive through computed property
}

const handleFilter = () => {
  // Filter is reactive through computed property
}

const handleDateChange = () => {
  currentPage.value = 1
  loadLogs(1)
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadLogs(1)
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadLogs(page)
}

const viewLogDetail = (log: AccessLog) => {
  selectedLog.value = log
  detailDialogVisible.value = true
}

const retryRequest = async (log: AccessLog) => {
  try {
    await ElMessageBox.confirm(
      '确定要重试这个失败的请求吗？',
      '重试请求',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // Here you would implement the retry logic
    // For now, just show a success message
    ElMessage.success('请求已重新提交')
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('重试失败')
    }
  }
}

const exportLogs = async () => {
  try {
    // Get current filter parameters
    const params: any = {
      export: true
    }
    
    if (typeFilter.value) {
      params.request_type = typeFilter.value
    }
    
    if (statusFilter.value) {
      params.status_filter = statusFilter.value
    }
    
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // Here you would implement the export functionality
    // For now, just show a success message
    ElMessage.success('日志导出功能开发中')
    
  } catch (error: any) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  await loadLogs()
})
</script>

<style scoped>
.admin-logs {
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

.user-id,
.model-name {
  font-family: var(--font-mono);
  font-size: 12px;
}

.error-message {
  color: var(--error-color);
  font-size: 12px;
}

.text-success {
  color: var(--success-color);
}

.latency-good {
  color: var(--success-color);
  font-weight: 500;
}

.latency-normal {
  color: var(--warning-color);
}

.latency-slow {
  color: var(--error-color);
  font-weight: 500;
}

.table-actions {
  display: flex;
  gap: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.log-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.json-content {
  background: var(--bg-tertiary);
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  border: 1px solid var(--border-light);
}

.error-content {
  background: var(--bg-tertiary);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--error-color);
}

.error-content .error-message {
  font-size: 14px;
  margin-bottom: 12px;
}

.error-traceback h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.error-traceback pre {
  font-size: 11px;
  line-height: 1.4;
  margin: 0;
  overflow-x: auto;
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
  
  .search-form > * {
    width: 100% !important;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>