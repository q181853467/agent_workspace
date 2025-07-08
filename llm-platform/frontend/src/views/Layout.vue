<template>
  <el-container class="app-layout">
    <!-- Sidebar -->
    <el-aside 
      :width="sidebarCollapsed ? '64px' : '240px'"
      class="sidebar"
    >
      <div class="sidebar-header">
        <div v-if="!sidebarCollapsed" class="logo">
          <el-icon size="24" color="var(--primary-color)">
            <Box />
          </el-icon>
          <span class="logo-text">LLM Platform</span>
        </div>
        <el-icon v-else size="24" color="var(--primary-color)">
          <Box />
        </el-icon>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="sidebarCollapsed"
        :unique-opened="true"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Dashboard /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>
        
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>AI 对话</template>
        </el-menu-item>
        
        <el-menu-item index="/models">
          <el-icon><Box /></el-icon>
          <template #title>模型管理</template>
        </el-menu-item>
        
        <el-menu-item index="/api-keys">
          <el-icon><Key /></el-icon>
          <template #title>API 密钥</template>
        </el-menu-item>
        
        <el-menu-item index="/test">
          <el-icon><Monitor /></el-icon>
          <template #title>API 测试</template>
        </el-menu-item>
        
        <el-menu-item 
          v-if="authStore.isAdmin" 
          index="/admin"
        >
          <el-icon><Setting /></el-icon>
          <template #title>系统管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- Main Content -->
    <el-container class="main-container">
      <!-- Header -->
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-button
            text
            @click="toggleSidebar"
          >
            <el-icon size="20">
              <Fold v-if="!sidebarCollapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item to="/dashboard">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="breadcrumbItems.length > 0">
              {{ breadcrumbItems[breadcrumbItems.length - 1] }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- Theme Toggle -->
          <el-tooltip content="切换主题">
            <el-button
              text
              @click="themeStore.toggleMode"
            >
              <el-icon size="18">
                <Sunny v-if="themeStore.isDark" />
                <Moon v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          
          <!-- User Menu -->
          <el-dropdown @command="handleUserMenuCommand">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ authStore.userName }}</span>
              <el-icon class="arrow-down"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- Content -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useThemeStore } from '@/store/theme'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const sidebarCollapsed = ref(false)

const activeMenu = computed(() => {
  return route.path
})

const breadcrumbItems = computed(() => {
  const items: string[] = []
  
  if (route.meta?.title) {
    items.push(route.meta.title as string)
  }
  
  return items
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleUserMenuCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    authStore.logout()
  } catch {
    // User cancelled
  }
}

// Auto-collapse sidebar on mobile
watch(
  () => window.innerWidth,
  (width) => {
    if (width < 768) {
      sidebarCollapsed.value = true
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.sidebar {
  background: var(--bg-primary);
  border-right: 1px solid var(--border-light);
  transition: width 0.3s ease;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-light);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.main-container {
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: var(--bg-tertiary);
}

.username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.arrow-down {
  font-size: 12px;
  color: var(--text-secondary);
}

.main-content {
  background: var(--bg-secondary);
  padding: 16px;
  overflow-y: auto;
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
  .header-left .breadcrumb {
    display: none;
  }
  
  .username {
    display: none;
  }
}
</style>