<template>
  <div class="admin-layout">
    <div class="admin-header">
      <div class="header-content">
        <div class="admin-title">
          <el-icon size="24" color="var(--primary-color)">
            <Setting />
          </el-icon>
          <h1>系统管理</h1>
        </div>
        
        <div class="header-actions">
          <el-button 
            text 
            @click="router.push('/dashboard')"
          >
            <el-icon><Back /></el-icon>
            返回主页
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="admin-nav">
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        router
        class="admin-menu"
      >
        <el-menu-item index="/admin">
          <el-icon><Odometer /></el-icon>
          概览
        </el-menu-item>
        
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          用户管理
        </el-menu-item>
        
        <el-menu-item index="/admin/models">
          <el-icon><Box /></el-icon>
          模型管理
        </el-menu-item>
        
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          系统日志
        </el-menu-item>
      </el-menu>
    </div>
    
    <div class="admin-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  return route.path
})

// Check admin permission
if (!authStore.isAdmin) {
  router.push('/dashboard')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.admin-header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  padding: 16px 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.admin-nav {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  padding: 0 24px;
}

.admin-menu {
  max-width: 1200px;
  margin: 0 auto;
  border: none;
}

.admin-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .admin-header {
    padding: 12px 16px;
  }
  
  .admin-nav {
    padding: 0 16px;
  }
  
  .admin-content {
    padding: 16px;
  }
  
  .admin-title h1 {
    font-size: 20px;
  }
}
</style>