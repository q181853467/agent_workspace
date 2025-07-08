import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, Token } from '@/types'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userName = computed(() => user.value?.full_name || user.value?.username || '')
  
  // Demo mode flag
  const isDemoMode = ref(true) // Enable demo mode by default
  
  // Actions
  const login = async (credentials: LoginRequest) => {
    try {
      loading.value = true
      
      // Demo mode: use mock authentication
      if (isDemoMode.value) {
        await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
        
        if (credentials.username === 'admin' && credentials.password === 'admin123') {
          const mockUser: User = {
            id: 1,
            username: 'admin',
            email: 'admin@example.com',
            full_name: '系统管理员',
            role: 'admin',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
          token.value = 'demo-admin-token-' + Date.now()
          user.value = mockUser
          localStorage.setItem('auth_token', token.value)
          localStorage.setItem('demo_user', JSON.stringify(mockUser))
          
          ElMessage.success('登录成功 (演示模式)')
          router.push('/dashboard')
          return
          
        } else if (credentials.username === 'demo_user' && credentials.password === 'demo123') {
          const mockUser: User = {
            id: 2,
            username: 'demo_user',
            email: 'demo@example.com',
            full_name: '演示用户',
            role: 'user',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
          token.value = 'demo-user-token-' + Date.now()
          user.value = mockUser
          localStorage.setItem('auth_token', token.value)
          localStorage.setItem('demo_user', JSON.stringify(mockUser))
          
          ElMessage.success('登录成功 (演示模式)')
          router.push('/dashboard')
          return
          
        } else {
          throw new Error('用户名或密码错误。请使用 admin/admin123 或 demo_user/demo123')
        }
      }
      
      // Real API mode
      const tokenData: Token = await authApi.login(credentials)
      token.value = tokenData.access_token
      
      // Store token in localStorage
      localStorage.setItem('auth_token', tokenData.access_token)
      
      // Get user info
      await getCurrentUser()
      
      ElMessage.success('登录成功')
      
      // Redirect to dashboard
      router.push('/dashboard')
      
    } catch (error: any) {
      ElMessage.error(error.message || '登录失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    router.push('/login')
    ElMessage.success('已退出登录')
  }
  
  const getCurrentUser = async () => {
    try {
      if (!token.value) return
      
      // Demo mode: load from localStorage
      if (isDemoMode.value) {
        const savedUser = localStorage.getItem('demo_user')
        if (savedUser) {
          user.value = JSON.parse(savedUser)
        }
        return
      }
      
      const userData = await authApi.getCurrentUser()
      user.value = userData
      
    } catch (error: any) {
      console.error('Failed to get user info:', error)
      // If getting user info fails, logout
      logout()
    }
  }
  
  const initAuth = async () => {
    const savedToken = localStorage.getItem('auth_token')
    if (savedToken) {
      token.value = savedToken
      
      if (isDemoMode.value) {
        const savedUser = localStorage.getItem('demo_user')
        if (savedUser) {
          user.value = JSON.parse(savedUser)
        }
      } else {
        await getCurrentUser()
      }
    }
  }
  
  const updateUser = (userData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
    }
  }
  
  return {
    // State
    user: readonly(user),
    token: readonly(token),
    loading: readonly(loading),
    isDemoMode: readonly(isDemoMode),
    
    // Getters
    isAuthenticated,
    isAdmin,
    userName,
    
    // Actions
    login,
    logout,
    getCurrentUser,
    initAuth,
    updateUser
  }
})