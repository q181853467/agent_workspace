<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="chat-title">
        <h1>AI 对话</h1>
        <p>与 AI 模型进行智能对话</p>
      </div>
      
      <div class="model-selector">
        <el-select
          v-model="selectedModelName"
          placeholder="选择模型"
          @change="handleModelChange"
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
      </div>
    </div>
    
    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-icon">
            <el-icon size="48" color="var(--primary-color)">
              <ChatDotRound />
            </el-icon>
          </div>
          <h3>开始与 AI 对话</h3>
          <p>输入您的问题，AI 将为您提供智能回答</p>
          
          <div class="example-questions">
            <h4>试试这些问题：</h4>
            <div class="question-chips">
              <el-tag
                v-for="(question, index) in exampleQuestions"
                :key="index"
                class="question-chip"
                @click="sendMessage(question)"
              >
                {{ question }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="message.role"
        >
          <div class="message-avatar">
            <el-avatar v-if="message.role === 'user'" :size="32">
              <el-icon><User /></el-icon>
            </el-avatar>
            <el-avatar v-else :size="32" class="assistant-avatar">
              <el-icon><Robot /></el-icon>
            </el-avatar>
          </div>
          
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">
                {{ message.role === 'user' ? '您' : 'AI 助手' }}
              </span>
              <span class="message-time">
                {{ formatRelativeTime(message.timestamp) }}
              </span>
            </div>
            
            <div class="message-text">
              <div
                v-if="message.role === 'assistant'"
                class="assistant-message"
                v-html="formatMessage(message.content)"
              ></div>
              <div v-else class="user-message">
                {{ message.content }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Loading message -->
        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">
            <el-avatar :size="32" class="assistant-avatar">
              <el-icon><Robot /></el-icon>
            </el-avatar>
          </div>
          <div class="message-content">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入您的问题..."
            :disabled="isLoading"
            @keydown.enter.exact.prevent="handleSend"
            @keydown.enter.shift.exact="inputMessage += '\n'"
          />
          
          <div class="input-actions">
            <el-button
              type="primary"
              :disabled="!inputMessage.trim() || isLoading"
              @click="handleSend"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
        
        <div class="chat-controls">
          <el-button
            size="small"
            @click="clearMessages"
            :disabled="messages.length === 0 || isLoading"
          >
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
          
          <el-button
            size="small"
            @click="exportChat"
            :disabled="messages.length === 0"
          >
            <el-icon><Download /></el-icon>
            导出对话
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useModelsStore } from '@/store/models'
import { chatApi } from '@/api/chat'
import { formatRelativeTime, getProviderIcon, downloadFile } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ChatMessage } from '@/types'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const modelsStore = useModelsStore()

interface Message extends ChatMessage {
  timestamp: Date
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()

const selectedModelName = computed({
  get: () => modelsStore.selectedModel?.name || '',
  set: (value: string) => {
    const model = modelsStore.activeModels.find(m => m.name === value)
    if (model) {
      modelsStore.selectModel(model)
    }
  }
})

const exampleQuestions = [
  '你好，请介绍一下自己',
  '写一个 Python 快速排序算法',
  '解释一下机器学习的基本概念',
  '当前时间是多少？'
]

// Initialize markdown parser
const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return '' // use external default escaping
  }
})

const formatMessage = (content: string) => {
  return md.render(content)
}

const handleModelChange = (modelName: string) => {
  const model = modelsStore.activeModels.find(m => m.name === modelName)
  if (model) {
    modelsStore.selectModel(model)
    ElMessage.success(`已切换到模型：${model.display_name}`)
  }
}

const sendMessage = async (content?: string) => {
  const messageContent = content || inputMessage.value.trim()
  if (!messageContent || isLoading.value) return
  
  if (!modelsStore.selectedModel) {
    ElMessage.error('请先选择一个模型')
    return
  }
  
  const userMessage: Message = {
    role: 'user',
    content: messageContent,
    timestamp: new Date()
  }
  
  messages.value.push(userMessage)
  if (!content) {
    inputMessage.value = ''
  }
  
  isLoading.value = true
  
  try {
    const chatMessages: ChatMessage[] = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))
    
    const response = await chatApi.createChatCompletion({
      model: modelsStore.selectedModel.name,
      messages: chatMessages,
      temperature: 0.7,
      max_tokens: 1024
    })
    
    const assistantMessage: Message = {
      role: 'assistant',
      content: response.choices[0].message.content,
      timestamp: new Date()
    }
    
    messages.value.push(assistantMessage)
    
  } catch (error: any) {
    ElMessage.error(error.message || '请求失败')
    console.error('Chat error:', error)
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const handleSend = () => {
  sendMessage()
}

const clearMessages = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有对话记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    messages.value = []
  } catch {
    // User cancelled
  }
}

const exportChat = () => {
  const chatContent = messages.value
    .map(msg => `**${msg.role === 'user' ? '用户' : 'AI助手'}** (${msg.timestamp.toLocaleString()})\n\n${msg.content}\n\n---\n\n`)
    .join('')
  
  const filename = `chat_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.md`
  downloadFile(chatContent, filename, 'text/markdown')
  
  ElMessage.success('对话已导出')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Watch for new messages and scroll to bottom
watch(
  () => messages.value.length,
  () => {
    scrollToBottom()
  }
)

onMounted(async () => {
  await modelsStore.fetchActiveModels()
  
  // Set default model if none selected
  if (!modelsStore.selectedModel && modelsStore.activeModels.length > 0) {
    modelsStore.selectModel(modelsStore.activeModels[0])
  }
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.chat-title h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.chat-title p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.model-selector {
  min-width: 200px;
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.welcome-icon {
  margin-bottom: 16px;
}

.welcome-message h3 {
  color: var(--text-primary);
  margin-bottom: 8px;
}

.example-questions {
  margin-top: 32px;
}

.example-questions h4 {
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 14px;
}

.question-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.question-chip {
  cursor: pointer;
  transition: all 0.2s;
}

.question-chip:hover {
  background: var(--primary-color);
  color: white;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.assistant-avatar {
  background: linear-gradient(45deg, var(--primary-color), var(--primary-light));
  color: white;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.message-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

.message-text {
  background: var(--bg-tertiary);
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.user .message-text {
  background: var(--primary-color);
  color: white;
}

.assistant-message {
  color: var(--text-primary);
}

.user-message {
  color: inherit;
}

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: loading 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input {
  border-top: 1px solid var(--border-light);
  padding: 16px;
  background: var(--bg-secondary);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 12px;
}

.input-container .el-textarea {
  flex: 1;
}

.input-actions {
  flex-shrink: 0;
}

.chat-controls {
  display: flex;
  gap: 8px;
  justify-content: center;
}

@media (max-width: 768px) {
  .chat-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .question-chips {
    flex-direction: column;
    align-items: center;
  }
}
</style>

<style>
/* Global styles for markdown content */
.assistant-message pre {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.assistant-message code {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.assistant-message pre code {
  background: none;
  padding: 0;
}

.assistant-message blockquote {
  border-left: 4px solid var(--primary-color);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.assistant-message ul,
.assistant-message ol {
  padding-left: 20px;
  margin: 8px 0;
}

.assistant-message table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.assistant-message th,
.assistant-message td {
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  text-align: left;
}

.assistant-message th {
  background: var(--bg-tertiary);
  font-weight: 600;
}
</style>