<template>
  <div class="profile-page">
    <div class="page-header">
      <h1>个人资料</h1>
      <p>管理您的个人信息和账户设置</p>
    </div>
    
    <div class="profile-content">
      <!-- User Info Card -->
      <el-card class="user-info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <div class="user-info">
          <div class="avatar-section">
            <el-avatar :size="80">
              <el-icon size="40"><User /></el-icon>
            </el-avatar>
            <div class="user-details">
              <h3>{{ authStore.user?.full_name || authStore.user?.username }}</h3>
              <p>{{ authStore.user?.email }}</p>
              <el-tag :type="authStore.isAdmin ? 'danger' : 'primary'" size="small">
                {{ authStore.isAdmin ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- Edit Profile Form -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>编辑资料</span>
          </div>
        </template>
        
        <el-form
          ref="profileFormRef"
          :model="profileForm"
          :rules="profileRules"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="profileForm.username"
              placeholder="请输入用户名"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input
              v-model="profileForm.email"
              type="email"
              placeholder="请输入邮箱"
              maxlength="255"
            />
          </el-form-item>
          
          <el-form-item label="姓名" prop="full_name">
            <el-input
              v-model="profileForm.full_name"
              placeholder="请输入姓名"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="个人描述" prop="description">
            <el-input
              v-model="profileForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入个人描述"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="updating"
              @click="updateProfile"
            >
              保存修改
            </el-button>
            <el-button @click="resetForm">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- Change Password Card -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>修改密码</span>
          </div>
        </template>
        
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
          class="password-form"
        >
          <el-form-item label="新密码" prop="password">
            <el-input
              v-model="passwordForm.password"
              type="password"
              placeholder="请输入新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="changingPassword"
              @click="changePassword"
            >
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- Account Stats -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>账户统计</span>
          </div>
        </template>
        
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.apiKeysCount }}</div>
            <div class="stat-label">API 密钥</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ formatTime(authStore.user?.created_at || '', 'YYYY-MM-DD') }}</div>
            <div class="stat-label">注册时间</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ formatTime(authStore.user?.updated_at || '', 'YYYY-MM-DD') }}</div>
            <div class="stat-label">最后更新</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { apiKeysApi } from '@/api/apiKeys'
import { formatTime, isValidEmail } from '@/utils'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { UserUpdate } from '@/types'

const authStore = useAuthStore()

const updating = ref(false)
const changingPassword = ref(false)
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const profileForm = reactive<UserUpdate>({
  username: '',
  email: '',
  full_name: '',
  description: ''
})

const passwordForm = reactive({
  password: '',
  confirmPassword: ''
})

const stats = reactive({
  apiKeysCount: 0
})

const validateEmail = (rule: any, value: string, callback: any) => {
  if (value && !isValidEmail(value)) {
    callback(new Error('请输入正确的邮箱地址'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const profileRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  full_name: [
    { max: 100, message: '姓名长度不能超过 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过 500 个字符', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少需蝨6位字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const initForm = () => {
  const user = authStore.user
  if (user) {
    profileForm.username = user.username
    profileForm.email = user.email
    profileForm.full_name = user.full_name || ''
    profileForm.description = user.description || ''
  }
}

const resetForm = () => {
  initForm()
  profileFormRef.value?.clearValidate()
}

const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        updating.value = true
        
        // TODO: Implement update profile API call
        // const updatedUser = await userApi.updateProfile(profileForm)
        // authStore.updateUser(updatedUser)
        
        ElMessage.success('个人资料已更新')
        
      } catch (error: any) {
        ElMessage.error(error.message || '更新失败')
      } finally {
        updating.value = false
      }
    }
  })
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        changingPassword.value = true
        
        // TODO: Implement change password API call
        // await userApi.changePassword({
        //   password: passwordForm.password
        // })
        
        ElMessage.success('密码已修改')
        
        // Reset password form
        passwordForm.password = ''
        passwordForm.confirmPassword = ''
        passwordFormRef.value?.resetFields()
        
      } catch (error: any) {
        ElMessage.error(error.message || '密码修改失败')
      } finally {
        changingPassword.value = false
      }
    }
  })
}

const loadStats = async () => {
  try {
    const apiKeys = await apiKeysApi.getApiKeys()
    stats.apiKeysCount = apiKeys.length
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(async () => {
  initForm()
  await loadStats()
})
</script>

<style scoped>
.profile-page {
  max-width: 800px;
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

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  font-weight: 600;
  color: var(--text-primary);
}

.user-info-card {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  color: white;
}

.user-info-card :deep(.el-card__header) {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.user-info-card .card-header {
  color: white;
}

.user-info {
  padding: 16px 0;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-details h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.user-details p {
  font-size: 16px;
  margin: 0 0 12px 0;
  color: rgba(255, 255, 255, 0.9);
}

.profile-form,
.password-form {
  max-width: 500px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 24px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>