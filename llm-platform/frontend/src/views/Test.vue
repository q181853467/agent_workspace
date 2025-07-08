<template>
  <div class="test-page">
    <div class="page-header">
      <div class="header-content">
        <h1>API 测试</h1>
        <p>测试 LLM Platform API 的功能和性能</p>
      </div>
    </div>
    
    <div class="test-content">
      <!-- API Configuration -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>API 配置</span>
          </div>
        </template>
        
        <el-form :model="apiConfig" label-width="80px" class="config-form">
          <el-form-item label="模型">
            <el-select
              v-model="apiConfig.model"
              placeholder="选择模型"
              style="width: 100%"
            >
              <el-option
                v-for="model in modelsStore.activeModels"
                :key="model.id"
                :label="model.display_name"
                :value="model.name"
              >
                <div class="model-option">
                  <span>{{ getProviderIcon(model.provider) }} {{ model.display_name }}</span>
                  <el-tag size="small" type="info">{{ model.provider }}</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="Temperature">
                <el-slider
                  v-model="apiConfig.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  show-input
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Max Tokens">
                <el-input-number
                  v-model="apiConfig.max_tokens"
                  :min="1"
                  :max="4096"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="流式">
            <el-switch
              v-model="apiConfig.stream"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- Test Input -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>测试输入</span>
            <div class="header-actions">
              <el-button
                size="small"
                @click="loadExample"
              >
                加载示例
              </el-button>
              <el-button
                size="small"
                @click="clearInput"
              >
                清空
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="test-input">
          <el-input
            v-model="testPrompt"
            type="textarea"
            :rows="6"
            placeholder="输入您要测试的提示词..."
            maxlength="2000"
            show-word-limit
          />
          
          <div class="input-actions">
            <el-button
              type="primary"
              :loading="testing"
              :disabled="!testPrompt.trim() || !apiConfig.model"
              @click="runTest"
            >
              <el-icon><CaretRight /></el-icon>
              运行测试
            </el-button>
            
            <el-button
              :disabled="!currentTest"
              @click="exportTest"
            >
              <el-icon><Download /></el-icon>
              导出结果
            </el-button>
          </div>
        </div>
      </el-card>
      
      <!-- Test Results -->
      <el-card v-if="currentTest" shadow="never">
        <template #header>
          <div class="card-header">
            <span>测试结果</span>
            <div class="test-status">
              <el-tag
                :type="currentTest.status === 'success' ? 'success' : 'danger'"
                size="small"
              >
                {{ currentTest.status === 'success' ? '成功' : '失败' }}
              </el-tag>
              <span class="duration">{{ currentTest.duration }}ms</span>
            </div>
          </div>
        </template>
        
        <div class="test-results">
          <!-- Request Info -->
          <div class="result-section">
            <h4>请求信息</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="模型">
                {{ currentTest.request.model }}
              </el-descriptions-item>
              <el-descriptions-item label="Temperature">
                {{ currentTest.request.temperature }}
              </el-descriptions-item>
              <el-descriptions-item label="Max Tokens">
                {{ currentTest.request.max_tokens }}
              </el-descriptions-item>
              <el-descriptions-item label="流式">
                {{ currentTest.request.stream ? '是' : '否' }}
              </el-descriptions-item>
              <el-descriptions-item label="请求时间" :span="2">
                {{ formatTime(currentTest.timestamp) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- Response -->
          <div class="result-section">
            <h4>响应结果</h4>
            <div v-if="currentTest.status === 'success'" class="response-content">
              <div class="response-text" v-html="formatMessage(currentTest.response.content)"></div>
              
              <div v-if="currentTest.response.usage" class="usage-info">
                <h5>Token 使用情况</h5>
                <div class="usage-stats">
                  <div class="usage-item">
                    <span class="label">输入 Tokens:</span>
                    <span class="value">{{ currentTest.response.usage.prompt_tokens }}</span>
                  </div>
                  <div class="usage-item">
                    <span class="label">输出 Tokens:</span>
                    <span class="value">{{ currentTest.response.usage.completion_tokens }}</span>
                  </div>
                  <div class="usage-item">
                    <span class="label">总 Tokens:</span>
                    <span class="value">{{ currentTest.response.usage.total_tokens }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="error-content">
              <el-alert
                type="error"
                :title="currentTest.error"
                show-icon
                :closable="false"
              />
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- Test History -->
      <el-card v-if="testHistory.length > 0" shadow="never">
        <template #header>
          <div class="card-header">
            <span>测试历史</span>
            <el-button
              size="small"
              @click="clearHistory"
            >
              清空历史
            </el-button>
          </div>
        </template>
        
        <div class="history-list">
          <div
            v-for="(test, index) in testHistory"
            :key="index"
            class="history-item"
            @click="loadHistoryTest(test)"
          >
            <div class="history-info">
              <div class="history-header">
                <span class="model">{{ test.request.model }}</span>
                <el-tag
                  :type="test.status === 'success' ? 'success' : 'danger'"
                  size="small"
                >
                  {{ test.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </div>
              <div class="history-prompt">{{ truncateText(test.request.prompt, 100) }}</div>
              <div class="history-meta">
                <span>{{ formatRelativeTime(test.timestamp) }}</span>
                <span>·</span>
                <span>{{ test.duration }}ms</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useModelsStore } from '@/store/models'
import { chatApi } from '@/api/chat'
import { formatTime, formatRelativeTime, getProviderIcon, truncateText, downloadFile } from '@/utils'
import { ElMessage } from 'element-plus'
import type { ChatCompletionRequest, ChatCompletionResponse } from '@/types'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const modelsStore = useModelsStore()

interface TestResult {
  request: {
    model: string
    prompt: string
    temperature: number
    max_tokens: number
    stream: boolean
  }
  response?: {
    content: string
    usage?: {
      prompt_tokens: number
      completion_tokens: number
      total_tokens: number
    }
  }
  status: 'success' | 'error'
  error?: string
  duration: number
  timestamp: Date
}

const testing = ref(false)
const currentTest = ref<TestResult | null>(null)
const testHistory = ref<TestResult[]>([])
const testPrompt = ref('')

const apiConfig = reactive({
  model: '',
  temperature: 0.7,
  max_tokens: 1024,
  stream: false
})

// Initialize markdown parser
const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

const formatMessage = (content: string) => {
  return md.render(content)
}

const loadExample = () => {
  const examples = [
    '请编写一个 Python 函数，计算斐波那契数列的第n项。',
    '解释一下机器学习中的梯度下降算法。',
    '你好！请介绍一下你的能力和特点。',
    '请写一个关于React Hooks的简单教程。',
    '分析一下人工智能在未来十年的发展趋势。'
  ]
  
  const randomExample = examples[Math.floor(Math.random() * examples.length)]
  testPrompt.value = randomExample
}

const clearInput = () => {
  testPrompt.value = ''
}

const runTest = async () => {
  if (!testPrompt.value.trim() || !apiConfig.model) {
    ElMessage.error('请输入测试内容并选择模型')
    return
  }
  
  testing.value = true
  const startTime = Date.now()
  
  const testRequest = {
    model: apiConfig.model,
    prompt: testPrompt.value,
    temperature: apiConfig.temperature,
    max_tokens: apiConfig.max_tokens,
    stream: apiConfig.stream
  }
  
  try {
    const chatRequest: ChatCompletionRequest = {
      model: apiConfig.model,
      messages: [
        { role: 'user', content: testPrompt.value }
      ],
      temperature: apiConfig.temperature,
      max_tokens: apiConfig.max_tokens,
      stream: apiConfig.stream
    }
    
    const response = await chatApi.createChatCompletion(chatRequest)
    const duration = Date.now() - startTime
    
    const testResult: TestResult = {
      request: testRequest,
      response: {
        content: response.choices[0].message.content,
        usage: response.usage
      },
      status: 'success',
      duration,
      timestamp: new Date()
    }
    
    currentTest.value = testResult
    testHistory.value.unshift(testResult)
    
    // Keep only last 10 tests
    if (testHistory.value.length > 10) {
      testHistory.value = testHistory.value.slice(0, 10)
    }
    
    ElMessage.success(`测试完成，耗时 ${duration}ms`)
    
  } catch (error: any) {
    const duration = Date.now() - startTime
    
    const testResult: TestResult = {
      request: testRequest,
      status: 'error',
      error: error.message || '请求失败',
      duration,
      timestamp: new Date()
    }
    
    currentTest.value = testResult
    testHistory.value.unshift(testResult)
    
    ElMessage.error('测试失败：' + (error.message || '未知错误'))
    
  } finally {
    testing.value = false
  }
}

const exportTest = () => {
  if (!currentTest.value) return
  
  const test = currentTest.value
  const content = `# API 测试结果

## 请求信息
- 模型: ${test.request.model}
- Temperature: ${test.request.temperature}
- Max Tokens: ${test.request.max_tokens}
- 流式: ${test.request.stream ? '是' : '否'}
- 测试时间: ${formatTime(test.timestamp)}
- 耗时: ${test.duration}ms

## 输入内容
${test.request.prompt}

## 响应结果
${test.status === 'success' ? test.response!.content : `错误: ${test.error}`}

${test.status === 'success' && test.response?.usage ? `## Token 使用
- 输入 Tokens: ${test.response.usage.prompt_tokens}
- 输出 Tokens: ${test.response.usage.completion_tokens}
- 总 Tokens: ${test.response.usage.total_tokens}` : ''}
`
  
  const filename = `api_test_${test.timestamp.toISOString().slice(0, 19).replace(/:/g, '-')}.md`
  downloadFile(content, filename, 'text/markdown')
  
  ElMessage.success('测试结果已导出')
}

const loadHistoryTest = (test: TestResult) => {
  currentTest.value = test
  testPrompt.value = test.request.prompt
  apiConfig.model = test.request.model
  apiConfig.temperature = test.request.temperature
  apiConfig.max_tokens = test.request.max_tokens
  apiConfig.stream = test.request.stream
}

const clearHistory = () => {
  testHistory.value = []
  ElMessage.success('测试历史已清空')
}

onMounted(async () => {
  await modelsStore.fetchActiveModels()
  
  // Set default model
  if (modelsStore.activeModels.length > 0) {
    apiConfig.model = modelsStore.selectedModel?.name || modelsStore.activeModels[0].name
  }
})
</script>

<style scoped>
.test-page {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-header p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.config-form {
  max-width: 600px;
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.test-input {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-actions {
  display: flex;
  gap: 12px;
}

.test-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.duration {
  font-size: 14px;
  color: var(--text-secondary);
}

.test-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-section h4 {
  margin-bottom: 12px;
  color: var(--text-primary);
}

.response-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.response-text {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
  min-height: 100px;
  line-height: 1.6;
}

.usage-info h5 {
  margin-bottom: 8px;
  color: var(--text-primary);
}

.usage-stats {
  display: flex;
  gap: 24px;
}

.usage-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.usage-item .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.usage-item .value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--primary-color);
  background: var(--bg-tertiary);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-header .model {
  font-weight: 600;
  color: var(--text-primary);
}

.history-prompt {
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.history-meta {
  font-size: 12px;
  color: var(--text-tertiary);
  display: flex;
  gap: 8px;
  align-items: center;
}

@media (max-width: 768px) {
  .usage-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .input-actions {
    flex-direction: column;
  }
}
</style>

<style>
/* Global styles for test response markdown content */
.response-text pre {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.response-text code {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.response-text pre code {
  background: none;
  padding: 0;
}

.response-text blockquote {
  border-left: 4px solid var(--primary-color);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.response-text ul,
.response-text ol {
  padding-left: 20px;
  margin: 8px 0;
}

.response-text table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.response-text th,
.response-text td {
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  text-align: left;
}

.response-text th {
  background: var(--bg-secondary);
  font-weight: 600;
}
</style>