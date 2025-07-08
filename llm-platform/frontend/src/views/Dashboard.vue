<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>欢迎回来，{{ authStore.userName }}！</h1>
      <p>这里是您的个人仪表板</p>
    </div>
    
    <!-- Overview Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon primary">
            <el-icon size="24"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(stats.total_requests || 0) }}</div>
            <div class="stat-label">总请求数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon success">
            <el-icon size="24"><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ modelsStore.activeModels.length }}</div>
            <div class="stat-label">可用模型</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon size="24"><Key /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ apiKeysCount }}</div>
            <div class="stat-label">API 密钥</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon info">
            <el-icon size="24"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avg_latency || 0 }}ms</div>
            <div class="stat-label">平均延迟</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Quick Actions -->
      <el-card class="quick-actions" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>快速操作</span>
          </div>
        </template>
        
        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            @click="router.push('/chat')"
          >
            <el-icon><ChatDotRound /></el-icon>
            开始对话
          </el-button>
          
          <el-button
            size="large"
            @click="router.push('/api-keys')"
          >
            <el-icon><Key /></el-icon>
            创建 API 密钥
          </el-button>
          
          <el-button
            size="large"
            @click="router.push('/test')"
          >
            <el-icon><Monitor /></el-icon>
            API 测试
          </el-button>
          
          <el-button
            v-if="authStore.isAdmin"
            size="large"
            @click="router.push('/admin')"
          >
            <el-icon><Setting /></el-icon>
            系统管理
          </el-button>
        </div>
      </el-card>
      
      <!-- Recent Models -->
      <el-card class="recent-models" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>可用模型</span>
            <el-button
              text
              type="primary"
              @click="router.push('/models')"
            >
              查看全部
            </el-button>
          </div>
        </template>
        
        <div v-if="modelsStore.loading" class="loading">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else class="models-list">
          <div
            v-for="model in modelsStore.activeModels.slice(0, 5)"
            :key="model.id"
            class="model-item"
            @click="selectModel(model)"
          >
            <div class="model-info">
              <div class="model-name">{{ model.display_name }}</div>
              <div class="model-provider">{{ getProviderIcon(model.provider) }} {{ model.provider }}</div>
            </div>
            <div class="model-status">
              <el-tag
                :type="model.is_active ? 'success' : 'danger'"
                size="small"
              >
                {{ model.is_active ? '活跃' : '停用' }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- Usage Chart -->
      <el-card class="usage-chart" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>使用统计</span>
            <el-select
              v-model="chartPeriod"
              size="small"
              style="width: 100px"
              @change="updateChart"
            >
              <el-option label="7天" value="7" />
              <el-option label="30天" value="30" />
            </el-select>
          </div>
        </template>
        
        <div class="chart-container">
          <v-chart
            v-if="chartOptions"
            :option="chartOptions"
            class="chart"
            autoresize
          />
          <div v-else class="no-data">
            <el-empty description="暂无数据" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useModelsStore } from '@/store/models'
import { apiKeysApi } from '@/api/apiKeys'
import { adminApi } from '@/api/admin'
import { formatNumber, getProviderIcon } from '@/utils'
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
const authStore = useAuthStore()
const modelsStore = useModelsStore()

const stats = ref({
  total_requests: 0,
  avg_latency: 0
})
const apiKeysCount = ref(0)
const chartPeriod = ref('7')
const chartOptions = ref(null)

const selectModel = (model: any) => {
  modelsStore.selectModel(model)
  ElMessage.success(`已选择模型：${model.display_name}`)
  router.push('/chat')
}

const loadStats = async () => {
  try {
    // Load API keys count
    const apiKeys = await apiKeysApi.getApiKeys()
    apiKeysCount.value = apiKeys.length
    
    // Load usage stats if admin
    if (authStore.isAdmin) {
      const overviewStats = await adminApi.getOverviewStats()
      stats.value = {
        total_requests: overviewStats.recent_api_calls_24h,
        avg_latency: Math.round(overviewStats.avg_latency_ms)
      }
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const updateChart = async () => {
  try {
    if (!authStore.isAdmin) return
    
    const usageStats = await adminApi.getUsageStats(parseInt(chartPeriod.value))
    
    const dates = usageStats.daily_stats.map(stat => stat.date)
    const requests = usageStats.daily_stats.map(stat => stat.request_count)
    const latencies = usageStats.daily_stats.map(stat => Math.round(stat.avg_latency_ms))
    
    chartOptions.value = {
      title: {
        text: '请求统计',
        left: 'center',
        textStyle: {
          fontSize: 14,
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
  } catch (error) {
    console.error('Failed to load chart data:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    modelsStore.fetchActiveModels(),
    loadStats()
  ])
  
  if (authStore.isAdmin) {
    updateChart()
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-header h1 {
  font-size: 32px;
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
  margin-bottom: 24px;
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
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.usage-chart {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.models-list {
  space-y: 12px;
}

.model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.model-item:hover {
  border-color: var(--primary-color);
  background: var(--bg-tertiary);
}

.model-name {
  font-weight: 600;
  color: var(--text-primary);
}

.model-provider {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.chart-container {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

.loading,
.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
}
</style>