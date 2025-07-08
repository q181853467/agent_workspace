<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <el-icon size="48" color="var(--primary-color)">
            <Box />
          </el-icon>
        </div>
        <h1 class="title">LLM Platform</h1>
        <p class="subtitle">企业级大模型克隆平台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="authStore.loading"
            @click="handleLogin"
          >
            <span v-if="!authStore.loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="demo-accounts">
        <el-divider>演示账号</el-divider>
        <div class="demo-buttons">
          <el-button
            size="small"
            @click="setDemoAccount('admin')"
          >
            管理员账号
          </el-button>
          <el-button
            size="small"
            @click="setDemoAccount('user')"
          >
            普通用户
          </el-button>
        </div>
        <div class="demo-info">
          <el-text size="small" type="info">
            管理员: admin / admin123<br>
            用户: demo / demo123
          </el-text>
        </div>
      </div>
    </div>
    
    <div class="login-footer">
      <p>&copy; 2025 LLM Platform. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import type { FormInstance } from 'element-plus'
import type { LoginRequest } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()

const loginForm = reactive<LoginRequest>({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少需蝨6位字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await authStore.login(loginForm)
        
        // Redirect to original page or dashboard
        const redirect = route.query.redirect as string
        router.push(redirect || '/dashboard')
        
      } catch (error) {
        console.error('Login failed:', error)
      }
    }
  })
}

const setDemoAccount = (type: 'admin' | 'user') => {
  if (type === 'admin') {
    loginForm.username = 'admin'
    loginForm.password = 'admin123'
  } else {
    loginForm.username = 'demo'
    loginForm.password = 'demo123'
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 16px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(45deg, var(--primary-color), var(--primary-light));
  border: none;
}

.demo-accounts {
  text-align: center;
}

.demo-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 16px;
}

.demo-info {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
}

.login-footer {
  margin-top: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
    margin: 0 16px;
  }
  
  .demo-buttons {
    flex-direction: column;
  }
}
</style>