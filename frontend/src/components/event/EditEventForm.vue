<template>
  <!-- 这个组件没有自己的容器，因为它将被嵌入到模态框中 -->
  <n-form @submit.prevent>
    <div class="form-group">
      <label for="edit-name">展会名称:</label>
      <n-input id="edit-name" v-model:value="editableEvent.name" />
    </div>
    <div class="form-group">
      <label for="edit-date">日期:</label>
      <n-date-picker id="edit-date" v-model:value="editableEvent.date" type="date" value-format="yyyy-MM-dd" />
    </div>
    <div class="form-group">
      <label for="edit-location">地点:</label>
      <n-input id="edit-location" v-model:value="editableEvent.location" />
    </div>
    <div class="form-group">
      <label for="edit-vendor_password">摊主密码 (可选):</label>
      <n-input id="edit-vendor_password" v-model:value="editableEvent.vendor_password" placeholder="留空则清除密码" />
    </div>
    <ImageUploader
      label="展会收款码"
      :initial-image-url="editableEvent.qrcode_url"
      v-model="newQrCodeFile"
      @image-removed="handleImageRemoval"
    />
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <!-- 提交按钮仍由父组件模态框 footer 提供 -->
  </n-form>
</template>

<script setup>
import { ref, watch } from 'vue';
import ImageUploader from '@/components/shared/ImageUploader.vue'; 
import { NForm, NInput, NDatePicker } from 'naive-ui';
const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
});

const errorMessage = ref('');
// 创建一个可编辑的副本，避免直接修改 props
const editableEvent = ref({});

// 【简化】现在只需要这两个状态来构建 FormData
const newQrCodeFile = ref(null); // v-model 会自动更新这个
const imageRemoved = ref(false); // 专门的事件会更新这个

// 使用 watch 监听 props.event 的变化
// 当父组件传入新的 event 对象时（例如用户点击了另一个展会的编辑按钮），
// 更新我们的可编辑副本
watch(() => props.event, (newEvent) => {
  if (newEvent) {
    editableEvent.value = { ...newEvent, vendor_password: newEvent.vendor_password || '' };
    // 避免将空字符串传入 NDatePicker
    if (!editableEvent.value.date) {
      editableEvent.value.date = null;
    }
    // 重置提交状态
    newQrCodeFile.value = null;
    imageRemoved.value = false;
  }
}, { immediate: true });

// 【新增】处理来自 ImageUploader 的移除事件
function handleImageRemoval() {
  imageRemoved.value = true;
}

// 定义一个暴露给父组件的方法，用于触发提交
function submit() {
  if (!editableEvent.value.name || !editableEvent.value.date) {
    errorMessage.value = "展会名称和日期不能为空。";
    return null;
  }
  errorMessage.value = '';

  const formData = new FormData();
  
  formData.append('id', editableEvent.value.id);
  formData.append('name', editableEvent.value.name);
  formData.append('date', editableEvent.value.date);
  formData.append('location', editableEvent.value.location);
  formData.append('vendor_password', editableEvent.value.vendor_password);

  if (newQrCodeFile.value) {
    formData.append('payment_qr_code', newQrCodeFile.value);
  } 
  else if (imageRemoved.value) {
    formData.append('remove_payment_qr_code', 'true');
  }

  return formData;
}

defineExpose({
  submit,
});
</script>

<style scoped>
/* 样式与 CreateEventForm 类似 */
.form-group { margin-bottom: 1rem; }
label { display: block; margin-bottom: 0.5rem; }
input {
  width: 100%;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
  padding: 10px;
  border-radius: 4px;
  box-sizing: border-box;
}
.error-message { color: var(--error-color); }
</style>