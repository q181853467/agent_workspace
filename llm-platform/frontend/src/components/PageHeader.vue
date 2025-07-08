<template>
  <div class="page-header">
    <div class="header-content">
      <div class="title-section">
        <h1 v-if="title">{{ title }}</h1>
        <p v-if="description">{{ description }}</p>
      </div>
      
      <div class="action-section" v-if="$slots.actions">
        <slot name="actions"></slot>
      </div>
    </div>
    
    <div v-if="$slots.extra" class="header-extra">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  title: '',
  description: ''
})
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.title-section h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.title-section p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.action-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-extra {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .title-section h1 {
    font-size: 24px;
  }
}
</style>