<template>
  <div class="loading-spinner" :class="{ 'is-fullscreen': fullscreen }">
    <div class="spinner-container">
      <div class="spinner" :style="{ width: size, height: size }">
        <div class="spinner-inner"></div>
      </div>
      <div v-if="text" class="spinner-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: string
  text?: string
  fullscreen?: boolean
}

withDefaults(defineProps<Props>(), {
  size: '24px',
  text: '',
  fullscreen: false
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.loading-spinner.is-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  position: relative;
  border-radius: 50%;
  border: 2px solid var(--border-light);
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
}

.spinner-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: var(--primary-color);
  animation: spin 2s linear infinite reverse;
}

.spinner-text {
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>