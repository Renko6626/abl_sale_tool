<template>
  <n-modal 
    :show="show" 
    :mask-closable="true"
    @update:show="val => { if (!val) $emit('close') }"
  >
    <n-card :bordered="true" size="medium" style="width: 500px; max-width: 90%;">
      <template #header>
        <div class="modal-header">
          <slot name="header">默认标题</slot>
          <n-button quaternary circle size="small" @click="$emit('close')">×</n-button>
        </div>
      </template>

      <div class="modal-body">
        <slot name="body">默认内容</slot>
      </div>

      <template #footer>
        <div class="modal-footer">
          <slot name="footer">
            <n-button @click="$emit('close')">关闭</n-button>
          </slot>
        </div>
      </template>
    </n-card>
  </n-modal>
</template>

<script setup>
import { NModal, NCard, NButton } from 'naive-ui';
// 定义组件可以接收的 props 和可以触发的 events
defineProps({
  show: {
    type: Boolean,
    required: true,
  },
});
defineEmits(['close']);
</script>

<style scoped>
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.25rem;
  border-bottom: 1px solid var(--border-color);
}
.modal-body {
  padding: 1rem 0.25rem;
}
.modal-footer {
  padding: 0.75rem 0.25rem;
  border-top: 1px solid var(--border-color);
  text-align: right;
}
</style>