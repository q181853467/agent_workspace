import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

type ThemeMode = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  // State
  const mode = ref<ThemeMode>('auto')
  const systemDark = ref(false)
  
  // Getters
  const isDark = computed(() => {
    return mode.value === 'dark' || (mode.value === 'auto' && systemDark.value)
  })
  
  const currentTheme = computed(() => {
    return isDark.value ? 'dark' : 'light'
  })
  
  // Actions
  const setMode = (newMode: ThemeMode) => {
    mode.value = newMode
    localStorage.setItem('theme_mode', newMode)
    applyTheme()
  }
  
  const toggleMode = () => {
    const modes: ThemeMode[] = ['light', 'dark', 'auto']
    const currentIndex = modes.indexOf(mode.value)
    const nextIndex = (currentIndex + 1) % modes.length
    setMode(modes[nextIndex])
  }
  
  const applyTheme = () => {
    const root = document.documentElement
    const theme = currentTheme.value
    
    root.setAttribute('data-theme', theme)
    
    // Update Element Plus theme
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }
  
  const initTheme = () => {
    // Get saved theme mode
    const savedMode = localStorage.getItem('theme_mode') as ThemeMode
    if (savedMode && ['light', 'dark', 'auto'].includes(savedMode)) {
      mode.value = savedMode
    }
    
    // Detect system theme
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    systemDark.value = mediaQuery.matches
    
    // Listen for system theme changes
    mediaQuery.addEventListener('change', (e) => {
      systemDark.value = e.matches
      if (mode.value === 'auto') {
        applyTheme()
      }
    })
    
    // Apply initial theme
    applyTheme()
  }
  
  return {
    // State
    mode: readonly(mode),
    systemDark: readonly(systemDark),
    
    // Getters
    isDark,
    currentTheme,
    
    // Actions
    setMode,
    toggleMode,
    initTheme
  }
})