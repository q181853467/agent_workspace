<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useThemeStore } from '@/store/theme'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

const authStore = useAuthStore()
const themeStore = useThemeStore()

// Configure NProgress
NProgress.configure({ 
  showSpinner: false,
  minimum: 0.1,
  speed: 500
})

onMounted(async () => {
  // Initialize theme
  themeStore.initTheme()
  
  // Try to restore authentication state
  await authStore.initAuth()
})
</script>

<style>
/* NProgress custom styling */
#nprogress .bar {
  background: var(--primary-color) !important;
  height: 3px !important;
}

#nprogress .peg {
  box-shadow: 0 0 10px var(--primary-color), 0 0 5px var(--primary-color) !important;
}

.app-container {
  min-height: 100vh;
  background-color: var(--bg-secondary);
}
</style>