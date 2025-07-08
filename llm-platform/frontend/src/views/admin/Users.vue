<template>
  <div class="admin-users">
    <div class="page-header">
      <div class="header-content">
        <h1>用户管理</h1>
        <p>管理系统用户，查看用户信息和状态</p>
      </div>
      
      <div class="header-actions">
        <el-button @click="refreshUsers" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建用户
        </el-button>
      </div>
    </div>
    
    <!-- Search and Filter -->
    <el-card shadow="never" class="search-card">
      <div class="search-form">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户名或邮箱"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="statusFilter"
          placeholder="用户状态"
          clearable
          style="width: 150px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="活跃" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
        
        <el-select
          v-model="roleFilter"
          placeholder="用户角色"
          clearable
          style="width: 150px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
      </div>
    </el-card>
    
    <!-- Users Table -->
    <el-card shadow="never">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="8" animated />
      </div>
      
      <el-table
        v-else
        :data="filteredUsers"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="username" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="user-details">
                <div class="username">{{ row.username }}</div>
                <div class="full-name">{{ row.full_name || '-' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.role === 'admin' ? 'danger' : 'primary'"
              size="small"
            >
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
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
        
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at, 'YYYY-MM-DD') }}
          </template>
        </el-table-column>
        
        <el-table-column prop="updated_at" label="最后更新" width="160">
          <template #default="{ row }">
            {{ formatRelativeTime(row.updated_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="编辑">
                <el-button
                  size="small"
                  text
                  @click="editUser(row)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip :content="row.is_active ? '停用' : '启用'">
                <el-button
                  size="small"
                  text
                  :type="row.is_active ? 'warning' : 'success'"
                  @click="toggleUserStatus(row)"
                >
                  <el-icon><Switch /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="删除">
                <el-button
                  size="small"
                  text
                  type="danger"
                  @click="deleteUser(row)"
                  :disabled="row.id === authStore.user?.id"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无用户数据" />
        </template>
      </el-table>
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑用户' : '创建用户'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="isEditing"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱"
            maxlength="255"
          />
        </el-form-item>
        
        <el-form-item v-if="!isEditing" label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input
            v-model="form.full_name"
            placeholder="请输入姓名（可选）"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select
            v-model="form.role"
            placeholder="选择用户角色"
            style="width: 100%"
          >
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="活跃"
            inactive-text="停用"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="用户描述（可选）"
            maxlength="500"
            show-word-limit
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { adminApi } from '@/api/admin'
import { formatTime, formatRelativeTime, isValidEmail } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { User, UserCreate, UserUpdate } from '@/types'

const authStore = useAuthStore()

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const roleFilter = ref('')

const users = ref<User[]>([])
const currentEditingUser = ref<User | null>(null)

const formRef = ref<FormInstance>()
const form = reactive<UserCreate & { is_active?: boolean }>({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: 'user',
  description: '',
  is_active: true
})

const validateEmail = (rule: any, value: string, callback: any) => {
  if (value && !isValidEmail(value)) {
    callback(new Error('请输入正确的邮箱地址'))
  } else {
    callback()
  }
}

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少需要6位字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
}

const filteredUsers = computed(() => {
  let filtered = users.value
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      (user.full_name && user.full_name.toLowerCase().includes(query))
    )
  }
  
  // Status filter
  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(user => user.is_active === isActive)
  }
  
  // Role filter
  if (roleFilter.value) {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }
  
  return filtered
})

const loadUsers = async () => {
  try {
    loading.value = true
    users.value = await adminApi.getUsers()
  } catch (error: any) {
    ElMessage.error('获取用户列表失败')
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const refreshUsers = async () => {
  await loadUsers()
  ElMessage.success('用户列表已刷新')
}

const handleSearch = () => {
  // Search is reactive through computed property
}

const handleFilter = () => {
  // Filter is reactive through computed property
}

const showCreateDialog = () => {
  isEditing.value = false
  dialogVisible.value = true
}

const editUser = (user: User) => {
  isEditing.value = true
  currentEditingUser.value = user
  
  form.username = user.username
  form.email = user.email
  form.full_name = user.full_name || ''
  form.role = user.role
  form.description = user.description || ''
  form.is_active = user.is_active
  
  dialogVisible.value = true
}

const resetForm = () => {
  form.username = ''
  form.email = ''
  form.password = ''
  form.full_name = ''
  form.role = 'user'
  form.description = ''
  form.is_active = true
  currentEditingUser.value = null
  formRef.value?.resetFields()
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        
        if (isEditing.value && currentEditingUser.value) {
          // Update user
          const updateData: UserUpdate = {
            email: form.email,
            full_name: form.full_name,
            role: form.role,
            description: form.description,
            is_active: form.is_active
          }
          
          await adminApi.updateUser(currentEditingUser.value.id, updateData)
          ElMessage.success('用户信息已更新')
        } else {
          // Create user
          await adminApi.createUser({
            username: form.username,
            email: form.email,
            password: form.password,
            full_name: form.full_name,
            role: form.role,
            description: form.description
          })
          ElMessage.success('用户创建成功')
        }
        
        dialogVisible.value = false
        await loadUsers()
        
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const toggleUserStatus = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要${user.is_active ? '停用' : '启用'}用户 "${user.username}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await adminApi.updateUser(user.id, {
      is_active: !user.is_active
    })
    
    ElMessage.success(`用户已${user.is_active ? '停用' : '启用'}`)
    await loadUsers()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const deleteUser = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '危险操作',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    await adminApi.deleteUser(user.id)
    ElMessage.success('用户已删除')
    await loadUsers()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(async () => {
  await loadUsers()
})
</script>

<style scoped>
.admin-users {
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

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  color: var(--text-primary);
}

.full-name {
  font-size: 12px;
  color: var(--text-secondary);
}

.table-actions {
  display: flex;
  gap: 4px;
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