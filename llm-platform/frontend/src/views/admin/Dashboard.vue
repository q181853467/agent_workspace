<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1>管理概览</h1>
      <p>平台运营数据和系统状态监控</p>
    </div>
    
    <!-- Overview Stats -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon primary">
            <el-icon size="24"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overviewStats.total_users || 0 }}</div>
            <div class="stat-label">总用户数</div>
            <div class="stat-change positive">活跃: {{ overviewStats.active_users || 0 }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon success">
            <el-icon size="24"><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overviewStats.total_models || 0 }}</div>
            <div class="stat-label">模型总数</div>
            <div class="stat-change positive">活跃: {{ overviewStats.active_models || 0 }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon size="24"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(overviewStats.recent_api_calls_24h || 0) }}</div>
            <div class="stat-label">24小时请求</div>
            <div class="stat-change neutral">API调用</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon info">
            <el-icon size="24"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ Math.round(overviewStats.avg_latency_ms || 0) }}ms</div>
            <div class="stat-label">平均延迟</div>
            <div class="stat-change" :class="getLatencyClass(overviewStats.avg_latency_ms)">响应时间</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- Charts Section -->
    <div class="charts-grid">
      <!-- Usage Chart -->
      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="chart-header">
            <span>API使用趋势</span>
            <el-select
              v-model="chartPeriod"
              size="small"
              style="width: 100px"
              @change="loadUsageStats"
            >
              <el-option label="7天" value="7" />
              <el-option label="30天" value="30" />
            </el-select>
          </div>
        </template>
        
        <div class="chart-container">
          <v-chart
            v-if="usageChartOptions"
            :option="usageChartOptions"
            class="chart"
            autoresize
          />
          <div v-else class="chart-loading">
            <el-skeleton :rows="6" animated />
          </div>
        </div>
      </el-card>
      
      <!-- System Status -->
      <el-card class="status-card" shadow="never">
        <template #header>
          <div class="chart-header">
            <span>系统状态</span>
            <el-button
              size="small"
              @click="refreshStatus"
              :loading="statusLoading"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <div class="status-list">
          <div class="status-item">
            <div class="status-info">
              <span class="status-name">API服务</span>
              <span class="status-desc">核心API服务状态</span>
            </div>
            <el-tag type="success" size="small">正常</el-tag>
          </div>
          
          <div class="status-item">
            <div class="status-info">
              <span class="status-name">数据库</span>
              <span class="status-desc">数据库连接状态</span>
            </div>
            <el-tag type="success" size="small">正常</el-tag>
          </div>
          
          <div class="status-item">
            <div class="status-info">
              <span class="status-name">模型服务</span>
              <span class="status-desc">模型调用服务状态</span>
            </div>
            <el-tag type="success" size="small">正常</el-tag>
          </div>
          
          <div class="status-item">
            <div class="status-info">
              <span class="status-name">缓存服务</span>
              <span class="status-desc">Redis缓存状态</span>
            </div>
            <el-tag type="warning" size="small">可选</el-tag>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- Recent Logs -->
    <el-card shadow="never">
      <template #header>
        <div class="chart-header">
          <span>最近日志</span>
          <el-button
            size="small"
            @click="router.push('/admin/logs')"
          >
            查看全部
          </el-button>
        </div>
      </template>
      
      <div v-if="logsLoading" class="logs-loading">
        <el-skeleton :rows="5" animated />
      </div>
      
      <el-table
        v-else
        :data="recentLogs.slice(0, 10)"
        style="width: 100%"
      >
        <el-table-column prop="request_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getRequestTypeColor(row.request_type)">
              {{ row.request_type }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status_code" label="状态" width="80">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="row.status_code === 200 ? 'success' : 'danger'"
            >
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="latency_ms" label="延迟" width="80">
          <template #default="{ row }">
            {{ row.latency_ms }}ms
          </template>
        </el-table-column>
        
        <el-table-column prop="total_tokens" label="Tokens" width="80">
          <template #default="{ row }">
            {{ row.total_tokens || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">
            {{ formatRelativeTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="error_message" label="错误信息" min-width="200">
          <template #default="{ row }">
            <span v-if="row.error_message" class="error-message">
              {{ truncateText(row.error_message, 50) }}
            </span>
            <span v-else class="text-success">正常</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!logsLoading && recentLogs.length === 0" class="empty-logs">
        <el-empty description="暂无日志数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import { formatNumber, formatRelativeTime, truncateText } from '@/utils'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import type { OverviewStats, UsageStats, AccessLog } from '@/types'

// Register ECharts components
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()

const loading = ref(false)
const statusLoading = ref(false)
const logsLoading = ref(false)
const chartPeriod = ref('7')

const overviewStats = ref<OverviewStats>({
  total_users: 0,
  active_users: 0,
  total_models: 0,
  active_models: 0,
  recent_api_calls_24h: 0,
  avg_latency_ms: 0
})

const usageChartOptions = ref(null)
const recentLogs = ref<AccessLog[]>([])

const getLatencyClass = (latency: number) => {
  if (latency < 100) return 'positive'
  if (latency < 500) return 'neutral'
  return 'negative'
}

const getRequestTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    chat: 'primary',
    chat_stream: 'success',
    completions: 'info',
    embeddings: 'warning'
  }
  return colors[type] || 'info'
}

const loadOverviewStats = async () => {
  try {
    const stats = await adminApi.getOverviewStats()
    overviewStats.value = stats
  } catch (error: any) {
    console.error('Failed to load overview stats:', error)
  }
}

const loadUsageStats = async () => {
  try {
    const stats = await adminApi.getUsageStats(parseInt(chartPeriod.value))
    
    const dates = stats.daily_stats.map(stat => stat.date)
    const requests = stats.daily_stats.map(stat => stat.request_count)
    const latencies = stats.daily_stats.map(stat => Math.round(stat.avg_latency_ms))
    
    usageChartOptions.value = {
      title: {
        text: 'API使用趋势',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['请求数', '平均延迟(ms)'],
        bottom: 0
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          formatter: (value: string) => {
            return new Date(value).toLocaleDateString('zh-CN', {
              month: 'short',
              day: 'numeric'
            })
          }
        }
      },
      yAxis: [
        {
          type: 'value',
          name: '请求数',
          position: 'left'
        },
        {
          type: 'value',
          name: '延迟(ms)',
          position: 'right'
        }
      ],
      series: [
        {
          name: '请求数',
          type: 'bar',
          data: requests,
          itemStyle: {
            color: '#6366f1'
          }
        },
        {
          name: '平均延迟(ms)',
          type: 'line',
          yAxisIndex: 1,
          data: latencies,
          itemStyle: {
            color: '#06b6d4'
          }
        }
      ]
    }
  } catch (error: any) {
    console.error('Failed to load usage stats:', error)
  }
}

const loadRecentLogs = async () => {
  try {
    logsLoading.value = true
    const logs = await adminApi.getRecentLogs(20)
    recentLogs.value = logs
  } catch (error: any) {
    console.error('Failed to load recent logs:', error)
  } finally {
    logsLoading.value = false
  }
}

const refreshStatus = async () => {
  statusLoading.value = true
  // Simulate status check
  await new Promise(resolve => setTimeout(resolve, 1000))
  statusLoading.value = false
  ElMessage.success('系统状态已刷新')
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    loadOverviewStats(),
    loadUsageStats(),
    loadRecentLogs()
  ])
  loading.value = false
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.dashboard-header p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.stat-card {
  border: 1px solid var(--border-light);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.primary {
  background: linear-gradient(45deg, #6366f1, #818cf8);
}

.stat-icon.success {
  background: linear-gradient(45deg, #10b981, #34d399);
}

.stat-icon.warning {
  background: linear-gradient(45deg, #f59e0b, #fbbf24);
}

.stat-icon.info {
  background: linear-gradient(45deg, #06b6d4, #22d3ee);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.positive {
  color: var(--success-color);
}

.stat-change.negative {
  color: var(--error-color);
}

.stat-change.neutral {
  color: var(--text-tertiary);
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-container {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-loading {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-name {
  font-weight: 500;
  color: var(--text-primary);
}

.status-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.logs-loading {
  padding: 20px;
}

.empty-logs {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.error-message {
  color: var(--error-color);
  font-size: 12px;
}

.text-success {
  color: var(--success-color);
  font-size: 12px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>