<template>
  <el-tag
    :type="tagType"
    :size="size"
    :effect="effect"
    :closable="closable"
    @close="$emit('close')"
  >
    <el-icon v-if="showIcon" class="tag-icon">
      <component :is="iconComponent" />
    </el-icon>
    <slot>{{ text }}</slot>
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  CircleCheckFilled,
  CircleCloseFilled,
  WarningFilled,
  InfoFilled,
  Loading
} from '@element-plus/icons-vue'

interface Props {
  status: 'success' | 'error' | 'warning' | 'info' | 'loading' | 'active' | 'inactive'
  text?: string
  size?: 'large' | 'default' | 'small'
  effect?: 'dark' | 'light' | 'plain'
  showIcon?: boolean
  closable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  size: 'small',
  effect: 'light',
  showIcon: false,
  closable: false
})

defineEmits<{
  close: []
}>()

const tagType = computed(() => {
  const typeMap = {
    success: 'success',
    error: 'danger',
    warning: 'warning',
    info: 'info',
    loading: 'info',
    active: 'success',
    inactive: 'danger'
  }
  return typeMap[props.status] || 'info'
})

const iconComponent = computed(() => {
  const iconMap = {
    success: CircleCheckFilled,
    error: CircleCloseFilled,
    warning: WarningFilled,
    info: InfoFilled,
    loading: Loading,
    active: CircleCheckFilled,
    inactive: CircleCloseFilled
  }
  return iconMap[props.status] || InfoFilled
})
</script>

<style scoped>
.tag-icon {
  margin-right: 4px;
}
</style>