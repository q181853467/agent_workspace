<template>
  <div class="empty-state">
    <div class="empty-content">
      <div class="empty-icon">
        <el-icon :size="iconSize" :color="iconColor">
          <component :is="iconComponent" />
        </el-icon>
      </div>
      
      <div class="empty-text">
        <h3 v-if="title">{{ title }}</h3>
        <p v-if="description">{{ description }}</p>
      </div>
      
      <div v-if="$slots.actions" class="empty-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  DocumentRemove,
  Box,
  User,
  ChatDotRound,
  Key,
  Warning
} from '@element-plus/icons-vue'

interface Props {
  type?: 'default' | 'nodata' | 'error' | 'network' | 'search'
  title?: string
  description?: string
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  title: '',
  description: '',
  iconSize: 64
})

const iconComponent = computed(() => {
  const iconMap = {
    default: Box,
    nodata: DocumentRemove,
    error: Warning,
    network: Warning,
    search: DocumentRemove
  }
  return iconMap[props.type] || Box
})

const iconColor = computed(() => {
  const colorMap = {
    default: '#c0c4cc',
    nodata: '#c0c4cc',
    error: '#f56c6c',
    network: '#e6a23c',
    search: '#909399'
  }
  return colorMap[props.type] || '#c0c4cc'
})
</script>

<style scoped>
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  padding: 40px 20px;
}

.empty-content {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  margin-bottom: 16px;
}

.empty-text h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-text p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.empty-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>